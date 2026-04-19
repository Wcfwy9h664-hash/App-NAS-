import streamlit as st
import yfinance as yf
import requests
import pandas as pd

# 1. Configuration - Look Pro & Fusée 🚀
st.set_page_config(page_title="Nasdaq Rocket Pro", page_icon="🚀", layout="centered")

# CSS pour un design sombre et épuré
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stMetric { background-color: #0e1117; padding: 20px; border-radius: 15px; border: 1px solid #31333F; }
    div.stButton > button:first-child { background-color: #2e7d32; color: white; width: 100%; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Nasdaq Intelligence")

# 2. Récupération des données du NASDAQ (^IXIC)
nasdaq = yf.Ticker("^IXIC")
hist = nasdaq.history(period="2d", interval="5m")

if not hist.empty:
    prix_actuel = hist['Close'].iloc[-1]
    prix_ouverture = hist['Close'].iloc[0]
    variation = prix_actuel - prix_ouverture
    pct_var = (variation / prix_ouverture) * 100

    # Affichage du prix en gros
    st.metric(label="NASDAQ 100 (Live)", 
              value=f"{prix_actuel:,.2f} $", 
              delta=f"{variation:,.2f} $ ({pct_var:.2f}%)")

    # 3. Intelligence News Spéciale Nasdaq
    st.subheader("📰 Analyse du Sentiment")
    api_key = "Ff12b93f85484bb0b854389fb3f9e578"
    url = f'https://newsapi.org/v2/everything?q=Nasdaq+FED+Economy&language=fr&sortBy=publishedAt&apiKey={api_key}'

    try:
        res = requests.get(url).json()
        if res['articles']:
            news = res['articles'][0]
            st.info(f"**Dernière news :** {news['title']}")
            
            # Algorithme de prédiction simplifié
            texte = news['title'].lower()
            if any(w in texte for w in ["hausse", "croissance", "positif", "record", "fed", "emploi"]):
                st.success("🔮 TENDANCE : HAUSSE PROBABLE (Bullish) 🟢")
            elif any(w in texte for w in ["chute", "inflation", "négatif", "baisse", "krach"]):
                st.error("🔮 TENDANCE : PRUDENCE REQUISE (Bearish) 🔴")
            else:
                st.warning("🔮 TENDANCE : NEUTRE / ATTENTE 🟡")
    except:
        st.write("Flux de news en cours...")

    # 4. Graphique Intra-day
    st.subheader("📈 Évolution du jour")
    st.area_chart(hist['Close'])

    # 5. Statistiques Clés
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"📉 **Bas du jour :** {hist['Low'].min():.2f}")
    with col2:
        st.write(f"📈 **Haut du jour :** {hist['High'].max():.2f}")

# Bouton de rafraîchissement
if st.button('🔄 Actualiser les données'):
    st.rerun()
