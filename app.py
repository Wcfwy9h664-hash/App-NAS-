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
    .signal-box { padding: 15px; border-radius: 12px; text-align: center; font-weight: bold; font-size: 22px; margin: 10px 0; }
    .range-container { background: #30363d; height: 12px; border-radius: 6px; margin: 10px 0; position: relative; }
    .range-bar { background: linear-gradient(90deg, #ffffff, #007bff); height: 100%; border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

# 2. Gestion du Temps
paris_tz = pytz.timezone('Europe/Paris')
now_paris = datetime.now(paris_tz)
next_m15 = (now_paris + timedelta(minutes=15)).replace(minute=(now_paris.minute // 15 + 1) * 15 % 60, second=0, microsecond=0)
if next_m15.minute == 0 and now_paris.minute >= 45: next_m15 += timedelta(hours=1)
time_diff = next_m15 - now_paris
min_left, sec_left = divmod(time_diff.seconds, 60)

# 3. News Rapides
try:
    api_key = "Ff12b93f85484bb0b854389fb3f9e578"
    news = requests.get(f'https://newsapi.org/v2/everything?q=Nasdaq&language=fr&pageSize=1&apiKey={api_key}').json()
    if news.get('articles'):
        st.markdown(f"📢 **FLASH:** {news['articles'][0]['title']}")
except: pass

# 4. Données & Calculs
try:
    df = yf.download("MNQ=F", period="2d", interval="15m", progress=False)
    if not df.empty:
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        curr = float(df['Close'].iloc[-1])
        hi, lo = df['High'].max(), df['Low'].min()
        
        # Calcul Pivot Point (Standard)
        prev_day = yf.download("MNQ=F", period="2d", interval="1d", progress=False)
        if isinstance(prev_day.columns, pd.MultiIndex): prev_day.columns = prev_day.columns.get_level_values(0)
        p_hi, p_lo, p_cl = prev_day['High'].iloc[-2], prev_day['Low'].iloc[-2], prev_day['Close'].iloc[-2]
        pivot = (p_hi + p_lo + p_cl) / 3

        # Header Metrics
        c1, c2 = st.columns([2, 1])
        with c1:
            st.title(f"MNQ: {curr:,.2f} $")
        with c2:
            st.markdown(f'<div class="timer-box">⌛ CLÔTURE M15<br><span style="font-size:20px; color:#007bff;">{min_left:02d}:{sec_left:02d}</span></div>', unsafe_allow_html=True)

        # Signal de Direction
        if curr > pivot and curr > df['Close'].rolling(20).mean().iloc[-1]:
            st.markdown('<div class="signal-box" style="background:#00ff41; color:#000;">🚀 TENDANCE HAUSSIÈRE (Piv+MA)</div>', unsafe_allow_html=True)
        elif curr < pivot and curr < df['Close'].rolling(20).mean().iloc[-1]:
            st.markdown('<div class="signal-box" style="background:#ff4b4b; color:#fff;">📉 TENDANCE BAISSIÈRE (Piv+MA)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="signal-box" style="background:#30363d; color:#fff;">⚖️ ZONE D\'INDÉCISION</div>', unsafe_allow_html=True)

        # Graphique
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#007bff', increasing_fillcolor='#007bff', decreasing_line_color='#ffffff', decreasing_fillcolor='#ffffff')])
        
        # Ajout Ligne Pivot
        fig.add_hline(y=pivot, line_dash="dash", line_color="yellow", annotation_text="PIVOT")
        
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

        # Heatmap Volume (Couleur selon intensité)
        v_curr = df['Volume'].iloc[-1]
        v_avg = df['Volume'].tail(10).mean()
        v_color = "#30363d" # Gris
        if v_curr > v_avg * 1.5: v_color = "#ffcc00" # Jaune
        if v_curr > v_avg * 2.5: v_color = "#ff4b4b" # Rouge (EXPLOSION)
        
        st.markdown(f"**Intensité des échanges (Volume)**")
        st.markdown(f'<div style="background:{v_color}; height:15px; border-radius:5px; width:100%;"></div>', unsafe_allow_html=True)

        # Daily Range
        prog = ((curr - lo) / (hi - lo)) * 100
        st.markdown(f"**Position Journée** ({lo:,.0f} - {hi:,.0f})")
        st.markdown(f'<div class="range-container"><div class="range-bar" style="width: {prog}%;"></div></div>', unsafe_allow_html=True)

except: st.error("Connexion flux...")

if st.button('🔄 ACTUALISER'): st.rerun()
