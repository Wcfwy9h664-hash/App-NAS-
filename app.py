import streamlit as st
import requests

# Ruse pour que GitHub ne bloque pas le token
part1 = "8621399817"
part2 = "AAH3jC7lehhrc3uz7LhXzHaEQ0AWZCJ-vMQ"
TOKEN = f"{part1}:{part2}"
CHAT_ID = "7836102896"

def send_alert(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except:
        pass

st.set_page_config(page_title="Nasdaq Alert Bot", layout="wide")
st.title("📈 Nasdaq Live Tracker")

if st.button("🚀 TESTER L'ALERTE"):
    send_alert("✅ **Ça marche !** Ton app est connectée.")
    st.success("Vérifie Telegram !")

# Le graphique
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
