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

st.title("MNQ 🚀 📢")

# 2. Logique Marché
paris_tz = pytz.timezone('Europe/Paris')
now_paris = datetime.now(paris_tz)
is_weekend = now_paris.weekday() == 5 or (now_paris.weekday() == 6 and now_paris.hour < 23)

# 3. Récupération sécurisée des données
try:
    ticker_symbol = "MNQ=F"
    # On télécharge 3 jours pour être sûr d'avoir de la donnée
    data = yf.download(ticker_symbol, period="3d", interval="15m", progress=False)

    if data is not None and not data.empty:
        # On s'assure que les colonnes sont simples (parfois yfinance met des doubles noms)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        current_price = float(data['Close'].iloc[-1])
        last_close = float(data['Close'].iloc[-2])
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
        with col3:
            st.metric(label="PLUS HAUT (M15)", value=f"{data['High'].max():,.2f} $")

        # 4. Graphique Bleu & Blanc
        st.subheader("📊 Graphique M15")
        fig = go.Figure(data=[go.Candlestick(
            x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
            increasing_line_color='#007bff', increasing_fillcolor='#007bff',
            decreasing_line_color='#ffffff', decreasing_fillcolor='#ffffff'
        )])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500,
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⏳ En attente des données du marché...")

except Exception as e:
    st.info("Connexion au flux en cours... Le marché est peut-être trop calme.")

# 5. Sidebar Risk
st.sidebar.header("🧮 Gestion du Risque")
cap = st.sidebar.number_input("Capital ($)", value=2000)
st.sidebar.write(f"Risque 1 contrat (40 pts) : **80 $** ({(80/cap)*100:.1f}%)")

if st.button('🔄 ACTUALISER'):
    st.rerun()
