import streamlit as st
import yfinance as yf
import requests
import pandas as pd
from datetime import datetime

# 1. Configuration de l'application
st.set_page_config(
    page_title="Nasdaq MNQ Tracker",
    page_icon="🚀",
    layout="centered"
)

# Style CSS personnalisé pour un look "Terminal de Trading"
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div.stMetric {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px 20px;
        border-radius: 10px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #238636;
        color: white;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 MNQ Micro Nasdaq-100")
st.caption(f"Données récupérées le : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# 2. Récupération du prix du Micro Nasdaq Futures
# MNQ=F est le symbole pour le contrat futur Micro E-mini sur Yahoo Finance
ticker_symbol = "MNQ=F"

try:
    ticker = yf.Ticker(ticker_symbol)
    # On récupère les données de la journée avec un intervalle de 5 minutes
    df = ticker.history(period="1d", interval="5m")
    
    if not df.empty:
        current_price = df['Close'].iloc[-1]
        previous_close = df['Close'].iloc[0]
        change = current_price - previous_close
        pct_change = (change / previous_close) * 100

        # Affichage du prix principal
        st.metric(
            label="Prix MNQ Futures (Live/Delayed)",
            value=f"{current_price:,.2f} $",
            delta=f"{change:,.2f} $ ({pct_change:.2f}%)"
        )

        # 3. Graphique Intra-day (Area chart pour un look moderne)
        st.subheader("📈 Évolution Intra-day")
        st.area_chart(df['Close'], use_container_width=True)

        # Stats rapides en colonnes
        col1, col2, col3 = st.columns(3)
        col1.write(f"**Haut:** {df['High'].max():.2f}")
        col2.write(f"**Bas:** {df['Low'].min():.2f}")
        col3.write(f"**Volume:** {ticker.fast_info.get('last_volume', 'N/A')}")

    else:
        st.warning("Marché fermé ou données indisponibles pour le moment.")

except Exception as e:
    st.error(f"Erreur lors de la récupération des prix : {e}")

# 4. Section News & Sentiment
st.divider()
st.subheader("📰 Intelligence & News")

# Utilisation de ton API News pour l'analyse
api_key = "Ff12b93f85484bb0b854389fb3f9e578"
news_url = f'https://newsapi.org/v2/everything?q=Nasdaq+FED+Economy&language=fr&sortBy=publishedAt&apiKey={api_key}'

try:
    response = requests.get(news_url).json()
    if response.get('articles'):
        top_news = response['articles'][0]
        st.info(f"**Dernière info :** {top_news['title']}")
        
        # Logique de prédiction simplifiée basée sur les mots clés
        text = top_news['title'].lower()
        if any(w in text for w in ["hausse", "croissance", "positif", "record", "fed", "emploi"]):
            st.success("🔮 PRÉDICTION : HAUSSE (Bullish) 🟢")
        elif any(w in text for w in ["chute", "inflation", "baisse", "danger", "krach"]):
            st.error("🔮 PRÉDICTION : BAISSE (Bearish) 🔴")
        else:
            st.warning("🔮 PRÉDICTION : NEUTRE / ATTENTE 🟡")
    else:
        st.write("Aucune actualité récente trouvée.")
except:
    st.write("Erreur de connexion au flux d'actualités.")

# 5. Bouton d'actualisation manuelle
st.divider()
if st.button('🔄 Actualiser le prix'):
    st.rerun()

st.caption("Note : Les prix MNQ=F peuvent avoir un délai de 10 à 20 minutes par rapport au flux réel CME.")
