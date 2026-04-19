import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import requests
import time

# 1. Configuration & Style
st.set_page_config(page_title="MNQ PRO TERMINAL", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .timer-box { background: #161b22; border: 2px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px; }
    .timer-val { font-size: 24px; font-weight: bold; color: #00ff41; font-family: monospace; }
    .signal-container { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 15px; }
    .signal-value { font-size: 28px; font-weight: bold; }
    .cal-box { background: #1a1f26; padding: 10px; border-radius: 8px; border: 1px solid #30363d; margin-top: 10px; font-size: 0.85em; }
    .impact-high { color: #ff4b4b; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. GESTION DU TEMPS ---
paris_tz = pytz.timezone('Europe/Paris')
now_paris = datetime.now(paris_tz)
next_m15 = (now_paris + timedelta(minutes=15)).replace(minute=(now_paris.minute // 15 + 1) * 15 % 60, second=0, microsecond=0)
if next_m15.minute == 0 and now_paris.minute >= 45: next_m15 += timedelta(hours=1)
time_diff = next_m15 - now_paris
min_left, sec_left = divmod(time_diff.seconds, 60)

st.markdown(f'''
    <div class="timer-box">
        <small style="color: #888;">PROCHAINE BOUGIE M15 DANS</small><br>
        <span class="timer-val">{min_left:02d}:{sec_left:02d}</span>
    </div>
''', unsafe_allow_html=True)

# --- 3. CALENDRIER ÉCONOMIQUE SIMPLIFIÉ ---
# On utilise une liste manuelle des gros RDV de la semaine ou une API news filtrée
st.markdown("📅 **PROCHAINS RENDEZ-VOUS (USA)**")
col_cal1, col_cal2 = st.columns(2)
# Exemple de données (Idéalement à coupler avec une API de calendrier plus tard)
events = [
    {"heure": "14:30", "nom": "Empire State Manufacturing", "impact": "🟡"},
    {"heure": "16:00", "nom": "Discours Membre FED", "impact": "🔥"},
]

with col_cal1:
    for ev in events:
        st.markdown(f'''<div class="cal-box">🕒 {ev['heure']} - {ev['nom']} {ev['impact']}</div>''', unsafe_allow_html=True)

# --- 4. DONNÉES & INDICATEURS ---
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
    
    # --- 5. LOGIQUE SIGNAL & RÉACTION ANNONCE ---
    # On regarde si la bougie actuelle est très volatile (signe d'annonce)
    volatility = (data['High'].iloc[-1] - data['Low'].iloc[-1])
    avg_vol = (data['High'] - data['Low']).tail(10).mean()
    
    reaction_msg = ""
    if volatility > (avg_vol * 2):
        reaction_msg = "⚡ RÉACTION VOLATILE DÉTECTÉE"

    tech_score = 1 if curr > ma_now else -1
    
    status_text, status_color, icon = "AUCUN SIGNAL", "#ffffff", "⚪"
    if rsi_now > 70: status_text, status_color, icon = "DANGER : SUR-ACHAT", "#ff8c00", "⚠️"
    elif rsi_now < 30: status_text, status_color, icon = "DANGER : SUR-VENTE", "#ff8c00", "⚠️"
    elif tech_score == 1: status_text, status_color, icon = "ACHAT CONFIRMÉ", "#00ff41", "🟢"
    elif tech_score == -1: status_text, status_color, icon = "VENTE CONFIRMÉE", "#ff4b4b", "🔴"

    st.markdown(f'''
        <div class="signal-container">
            <div style="font-size: 13px; color: #8b949e;">SIGNAL INDICATEURS</div>
            <div class="signal-value" style="color: {status_color};">{status_text}</div>
            <div style="font-size: 20px; margin-top: 5px;">{icon}</div>
            <div style="font-size: 12px; color: #ffcc00; margin-top:5px;">{reaction_msg}</div>
        </div>
    ''', unsafe_allow_html=True)

    # Metrics
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("PRIX", f"{curr:,.2f}$")
    with c2: st.metric("VOLATILITÉ", f"{volatility:,.1f}")
    with c3: st.metric("RSI", f"{rsi_now:.1f}")

    # Graphique
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
        increasing_line_color='#007bff', increasing_fillcolor='#007bff', decreasing_line_color='#ffffff', decreasing_fillcolor='#ffffff')])
    fig.add_hline(y=ma_now, line_color="gray", line_dash="dot")
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=350, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

except:
    st.info("Ouverture du flux à 23h00...")

# --- 6. AUTO-REFRESH ---
time.sleep(1)
st.rerun()
