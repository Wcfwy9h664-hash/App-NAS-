import streamlit as st
import yfinance as yf
import pandas as pd
import requests

# 1. Configuration de la page
st.set_page_config(page_title="Nasdaq MNQ Live", page_icon="🚀", layout="wide")

# Style CSS pour un look Terminal Pro
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stMetricValue"] { font-size: 40px; color: #00ff41; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 15px; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 MNQ TERMINAL STRATÉGIQUE")

# 2. Récupération des données
ticker_symbol = "MNQ=F"
ticker = yf.Ticker(ticker_symbol)

# On essaie de récupérer les données des 5 derniers jours pour avoir au moins la clôture de vendredi
data = ticker.history(period="5d", interval="5m")

# 3. Affichage conditionnel
if not data.empty:
    # On prend le dernier prix disponible (celui de vendredi soir si on est dimanche)
    current_price = data['Close'].iloc[-1]
    open_price = data['Open'].iloc[0]
    change = current_price - data['Close'].iloc[-2]
    pct_change = (change / data['Close'].iloc[-2]) * 100

    # Dashboard de Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="MICRO NASDAQ (MNQ)", value=f"{current_price:,.2f} $", delta=f"{change:,.2f} $ ({pct_change:.2f}%)")
    
    with col2:
        # Petit calcul de force relative (RSI simplifié)
        st.metric(label="STATUT MARCHÉ", value="FERMÉ" if pct_change == 0 else "OUVERT", delta="Ouverture à 23h")
    
    with col3:
        st.metric(label="PLUS HAUT (SESSION)", value=f"{data['High'].max():,.2f} $")

    # Graphique
    st.subheader("📈 Graphique MNQ (5 min)")
    st.area_chart(data['Close'])
    
else:
    # Si vraiment aucune donnée (très rare)
    st.warning("⚠️ Connexion au flux CME interrompue. Réouverture du flux à 23h00.")

# 4. Calculateur de Risk (Toujours dispo même si marché fermé)
st.sidebar.header("🧮 Gestion du Risque")
capital = st.sidebar.number_input("Capital ($)", value=2000)
levier = st.sidebar.selectbox("Nombre de contrats MNQ", [1, 2, 3, 4, 5])
stop_loss = st.sidebar.slider("Stop Loss (Points)", 10, 100, 30)

# Calcul : 1 point de MNQ = 2$
risque_total = stop_loss * 2 * levier
st.sidebar.divider()
st.sidebar.write(f"💸 Risque sur ce trade : **{risque_total} $**")
st.sidebar.write(f"📊 Impact capital : **{(risque_total/capital)*100:.2f} %**")

# 5. News & Sentiment
st.divider()
st.subheader("📰 News & Sentiment")
try:
    api_key = "Ff12b93f85484bb0b854389fb3f9e578"
    url = f'https://newsapi.org/v2/everything?q=Nasdaq+Fed&language=fr&apiKey={api_key}'
    news = requests.get(url).json()['articles'][0]
    st.info(f"**DERNIÈRE NEWS :** {news['title']}")
except:
    st.write("Chargement des actualités éco...")

# Bouton Refresh
if st.button('🔄 ACTUALISER LES DONNÉES'):
    st.rerun()
