import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# 1. Config de la page
st.set_page_config(page_title="MNQ 🚀", page_icon="🚀", layout="wide")

# Style CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stMetricValue"] { font-size: 40px !important; }
    .status-closed { color: #ff4b4b; font-weight: bold; font-size: 40px; }
    .status-open { color: #00ff41; font-weight: bold; font-size: 40px; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 15px; }
    </style>
""", unsafe_allow_html=True)

# LE NOUVEAU TITRE QUE TU AS DEMANDÉ
st.title("MNQ 🚀 📢")

# 2. Logique d'ouverture du marché (Heure de Paris)
paris_tz = pytz.timezone('Europe/Paris')
now_paris = datetime.now(paris_tz)
is_weekend = now_paris.weekday() == 5 or (now_paris.weekday() == 6 and now_paris.hour < 23)

# 3. Récupération des données
ticker_symbol = "MNQ=F"
ticker = yf.Ticker(ticker_symbol)
data = ticker.history(period="2d", interval="5m")

if not data.empty:
    current_price = data['Close'].iloc[-1]
    last_close = data['Close'].iloc[-2]
    change = current_price - last_close
    pct_change = (change / last_close) * 100

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="MICRO NASDAQ (MNQ)", value=f"{current_price:,.2f} $", delta=f"{change:,.2f} $ ({pct_change:.2f}%)")
    
    with col2:
        if is_weekend:
            st.markdown("<p style='color:gray; font-size:14px; margin-bottom:0;'>STATUT MARCHÉ</p>", unsafe_allow_html=True)
            st.markdown("<p class='status-closed'>FERMÉ</p>", unsafe_allow_html=True)
            st.caption("🔴 Réouverture à 23h00")
        else:
            st.markdown("<p style='color:gray; font-size:14px; margin-bottom:0;'>STATUT MARCHÉ</p>", unsafe_allow_html=True)
            st.markdown("<p class='status-open'>OUVERT</p>", unsafe_allow_html=True)
            st.caption("🟢 Session en cours")
    
    with col3:
        st.metric(label="PLUS HAUT (SESSION)", value=f"{data['High'].max():,.2f} $")

    # Graphique
    st.subheader("📈 Graphique Intra-day")
    st.area_chart(data['Close'])
    
# 4. Barre latérale : Calculateur de Risk
st.sidebar.header("🧮 Gestion du Risque")
capital = st.sidebar.number_input("Capital total ($)", value=2000)
contrats = st.sidebar.slider("Nombre de contrats MNQ", 1, 10, 1)
stop_loss_points = st.sidebar.number_input("Stop Loss (en points)", value=40)

# Calcul : 1 point de MNQ = 2$
risque_dollars = stop_loss_points * 2 * contrats
pourcentage_risque = (risque_dollars / capital) * 100

st.sidebar.divider()
st.sidebar.write(f"Perte potentielle : **{risque_dollars} $**")
if pourcentage_risque > 5:
    st.sidebar.error(f"Risque élevé : {pourcentage_risque:.2f}% du compte")
else:
    st.sidebar.success(f"Risque correct : {pourcentage_risque:.2f}% du compte")

# Bouton Refresh
if st.button('🔄 ACTUALISER'):
    st.rerun()
