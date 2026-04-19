import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import requests
import time

# 1. Config & Style
st.set_page_config(page_title="MNQ ULTIME LIVE", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .timer-box { background: #161b22; border: 2px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px; }
    .timer-val { font-size: 24px; font-weight: bold; color: #00ff41; font-family: monospace; }
    .signal-box { padding: 20px; border-radius: 15px; text-align: center; font-weight: bold; font-size: 22px; margin: 10px 0; border: 1px solid #ffffff; }
    .metric-card { background: #1a1f26; border: 1px solid #30363d; padding: 10px; border-radius: 10px; text-align: center; }
    .news-box { background-color: #1a1f26; padding: 8px; border-left: 4px solid #ffcc00; border-radius: 5px; margin-bottom: 5px; font-size: 0.85em; }
    </style>
""", unsafe_allow_html=True)

# --- 2. MOTEUR DE TEMPS (PARIS) ---
paris_tz = pytz.timezone('Europe/Paris')
now_paris = datetime.now(paris_tz)
next_m15 = (now_paris + timedelta(minutes=15)).replace(minute=(now_paris.minute // 15 + 1) * 15 % 60, second=0, microsecond=0)
if next_m15.minute == 0 and now_paris.minute >= 45: next_m15 += timedelta(hours=1)
time_diff = next_m15 - now_paris
min_left, sec_left = divmod(time_diff.seconds, 60)

# Affichage du Chrono en haut
st.markdown(f'''
    <div class="timer-box">
        <small style="color: #888;">PROCHAINE BOUGIE M15 DANS</small><br>
        <span class="timer-val">{min_left:02d}:{sec_left:02d}</span>
    </div>
''', unsafe_allow_html=True)

# --- 3. ANALYSE DES NEWS & SENTIMENT ---
sentiment_score = 0
try:
    api_key = "Ff12b93f85484bb0b854389fb3f9e578"
    news_res = requests.get(f'https://newsapi.org/v2/everything?q=Nasdaq+FED&language=fr&sortBy=publishedAt&pageSize=1&apiKey={api_key}').json()
    if news_res.get('articles'):
        art = news_res['articles'][0]
        st.markdown(f'<div class="news-box"><strong>INFO :</strong> {art["title"][:80]}...</div>', unsafe_allow_html=True)
        title = art["title"].lower()
        if any(w in title for w in ['hausse', 'positif', 'croissance', 'rebond']): sentiment_score = 1
        if any(w in title for w in ['chute', 'baisse', 'inflation', 'taux']): sentiment_score = -1
except: pass

# --- 4. DATA & INDICATEURS ---
@st.cache_data(ttl=60)
def get_live_data():
    df = yf.download("MNQ=F", period="5d", interval="15m", progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    # MA20
    df['MA20'] = df['Close'].rolling(window=20).mean()
    return df

try:
    data = get_live_data()
    curr = float(data['Close'].iloc[-1])
    rsi_now = data['RSI'].iloc[-1]
    ma_now = data['MA20'].iloc[-1]
    pivot = (data['High'].iloc[-1] + data['Low'].iloc[-1] + data['Close'].iloc[-1]) / 3

    # --- 5. SYNCHRONISATION DU SIGNAL ---
    tech_score = 0
    if curr > ma_now: tech_score += 1
    else: tech_score -= 1
    if rsi_now < 45: tech_score += 0.5 # Faveur achat
    if rsi_now > 55: tech_score -= 0.5 # Faveur vente
    
    final_decision = tech_score + (sentiment_score * 0.5)

    if final_decision > 0.5:
        st.markdown('<div class="signal-box" style="background:#00ff41; color:#000;">🚀 DIRECTION : ACHAT (BULLISH)</div>', unsafe_allow_html=True)
    elif final_decision < -0.5:
        st.markdown('<div class="signal-box" style="background:#ff4b4b; color:#fff;">📉 DIRECTION : VENTE (BEARISH)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="signal-box" style="background:#30363d; color:#fff;">⚖️ DIRECTION : NEUTRE / ATTENTE</div>', unsafe_allow_html=True)

    # --- 6. METRICS & CONFIANCE ---
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("PRIX MNQ", f"{curr:,.2f}$")
    with c2:
        conf_label = "FORTE" if abs(final_decision) >= 1.5 else "MODÉRÉE"
        st.metric("CONFIANCE", conf_label)
    with c3:
        st.metric("RSI (14)", f"{rsi_now:.1f}")

    # --- 7. GRAPHIQUE ---
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
        increasing_line_color='#007bff', increasing_fillcolor='#007bff', decreasing_line_color='#ffffff', decreasing_fillcolor='#ffffff')])
    fig.add_hline(y=ma_now, line_color="gray", line_dash="dot", annotation_text="MA20")
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.caption(f"Dernière MAJ Flux : {now_paris.strftime('%H:%M:%S')} | MA20 : {ma_now:,.1f}")

except:
    st.info("Récupération du flux en cours...")

# --- 8. BOUCLE TEMPS RÉEL ---
time.sleep(1)
st.rerun()
