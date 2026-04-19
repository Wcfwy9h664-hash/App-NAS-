import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import requests
import time

# 1. Configuration & Style
st.set_page_config(page_title="MNQ ELITE LIVE", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .timer-box { background: #161b22; border: 2px solid #007bff; padding: 15px; border-radius: 12px; text-align: center; }
    .timer-val { font-size: 28px; font-weight: bold; color: #00ff41; font-family: 'Courier New', Courier, monospace; }
    .signal-box { padding: 15px; border-radius: 12px; text-align: center; font-weight: bold; font-size: 20px; margin: 10px 0; }
    .range-container { background: #30363d; height: 12px; border-radius: 6px; margin: 10px 0; position: relative; }
    .range-bar { background: linear-gradient(90deg, #ffffff, #007bff); height: 100%; border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. LOGIQUE DE RAFRAÎCHISSEMENT AUTOMATIQUE ---
# Ceci force la page à se recharger toutes les secondes pour le timer
placeholder_timer = st.empty()

# 3. Gestion du Temps (Paris)
paris_tz = pytz.timezone('Europe/Paris')
now_paris = datetime.now(paris_tz)
# Calcul de la fin de la bougie M15 actuelle
next_m15 = (now_paris + timedelta(minutes=15)).replace(minute=(now_paris.minute // 15 + 1) * 15 % 60, second=0, microsecond=0)
if next_m15.minute == 0 and now_paris.minute >= 45: next_m15 += timedelta(hours=1)

time_diff = next_m15 - now_paris
min_left, sec_left = divmod(time_diff.seconds, 60)

# Affichage du Timer en haut qui bouge
with placeholder_timer:
    st.markdown(f'''
        <div class="timer-box">
            <span style="font-size: 14px; color: #888;">⏳ PROCHAINE BOUGIE M15 DANS</span><br>
            <span class="timer-val">{min_left:02d}:{sec_left:02d}</span>
        </div>
    ''', unsafe_allow_html=True)

st.title("MNQ 🚀 LIVE TERMINAL")

# 4. Données avec cache pour ne pas spammer Yahoo Finance
@st.cache_data(ttl=60) # Actualise les données boursières toutes les 60 secondes
def get_data():
    df = yf.download("MNQ=F", period="5d", interval="15m", progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df

try:
    df = get_data()
    if not df.empty:
        curr = float(df['Close'].iloc[-1])
        hi, lo = df['High'].iloc[-100:].max(), df['Low'].iloc[-100:].min()
        pivot = (df['High'].iloc[-1] + df['Low'].iloc[-1] + df['Close'].iloc[-1]) / 3
        ma20 = df['Close'].rolling(20).mean().iloc[-1]

        # Verdict
        if curr > pivot and curr > ma20:
            st.markdown('<div class="signal-box" style="background:#00ff41; color:#000;">🚀 DIRECTION : ACHAT</div>', unsafe_allow_html=True)
        elif curr < pivot and curr < ma20:
            st.markdown('<div class="signal-box" style="background:#ff4b4b; color:#fff;">📉 DIRECTION : VENTE</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="signal-box" style="background:#30363d; color:#fff;">⚖️ DIRECTION : NEUTRE</div>', unsafe_allow_html=True)

        # Graphique simplifié pour mobile
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#007bff', increasing_fillcolor='#007bff', decreasing_line_color='#ffffff', decreasing_fillcolor='#ffffff')])
        fig.add_hline(y=pivot, line_dash="dash", line_color="yellow")
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=350, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

        # Heatmap & Range
        prog = ((curr - lo) / (hi - lo)) * 100 if hi != lo else 50
        st.markdown(f"**Position dans le Range du Jour**")
        st.markdown(f'<div class="range-container"><div class="range-bar" style="width: {prog}%;"></div></div>', unsafe_allow_html=True)

except:
    st.info("Attente du flux de 23h00...")

# --- LOGIQUE DE BOUCLE INFINIE POUR LE TIMER ---
time.sleep(1)
st.rerun()
