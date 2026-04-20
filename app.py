import streamlit as st
import requests

# --- TES INFOS ---
TOKEN = "TON_TOKEN_ICI"  # <--- METS ICI LE CODE DE BOTFATHER
CHAT_ID = "7836102896"

def send_alert(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data)
    except:
        pass

st.set_page_config(page_title="Nasdaq SMC Bot", layout="wide")

st.title("📈 Nasdaq Smart Money Tracker")
st.write("Surveillance des FVG et BOS en cours...")

# Bouton de test
if st.button("🔔 Tester l'alerte sur mon téléphone"):
    send_alert("🚀 **Connexion réussie !**\nTon app Nasdaq est prête à envoyer des signaux SMC.")
    st.success("Signal envoyé ! Regarde Telegram.")

# Graphique TradingView Pro
st.components.v1.html("""
    <div style="height:600px;">
        <div id="tv_chart" style="height:100%;"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({
          "autosize": true,
          "symbol": "NASDAQ:QQQ",
          "interval": "15",
          "theme": "dark",
          "style": "1",
          "locale": "fr",
          "container_id": "tv_chart",
          "studies": ["RSI@tv-basicstudies"]
        });
        </script>
    </div>
""", height=600)
