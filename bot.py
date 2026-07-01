
import time
import requests
import threading
import sys
import smtplib
from email.mime.text import MIMEText
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- CONFIGURAÇÕES DE E-MAIL ---
EMAIL_REMETENTE = "edenirvancini@gmail.com"     # O e-mail que vai ENVIAR o alerta
EMAIL_SENHA = "Edenir.025"            # Senha de App gerada na sua conta Google
EMAIL_DESTINATARIO = "edenirvancini@gmail.com"  # O e-mail que vai RECEBER (pode ser o mesmo)

# --- CONFIGURAÇÕES METEOROLÓGICAS ---
LAT_CHAPECO = -27.1004
LON_CHAPECO = -52.6152
API_URL = f"https://open-meteo.com{LAT_CHAPECO}&longitude={LON_CHAPECO}&hourly=precipitation&current_weather=true&timezone=America%2FSao_Paulo"
MODO_EL_NINO = True

LIMIAR_ACUMULADO = 30.0 if MODO_EL_NINO else 40.0
LIMIAR_INTENSIDADE = 15.0 if MODO_EL_NINO else 20.0

def enviar_alerta_email(assunto, corpo):
    """Conecta ao servidor do Gmail e envia o e-mail de alerta."""
    msg = MIMEText(corpo, 'plain', 'utf-8')
    msg['Subject'] = assunto
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINATARIO

    try:
        # Configuração padrão para o servidor SMTP do Gmail
        with smtplib.SMTP_SSL('://gmail.com', 465, timeout=15) as servidor:
            servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)
            servidor.sendmail(EMAIL_REMETENTE, [EMAIL_DESTINATARIO], msg.as_string())
        print(f"📧 E-mail enviado com sucesso: {assunto}")
        sys.stdout.flush()
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")
        sys.stdout.flush()

def monitorar_chapeco():
    print("🤖 Monitoramento de Chapecó via E-mail iniciado...")
    sys.stdout.flush()
    
    # E-mail de teste ao iniciar
    enviar_alerta_email(
        "⚡ Sistema de Alertas Ativo", 
        f"O monitoramento de Chapecó está rodando na nuvem.\nModo El Niño: {'ATIVADO' if MODO_EL_NINO else 'DESATIVADO'}"
    )
    
    while True:
        try:
            print("🛰️ Verificando clima em Chapecó...")
            sys.stdout.flush()
            response = requests.get(API_URL, timeout=10)
            if response.status_code == 200:
                dados = response.json()
                chuva_hora = dados['hourly']['precipitation'][-1]
                chuva_24h = sum(dados['hourly']['precipitation'][:24])
                
                print(f"🌧️ Chuva medida: {chuva_hora} mm/h | Acumulado 24h: {chuva_24h:.1f} mm")
                sys.stdout.flush()
                
                if chuva_hora > LIMIAR_INTENSIDADE:
                    enviar_alerta_email(
                        "🚨 ALERTA DEFESA CIVIL: Chuva Torrencial!",
                        f"Atenção! Chuva torrencial detectada em Chapecó: {chuva_hora:.1f} mm/h.\nRisco iminente de enxurradas."
                    )
                elif chuva_24h > LIMIAR_ACUMULADO:
                    enviar_alerta_email(
                        "🚨 ALERTA DEFESA CIVIL: Volume Acumulado Alto",
                        f"Atenção! Volume acumulado de chuva atingiu {chuva_24h:.1f} mm nas últimas horas em Chapecó.\nRisco de alagamentos e deslizamentos."
                    )
            else:
                print(f"⚠️ Erro na API de clima: Status {response.status_code}")
                sys.stdout.flush()
        except Exception as e:
            print(f"❌ Erro no loop de monitoramento: {e}")
            sys.stdout.flush()
        time.sleep(600)

# --- MINI SERVIDOR WEB (Obrigatório para o Render) ---
class WebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Monitor de Email Online")
    def log_message(self, format, *args): return

def rodar_servidor_web():
    server = HTTPServer(('0.0.0.0', 10000), WebServer)
    server.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=monitorar_chapeco, daemon=True)
    t.start()
    rodar_servidor_web()
