import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz

# 1. Config de la page
st.set_page_config(page_title="MNQ 🚀", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stMetricValue"] { font-size: 40px !important; }
    .status-closed { color: #ff4b4b; font-weight: bold; font-size: 40px; }
    .status-open { color: #00ff41; font-weight: bold; font-size: 40px; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 15px; }
    </style>
""", unsafe_allow_html=True)

# TITRE DEMANDÉ
st.title("MNQ 🚀 📢")

# 2. Logique Marché (Heure de Paris)
paris_tz = pytz.timezone('Europe/Paris')
now_paris = datetime.now(paris_tz)
# Samedi ou Dimanche avant 23h = FERMÉ
is_weekend = now_paris.weekday() == 5 or (now_paris.weekday() == 6 and now_paris.hour < 23)

# 3. Données (Intervalle 15m)
ticker_symbol = "MNQ=F"
# On télécharge les données
data = yf.download(ticker_symbol, period="2d", interval="15m", progress=False)

if not data.empty:
    current_price = data['Close'].iloc[-1]
    last_close = data['Close'].iloc[-2]
    change = current_price - last_close
    pct_change = (change / last_close) * 100

    # Dashboard Metrics
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
        st.metric(label="PLUS HAUT (M15)", value=f"{data['High'].max():,.2f} $")

    # 4. GRAPHIQUE BOUGIES JAPONAISES (Bleu & Blanc)
    st.subheader("📊 Graphique M15")
    
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        # Couleurs personnalisées : Bleu pour la hausse, Blanc pour la baisse
        increasing_line_color='#007bff', # Bleu
        increasing_fillcolor='#007bff',
        decreasing_line_color='#ffffff', # Blanc
        decreasing_fillcolor='#ffffff'
    )])

    fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# 5. Sidebar Gestion du Risque
st.sidebar.header("🧮 Gestion du Risque")
capital = st.sidebar.number_input("Capital ($)", value=2000)
contrats = st.sidebar.slider("Contrats MNQ", 1, 10, 1)
stop_loss = st.sidebar.number_input("Stop Loss (Points)", value=40)
st.sidebar.divider()
risque = stop_loss * 2 * contrats
pourcentage = (risque/capital)*100
st.sidebar.write(f"Risque : **{risque} $** ({pourcentage:.2f}%)")

if pourcentage > 5:
    st.sidebar.error("⚠️ Risque trop élevé !")
else:
    st.sidebar.success("✅ Risque maîtrisé")

# Bouton de rafraîchissement manuel
if st.button('🔄 ACTUALISER LE PRIX'):
    st.rerun()
