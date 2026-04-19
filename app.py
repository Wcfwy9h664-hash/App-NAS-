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
    .status-closed { color: #ff4b4b; font-weight: bold; font-size: 35px; }
    .status-open { color: #00ff41; font-weight: bold; font-size: 35px; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 15px; }
    .news-box { background-color: #1a1f26; padding: 15px; border-left: 5px solid #007bff; border-radius: 5px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("MNQ 🚀 📢")

# 2. Logique Marché
paris_tz = pytz.timezone('Europe/Paris')
now_paris = datetime.now(paris_tz)
is_weekend = now_paris.weekday() == 5 or (now_paris.weekday() == 6 and now_paris.hour < 23)

# 3. Données & Signaux
try:
    ticker_symbol = "MNQ=F"
    data = yf.download(ticker_symbol, period="5d", interval="15m", progress=False)

    if data is not None and not data.empty:
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        data['RSI'] = 100 - (100 / (1 + (gain / loss)))
        data['MA20'] = data['Close'].rolling(window=20).mean()

        current_price = float(data['Close'].iloc[-1])
        change = current_price - float(data['Close'].iloc[-2])
        rsi_now = data['RSI'].iloc[-1]
        ma_now = data['MA20'].iloc[-1]

        signal_color = "⚪"
        signal_text = "AUCUN SIGNAL"
        if current_price > ma_now and rsi_now < 60:
            signal_color = "🟢"
            signal_text = "CONFIRMATION ACHAT"
        elif current_price < ma_now and rsi_now > 40:
            signal_color = "🔴"
            signal_text = "CONFIRMATION VENTE"

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="MICRO NASDAQ", value=f"{current_price:,.2f} $", delta=f"{change:,.2f} $")
        with col2:
            if is_weekend:
                st.markdown(f"<p class='status-closed'>FERMÉ</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p class='status-open'>OUVERT</p>", unsafe_allow_html=True)
        with col3:
            st.metric(label="SIGNAL INDICATEURS", value=signal_text, delta=signal_color)

        fig = go.Figure(data=[go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
            increasing_line_color='#007bff', increasing_fillcolor='#007bff',
            decreasing_line_color='#ffffff', decreasing_fillcolor='#ffffff'
        )])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=450, margin=dict(l=5, r=5, t=5, b=5))
        st.plotly_chart(fig, use_container_width=True)
except:
    st.error("Flux en pause...")

# 4. SECTION ANNONCES ÉCO
st.divider()
st.subheader("⚠️ Flash Économique")
try:
    api_key = "Ff12b93f85484bb0b854389fb3f9e578"
    news_url = f'https://newsapi.org/v2/everything?q=Nasdaq+FED+Inflation&language=fr&sortBy=publishedAt&pageSize=3&apiKey={api_key}'
    response = requests.get(news_url).json()
    if response.get('articles'):
        for art in response['articles']:
            st.markdown(f'<div class="news-box"><strong>{art["title"]}</strong><br><small>{art["source"]["name"]}</small></div>', unsafe_allow_html=True)
except:
    st.write("News indisponibles.")

# 5. SIDEBAR AVEC TA PHOTO
st.sidebar.header("⚙️ Paramètres")

# URL de TA photo (reçue de ton image précédente)
photo_url = "https://replicate.delivery/xpbkg/O5xH9XzMvQ6eGF5Y8WwF8E2H3V9wL0Z4Z6K4V9wL0Z4Z6K4V9/output.png"

# On affiche ta photo, arrondie pour le style
st.sidebar.image(photo_url, caption="Fondette Mode Zen", use_container_width=True)

st.sidebar.divider()
if 'rsi_now' in locals():
    st.sidebar.write(f"RSI Actuel : **{rsi_now:.1f}**")
if st.button('🔄 ACTUALISER TOUT'):
    st.rerun()
