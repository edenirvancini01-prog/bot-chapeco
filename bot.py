import time
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- CONFIGURAÇÕES DO BOT ---
TELEGRAM_TOKEN = "HTTP API:8744642328:AAGw5tDvh-AtbjCqnXDVO75sqmOC_WpeXyo"
CHAT_ID = "1337502984"
LAT_CHAPECO = -27.1004
LON_CHAPECO = -52.6152
API_URL = f"https://open-meteo.com{LAT_CHAPECO}&longitude={LON_CHAPECO}&hourly=precipitation&current_weather=true&timezone=America%2FSao_Paulo"
MODO_EL_NINO = True

LIMIAR_ACUMULADO = 30.0 if MODO_EL_NINO else 40.0
LIMIAR_INTENSIDADE = 15.0 if MODO_EL_NINO else 20.0

def enviar_mensagem_telegram(texto):
    url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e: print(e)

def monitorar_chapeco():
    enviar_mensagem_telegram("⚡ *Bot Chapecó hospedado com sucesso e monitorando!*")
    while True:
        try:
            response = requests.get(API_URL, timeout=10)
            if response.status_code == 200:
                dados = response.json()
                chuva_hora = dados['hourly']['precipitation'][-1]
                if chuva_hora > LIMIAR_INTENSIDADE:
                    enviar_mensagem_telegram(f"🚨 *ALERTA:* Chuva torrencial em Chapecó ({chuva_hora:.1f} mm/h)!")
        except Exception as e: print(e)
        time.sleep(600)

# --- MINI SERVIDOR WEB (Obrigatório para o Render não desligar o bot) ---
class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Online")

def rodar_servidor_web():
    server = HTTPServer(('0.0.0.0', 10000), WebServer)
    server.serve_forever()

if __name__ == "__main__":
    # Roda o monitoramento em uma linha de tempo separada
    threading.Thread(target=monitorar_chapeco, daemon=True).start()
    # Roda o servidor web na linha principal
    rodar_servidor_web()
