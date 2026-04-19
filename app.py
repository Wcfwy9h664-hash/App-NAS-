import streamlit as st
import yfinance as yf
import pandas as pd

# Config pro
st.set_page_config(page_title="Nasdaq Rocket Pro", page_icon="🚀", layout="wide")

# CSS spécial Mode Sombre & Alertes
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: white; }
    .stMetric { background-color: #111; border: 1px solid #333; padding: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 MNQ TERMINAL STRATÉGIQUE")

# --- 1. RÉCUPÉRATION DES DONNÉES ---
ticker = yf.Ticker("MNQ=F")
data = ticker.history(period="1d", interval="5m")

if not data.empty:
    prix = data['Close'].iloc[-1]
    variation = ((prix - data['Open'].iloc[0]) / data['Open'].iloc[0]) * 100

    # --- 2. DASHBOARD DE PRIX ---
    col1, col2, col3 = st.columns(3)
    col1.metric("MICRO NASDAQ", f"{prix:,.2f} $", f"{variation:.2f}%")
    
    # Indicateur de force (RSI simplifié)
    force = "NEUTRE ⚖️"
    if variation > 0.5: force = "ACHAT FORT 🔥"
    elif variation < -0.5: force = "VENTE FORTE ❄️"
    col2.metric("SIGNAL IA", force)
    
    col3.metric("PLUS HAUT JOUR", f"{data['High'].max():,.2f} $")

    # --- 3. GRAPHIQUE INTERACTIF ---
    st.area_chart(data['Close'])

    # --- 4. CALCULATEUR DE RISQUE (Nouveau !) ---
    st.sidebar.header("🧮 Calculateur de Risk")
    capital = st.sidebar.number_input("Ton Capital ($)", value=1000)
    stop_loss = st.sidebar.slider("Stop Loss (Points)", 10, 200, 50)
    
    # Le MNQ vaut 2$ le point
    risque_euro = stop_loss * 2
    st.sidebar.warning(f"Si tu perds ce trade, tu perds : {risque_euro} $")
    st.sidebar.info(f"Soit { (risque_euro/capital)*100:.1f}% de ton compte.")

else:
    st.info("⌛ En attente de l'ouverture du marché (23h00)...")
    st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueGZ3bmZ6NHR6NXN6NXN6NXN6NXN6NXN6NXN6NXN6NXN6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKMGpxx323Xf8xG/giphy.gif", width=300)

# Refresh automatique toutes les 60 secondes
# st.empty() # Placeholder pour le futur
