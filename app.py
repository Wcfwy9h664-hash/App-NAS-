import streamlit as st
import requests

# --- TES INFOS DEPUIS TES IMAGES ---
TOKEN = "8621399817:AAH3jC7lehhrc3uz7LhXzHaEQ0AWZCJ-vMQ"
CHAT_ID = "7836102896"

def send_alert(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

st.set_page_config(page_title="Nasdaq Alert Bot", layout="wide")

st.title("📈 Nasdaq Live Tracker & SMC")

if st.button("🚀 TESTER L'ALERTE SUR MON TEL"):
    send_alert("✅ **Connexion Réussie !**\nLe bot @NASDAQAlerteBot est maintenant lié à ton application.")
    st.success("Regarde ton Telegram !")

# Intégration TradingView
st.components.v1.html("""
    <div style="height:500px;">
        <div id="tv-chart" style="height:100%;"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({
          "autosize": true, "symbol": "NASDAQ:QQQ", "interval": "15",
          "theme": "dark", "style": "1", "locale": "fr",
          "container_id": "tv-chart"
        });
        </script>
    </div>
""", height=500)
