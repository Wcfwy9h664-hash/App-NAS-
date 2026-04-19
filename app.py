import streamlit as st
import yfinance as yf
import requests

st.title("📈 Nasdaq Live Intelligence")

# 1. Le Prix
nasdaq = yf.Ticker("^IXIC")
prix = nasdaq.fast_info['last_price']
st.metric("NASDAQ 100", f"{prix:.2f} $")

# 2. Les News & Prédiction
st.subheader("📰 News & Analyse")
api_key = "Ff12b93f85484bb0b854389fb3f9e578"
url = f'https://newsapi.org/v2/everything?q=Nasdaq+FED&language=fr&sortBy=publishedAt&apiKey={api_key}'

try:
    res = requests.get(url).json()
    titre = res['articles'][0]['title']
    st.info(f"Dernière info : {titre}")
    
    low_t = titre.lower()
    if any(w in low_t for w in ["hausse", "croissance", "positif"]):
        st.success("🔮 PRÉDICTION : HAUSSE")
    elif any(w in low_t for w in ["chute", "inflation", "négatif"]):
        st.error("🔮 PRÉDICTION : BAISSE")
    else:
        st.warning("🔮 PRÉDICTION : NEUTRE")
except:
    st.write("Chargement...")

# 3. Le Graphique
st.line_chart(nasdaq.history(period="1d", interval="15m")['Close'])
