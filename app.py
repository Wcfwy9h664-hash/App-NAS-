import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import requests

# 1. Configuration & Style
st.set_page_config(page_title="MNQ ELITE", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .timer-box { background: #161b22; border: 1px solid #007bff; padding: 10px; border-radius: 10px; text-align: center; }
    .signal-box { padding: 15px; border-radius: 12px; text-align: center; font-weight: bold; font-size: 20px; margin: 10px 0; }
    .range-container { background: #30363d; height: 12px; border-radius: 6px; margin: 10px 0; position: relative; }
    .range-bar { background: linear-gradient(90deg, #ffffff, #007bff); height: 100%; border-radius: 6px; }
    .news-box { background-color: #1a1f26; padding: 8px; border-left: 4px solid #007bff; border-radius: 5px; margin-bottom: 5px; font-size: 0.85em; }
    </style>
""", unsafe_allow_html=True)

# 2. Gestion du Temps
paris_tz = pytz.timezone('Europe/Paris')
now_paris = datetime.now(paris_tz)
next_m15 = (now_paris + timedelta(minutes=15)).replace(minute=(now_paris.minute // 15 + 1) * 15 % 60, second=0, microsecond=0)
if next_m15.minute == 0 and now_paris.minute >= 45: next_m15 += timedelta(hours=1)
time_diff = next_m15 - now_paris
min_left, sec_left = divmod(time_diff.seconds, 60)

# 3. News Flash Rapide
try:
    api_key = "Ff12b93f85484bb0b854389fb3f9e578"
    news_res = requests.get(f'https://newsapi.org/v2/everything?q=Nasdaq&language=fr&pageSize=1&apiKey={api_key}').json()
    if news_res.get('articles'):
        st.markdown(f"📢 **FLASH:** {news_res['articles'][0]['title']}")
except: pass

st.title("MNQ 🚀 STRATÉGIQUE")

# 4. Récupération des données avec sécurité
try:
    # On prend une période plus large (5j) pour être sûr d'avoir de la data même le dimanche
    df = yf.download("MNQ=F", period="5d", interval="15m", progress=False)
    
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        curr = float(df['Close'].iloc[-1])
        hi, lo = df['High'].iloc[-100:].max(), df['Low'].iloc[-100:].min() # Range sur les 100 dernières bougies
        
        # Calcul Pivot simplifié (sur les dernières bougies si le daily manque)
        pivot = (df['High'].iloc[-1] + df['Low'].iloc[-1] + df['Close'].iloc[-1]) / 3

        # Header
        c1, c2 = st.columns([2, 1])
        with c1:
            st.metric("PRIX MNQ", f"{curr:,.2f} $")
        with c2:
            st.markdown(f'<div class="timer-box">⌛ CLÔTURE M15<br><span style="font-size:18px; color:#007bff;">{min_left:02d}:{sec_left:02d}</span></div>', unsafe_allow_html=True)

        # Signal
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        if curr > pivot and curr > ma20:
            st.markdown('<div class="signal-box" style="background:#00ff41; color:#000;">🚀 DIRECTION : ACHAT</div>', unsafe_allow_html=True)
        elif curr < pivot and curr < ma20:
            st.markdown('<div class="signal-box" style="background:#ff4b4b; color:#fff;">📉 DIRECTION : VENTE</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="signal-box" style="background:#30363d; color:#fff;">⚖️ DIRECTION : NEUTRE</div>', unsafe_allow_html=True)

        # Graphique
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#007bff', increasing_fillcolor='#007bff', decreasing_line_color='#ffffff', decreasing_fillcolor='#ffffff')])
        fig.add_hline(y=pivot, line_dash="dash", line_color="yellow")
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=400, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

        # Heatmap Volume
        v_curr, v_avg = df['Volume'].iloc[-1], df['Volume'].tail(10).mean()
        v_color = "#30363d"
        if v_curr > v_avg * 1.5: v_color = "#ffcc00"
        if v_curr > v_avg * 2.5: v_color = "#ff4b4b"
        st.markdown(f"**Intensité Volume**")
        st.markdown(f'<div style="background:{v_color}; height:12px; border-radius:6px; width:100%;"></div>', unsafe_allow_html=True)

        # Daily Range
        prog = ((curr - lo) / (hi - lo)) * 100 if hi != lo else 50
        st.markdown(f"**Position Range**")
        st.markdown(f'<div class="range-container"><div class="range-bar" style="width: {prog}%;"></div></div>', unsafe_allow_html=True)

    else:
        st.warning("En attente de l'ouverture du flux (23h00)...")

except Exception as e:
    st.info("Flux en pause. Réouverture à 23h.")

if st.button('🔄 ACTUALISER'): st.rerun()
