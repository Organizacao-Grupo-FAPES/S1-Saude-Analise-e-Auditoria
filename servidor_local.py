import os
import sys
import json
import socket
import threading
import subprocess
import urllib.parse
from datetime import datetime
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(PROJECT_DIR, "scripts")
PORT = 8088

is_syncing = False

def run_sync_pipeline():
    global is_syncing
    if is_syncing:
        print("[SYNC] Sincronização já em andamento.")
        return
    is_syncing = True
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [SYNC] Iniciando pipeline de extração e consolidação do Jira...")
    try:
        pipeline_scripts = [
            "extractor_s1.py",
            "extract_interactions.py",
            "analytics_s1.py",
            "monitor_alertas_diretoria.py",
            "build_professional_dashboard.py"
        ]

        for s_name in pipeline_scripts:
            s_path = os.path.join(SCRIPTS_DIR, s_name)
            if os.path.exists(s_path):
                subprocess.run([sys.executable, s_path], check=True)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] [OK] Sincronização concluída com sucesso!")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERRO] Falha no sync:", e)
    finally:
        is_syncing = False

class S1DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PROJECT_DIR, **kwargs)

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                self.rfile.read(content_length)

            parsed_path = urllib.parse.urlparse(self.path)
            if parsed_path.path == "/api/sync":
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [API] Sincronização solicitada via Dashboard!")
                t = threading.Thread(target=run_sync_pipeline, daemon=True)
                t.start()

                response_data = {
                    "status": "success",
                    "message": "Sincronização com o Jira iniciada em segundo plano!"
                }
                body = json.dumps(response_data).encode('utf-8')

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_error(404, "Endpoint não encontrado")
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass

    def do_OPTIONS(self):
        try:
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass

    def copyfile(self, source, outputfile):
        try:
            super().copyfile(source, outputfile)
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            pass

    def log_message(self, format, *args):
        # Log limpo
        pass

class RobustHTTPServer(ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        exc_type, exc_val, _ = sys.exc_info()
        if exc_type in (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            return
        super().handle_error(request, client_address)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def run_server():
    server_address = ('0.0.0.0', PORT)
    httpd = RobustHTTPServer(server_address, S1DashboardHandler)
    local_ip = get_local_ip()
    print("=================================================================")
    print("      S1 SAÚDE - COCKPIT EXECUTIVO DE AUDITORIA ATIVO            ")
    print("=================================================================")
    print(f"   [1] Acesso Local:       http://localhost:{PORT}/index.html")
    print(f"   [2] Acesso IP na Rede:  http://{local_ip}:{PORT}/index.html")
    print("=================================================================")
    print("   Pressione Ctrl+C ou feche a janela para encerrar o serviço.   ")
    print("=================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor finalizado pelo usuário.")

if __name__ == "__main__":
    run_server()
