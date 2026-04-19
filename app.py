import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz
import requests

# 1. Config de la page
st.set_page_config(page_title="MNQ 🚀", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stMetricValue"] { font-size: 35px !important; }
    .status-closed { color: #ff4b4b; font-weight: bold; font-size: 25px; }
    .status-open { color: #00ff41; font-weight: bold; font-size: 25px; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    .news-box { background-color: #1a1f26; padding: 10px; border-left: 5px solid #007bff; border-radius: 5px; margin-bottom: 5px; font-size: 0.9em; }
    .signal-box { padding: 20px; border-radius: 15px; text-align: center; font-weight: bold; font-size: 24px; margin: 10px 0; border: 2px solid #ffffff; }
    </style>
""", unsafe_allow_html=True)

st.title("MNQ 🚀 TERMINAL STRATÉGIQUE")

# --- 2. RÉCUPÉRATION ET ANALYSE DES NEWS ---
sentiment_score = 0
news_titles = []
try:
    api_key = "Ff12b93f85484bb0b854389fb3f9e578"
    news_url = f'https://newsapi.org/v2/everything?q=Nasdaq+FED+Economy&language=fr&sortBy=publishedAt&pageSize=3&apiKey={api_key}'
    response = requests.get(news_url).json()
    
    bull_words = ['hausse', 'croissance', 'positif', 'gain', 'rebond', 'achat', 'confiance', 'nvidia']
    bear_words = ['chute', 'baisse', 'inflation', 'taux', 'fed', 'crainte', 'négatif', 'risque', 'correction']

    if response.get('articles'):
        st.subheader("📢 DERNIÈRES ALERTES")
        cols = st.columns(len(response['articles']))
        for i, art in enumerate(response['articles']):
            title = art["title"].lower()
            news_titles.append(title)
            # Analyse simple de sentiment
            for word in bull_words:
                if word in title: sentiment_score += 1
            for word in bear_words:
                if word in title: sentiment_score -= 1
            
            with cols[i]:
                st.markdown(f'<div class="news-box"><strong>{art["title"][:70]}...</strong><br><small>{art["source"]["name"]}</small></div>', unsafe_allow_html=True)
except:
    st.info("Attente des dernières news...")

st.divider()

# 3. Logique Marché & Données
paris_tz = pytz.timezone('Europe/Paris')
now_paris = datetime.now(paris_tz)
is_weekend = now_paris.weekday() == 5 or (now_paris.weekday() == 6 and now_paris.hour < 23)

try:
    ticker_symbol = "MNQ=F"
    data = yf.download(ticker_symbol, period="3d", interval="15m", progress=False)

    if not data.empty:
        if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
        
        # Technique
        data['MA20'] = data['Close'].rolling(window=20).mean()
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        current_price = float(data['Close'].iloc[-1])
        rsi_now = rsi.iloc[-1]
        ma_now = data['MA20'].iloc[-1]

        # --- 4. LE SUPER SIGNAL (NEWS + TECHNIQUE) ---
        technical_score = 0
        if current_price > ma_now: technical_score += 1
        else: technical_score -= 1
        if rsi_now < 40: technical_score += 1 # Survente = opportunité achat
        if rsi_now > 60: technical_score -= 1 # Surachat = risque vente

        final_score = technical_score + (sentiment_score * 0.5)

        # Affichage du verdict
        if final_score > 0.5:
            st.markdown('<div class="signal-box" style="background-color: #00ff41; color: #000000;">🚀 DIRECTION : ACHAT (BULLISH)</div>', unsafe_allow_html=True)
        elif final_score < -0.5:
            st.markdown('<div class="signal-box" style="background-color: #ff4b4b; color: #ffffff;">📉 DIRECTION : VENTE (BEARISH)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="signal-box" style="background-color: #555555; color: #ffffff;">⚖️ DIRECTION : NEUTRE / ATTENTE</div>', unsafe_allow_html=True)

        # 5. Dashboard Metrics
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("PRIX MNQ", f"{current_price:,.2f} $")
        with c2:
            st.markdown(f"<p class='status-{'closed' if is_weekend else 'open'}'>{'MARCHÉ FERMÉ' if is_weekend else 'MARCHÉ OUVERT'}</p>", unsafe_allow_html=True)
        with c3:
            confiance = "FORTE" if abs(final_score) > 1.5 else "MODÉRÉE"
            st.metric("CONFIANCE DU SIGNAL", confiance)

        # 6. Graphique
        fig = go.Figure(data=[go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
            increasing_line_color='#007bff', increasing_fillcolor='#007bff',
            decreasing_line_color='#ffffff', decreasing_fillcolor='#ffffff'
        )])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

except:
    st.error("Flux de données indisponible.")

# Sidebar
st.sidebar.header("📊 INFOS TECHNIQUES")
st.sidebar.write(f"RSI : {rsi_now:.1f}")
st.sidebar.write(f"Sentiment News : {sentiment_score}")
if st.button('🔄 ACTUALISER'):
    st.rerun()
