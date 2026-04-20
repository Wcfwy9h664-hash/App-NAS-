import time
import requests

# --- CONFIGURATION ---
# Crée un bot sur Telegram via @BotFather pour avoir ces infos
TOKEN = "TON_TOKEN_TELEGRAM"
CHAT_ID = "TON_CHAT_ID"

def send_alert(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    requests.get(url)

def detect_fvg(candles):
    """
    Détecte un Fair Value Gap (FVG)
    Un FVG haussier : le bas de la bougie 3 est plus haut que le haut de la bougie 1
    """
    b1, b2, b3 = candles[-3], candles[-2], candles[-1]
    
    # FVG HAUSSIER (Bullish Gap)
    if b3['low'] > b1['high']:
        return "🚀 FVG HAUSSIER détecté ! Le prix risque de revenir tester cette zone."
    
    # FVG BAISSIER (Bearish Gap)
    if b3['high'] < b1['low']:
        return "📉 FVG BAISSIER détecté ! Pression vendeuse forte."
    
    return None

# Simulation de la boucle de surveillance
print("Surveillance du NASDAQ en cours...")
while True:
    # Ici, on devrait normalement récupérer les vraies bougies via une API (ex: Binance ou Alpaca)
    # Pour l'exemple, on imagine qu'on a les 3 dernières bougies
    # signal = detect_fvg(data)
    # if signal:
    #     send_alert(signal)
    
    time.sleep(60) # Vérifie toutes les minutes
