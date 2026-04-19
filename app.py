import streamlit as st
import yfinance as yf
import requests
from datetime import datetime

# 1. Config de l'onglet et de la fusée
st.set_page_config(page_title="Nasdaq 🚀", page_icon="🚀")

# Style pour un look pro et cacher les logos Streamlit
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

# 2. ASTUCE POUR L'ICÔNE : Grosse fusée centrée
st.markdown("<h1 style='text-align: center; font-size: 70px;'>🚀</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>MNQ Intelligence</h2>", unsafe_allow_html=True)

# 3. Récupération MNQ (Micro Nasdaq)
ticker_symbol = "MNQ=F"

try:
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period="1d", interval="5m")
    
    if not df.empty:
        current_price = df['Close'].iloc[-1]
        previous_close = df['Close'].iloc[0]
        change = current_price - previous_close
        pct_change = (change / previous_close) * 100

        # Affichage du prix (S'actualisera à 23h !)
        st.metric(
            label="Micro Nasdaq Futures",
            value=f"{current_price:,.2f} $",
            delta=f"{change:,.2f} $ ({pct_change:.2f}%)"
        )
        
        # Graphique
        st.area_chart(df['Close'])
    else:
        # Message si le marché est fermé
        st.warning("Marché fermé. Ouverture ce soir à 23h00.")
        st.info("Dernière clôture enregistrée : ~26,825 $")

except Exception as e:
    st.error("Connexion aux flux financiers en attente...")

# 4. News & IA
st.subheader("📰 Sentiment du Marché")
api_key = "Ff12b93f85484bb0b854389fb3f9e578"
url = f'https://newsapi.org/v2/everything?q=Nasdaq+FED&language=fr&sortBy=publishedAt&apiKey={api_key}'

try:
    res = requests.get(url).json()
    if res.get('articles'):
        txt = res['articles'][0]['title']
        st.write(f"**News :** {txt}")
        if any(w in txt.lower() for w in ["hausse", "croissance", "positif"]):
            st.success("TENDANCE : HAUSSE 🟢")
        elif any(w in txt.lower() for w in ["baisse", "chute", "inflation"]):
            st.error("TENDANCE : BAISSE 🔴")
        else:
            st.warning("TENDANCE : NEUTRE 🟡")
except:
    pass

# Bouton de refresh en bas
if st.button('🔄 ACTUALISER LE PRIX'):
    st.rerun()
