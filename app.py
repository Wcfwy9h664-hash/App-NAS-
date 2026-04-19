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
    .status-closed { color: #ff4b4b; font-weight: bold; font-size: 30px; }
    .status-open { color: #00ff41; font-weight: bold; font-size: 30px; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 15px; }
    .news-box { background-color: #1a1f26; padding: 10px; border-left: 5px solid #ffcc00; border-radius: 5px; margin-bottom: 5px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

st.title("MNQ 🚀 📢")

# --- 2. SECTION ANNONCES (TOUT EN HAUT) ---
st.subheader("📢 DERNIÈRES ALERTES MARCHÉ")
try:
    api_key = "Ff12b93f85484bb0b854389fb3f9e578"
    news_url = f'https://newsapi.org/v2/everything?q=Nasdaq+FED+Inflation&language=fr&sortBy=publishedAt&pageSize=2&apiKey={api_key}'
    response = requests.get(news_url).json()
    if response.get('articles'):
        cols_news = st.columns(len(response['articles']))
        for i, art in enumerate(response['articles']):
            with cols_news[i]:
                st.markdown(f'<div class="news-box"><small style="color:#ffcc00;">URGENT</small><br><strong>{art["title"][:80]}...</strong><br><small>{art["source"]["name"]}</small></div>', unsafe_allow_html=True)
    else:
        st.info("Aucune alerte majeure pour le moment.")
except:
    st.write("Flux news en attente...")

st.divider()

# 3. Logique Marché & Données
paris_tz = pytz.timezone('Europe/Paris')
now_paris = datetime.now(paris_tz)
is_weekend = now_paris.weekday() == 5 or (now_paris.weekday() == 6 and now_paris.hour < 23)

try:
    ticker_symbol = "MNQ=F"
    data = yf.download(ticker_symbol, period="5d", interval="15m", progress=False)

    if data is not None and not data.empty:
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Calculs techniques
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        data['RSI'] = 100 - (100 / (1 + (gain / loss)))
        data['MA20'] = data['Close'].rolling(window=20).mean()

        current_price = float(data['Close'].iloc[-1])
        change = current_price - float(data['Close'].iloc[-2])
        rsi_now = data['RSI'].iloc[-1]
        ma_now = data['MA20'].iloc[-1]

        # 4. DASHBOARD PRIX & SIGNAUX
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="MNQ - PRIX ACTUEL", value=f"{current_price:,.2f} $", delta=f"{change:,.2f} $")
        with col2:
            if is_weekend:
                st.markdown(f"<p style='margin-bottom:0;'>STATUT</p><p class='status-closed'>FERMÉ</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='margin-bottom:0;'>STATUT</p><p class='status-open'>OUVERT</p>", unsafe_allow_html=True)
        with col3:
            # Sentiment de marché basé sur RSI
            sentiment = "NEUTRE ⚖️"
            if rsi_now > 65: sentiment = "ACHATS FORTS 🔥"
            elif rsi_now < 35: sentiment = "VENTES FORTES ❄️"
            st.metric(label="SENTIMENT MARCHÉ", value=sentiment)

        # 5. GRAPHIQUE
        fig = go.Figure(data=[go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
            increasing_line_color='#007bff', increasing_fillcolor='#007bff',
            decreasing_line_color='#ffffff', decreasing_fillcolor='#ffffff'
        )])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500, margin=dict(l=5, r=5, t=5, b=5))
        st.plotly_chart(fig, use_container_width=True)

except:
    st.error("Connexion au flux MNQ...")

# 6. SIDEBAR ÉPURÉE (Gestion du risque uniquement)
st.sidebar.header("⚙️ STRATÉGIE")
cap = st.sidebar.number_input("Capital de Trading ($)", value=2000)
st.sidebar.divider()
st.sidebar.write(f"RSI : **{rsi_now:.1f}**")
st.sidebar.write(f"MA20 : **{ma_now:,.1f}**")
st.sidebar.info(f"Rappel : 1 point = 2$. Un stop de 40 points = 80$ de risque.")

if st.button('🔄 RECHARGER LE TERMINAL'):
    st.rerun()
