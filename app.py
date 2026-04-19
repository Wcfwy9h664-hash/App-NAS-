import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import requests
import time

# 1. Configuration & Style
st.set_page_config(page_title="MNQ ULTIME 23H", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .timer-box { background: #161b22; border: 2px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px; }
    .timer-val { font-size: 24px; font-weight: bold; color: #00ff41; font-family: monospace; }
    .signal-container { padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 15px; }
    .signal-title { font-size: 14px; text-transform: uppercase; margin-bottom: 5px; font-weight: bold; }
    .signal-value { font-size: 34px; font-weight: bold; }
    .news-box { background-color: #1a1f26; padding: 10px; border-left: 4px solid #ffcc00; border-radius: 5px; margin-bottom: 10px; font-size: 0.9em; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CHRONO TEMPS RÉEL ---
paris_tz = pytz.timezone('Europe/Paris')
now_paris = datetime.now(paris_tz)
next_m15 = (now_paris + timedelta(minutes=15)).replace(minute=(now_paris.minute // 15 + 1) * 15 % 60, second=0, microsecond=0)
if next_m15.minute == 0 and now_paris.minute >= 45: next_m15 += timedelta(hours=1)
time_diff = next_m15 - now_paris
min_left, sec_left = divmod(time_diff.seconds, 60)

st.markdown(f'''
    <div class="timer-box">
        <small style="color: #888;">FIN DE BOUGIE DANS</small><br>
        <span class="timer-val">{min_left:02d}:{sec_left:02d}</span>
    </div>
''', unsafe_allow_html=True)

# --- 3. NEWS ---
sentiment_score = 0
try:
    api_key = "Ff12b93f85484bb0b854389fb3f9e578"
    news_res = requests.get(f'https://newsapi.org/v2/everything?q=Nasdaq+FED&language=fr&sortBy=publishedAt&pageSize=1&apiKey={api_key}').json()
    if news_res.get('articles'):
        art = news_res['articles'][0]
        st.markdown(f'<div class="news-box">🔥 {art["title"][:85]}...</div>', unsafe_allow_html=True)
        title = art["title"].lower()
        if any(w in title for w in ['hausse', 'positif', 'rebond']): sentiment_score = 1
        if any(w in title for w in ['chute', 'baisse', 'inflation']): sentiment_score = -1
except: pass

# --- 4. DONNÉES ---
@st.cache_data(ttl=60)
def get_data():
    df = yf.download("MNQ=F", period="5d", interval="15m", progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    df['MA20'] = df['Close'].rolling(window=20).mean()
    return df

try:
    data = get_data()
    curr = float(data['Close'].iloc[-1])
    rsi_now = data['RSI'].iloc[-1]
    ma_now = data['MA20'].iloc[-1]
    
    # --- 5. LOGIQUE DE SIGNAL & ZONE DE DANGER ---
    tech_score = 0
    if curr > ma_now: tech_score += 1
    else: tech_score -= 1
    
    final_score = tech_score + (sentiment_score * 0.5)
    
    # Init variables de style
    bg_color, text_val, icon, text_color = "#30363d", "AUCUN SIGNAL", "⚪", "#ffffff"

    # Vérification RSI (Zone de Danger)
    if rsi_now > 70:
        bg_color, text_val, icon = "#ff8c00", "DANGER : SUR-ACHAT", "⚠️"
        text_color = "#000000"
    elif rsi_now < 30:
        bg_color, text_val, icon = "#ff8c00", "DANGER : SUR-VENTE", "⚠️"
        text_color = "#000000"
    # Sinon Signal Classique
    elif final_score > 0.5:
        bg_color, text_val, icon, text_color = "#00ff41", "ACHAT CONFIRMÉ", "🟢", "#000000"
    elif final_score < -0.5:
        bg_color, text_val, icon, text_color = "#ff4b4b", "VENTE CONFIRMÉE", "🔴", "#ffffff"

    st.markdown(f'''
        <div class="signal-container" style="background-color: {bg_color}; color: {text_color};">
            <div class="signal-title" style="opacity: 0.8;">SIGNAL INDICATEURS</div>
            <div class="signal-value">{text_val}</div>
            <div style="font-size: 24px; margin-top: 5px;">{icon}</div>
        </div>
    ''', unsafe_allow_html=True)

    # Metrics
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("PRIX", f"{curr:,.2f}$")
    with c2: st.metric("CONFIANCE", "FORTE" if abs(final_score) >= 1.5 else "MODÉRÉE")
    with c3:
        # Couleur RSI dynamique
        rsi_col = "white"
        if rsi_now > 70 or rsi_now < 30: rsi_col = "#ff8c00"
        st.markdown(f"RSI: <span style='color:{rsi_col}; font-size:20px; font-weight:bold;'>{rsi_now:.1f}</span>", unsafe_allow_html=True)

    # Graphique
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
        increasing_line_color='#007bff', increasing_fillcolor='#007bff', decreasing_line_color='#ffffff', decreasing_fillcolor='#ffffff')])
    fig.add_hline(y=ma_now, line_color="gray", line_dash="dot")
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

except:
    st.info("Flux en attente d'ouverture...")

# --- 6. AUTO-REFRESH ---
time.sleep(1)
st.rerun()
