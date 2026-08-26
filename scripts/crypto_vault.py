import os
import sys
import json
import base64
import hashlib
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
import env_loader

def load_configured_users() -> dict:
    """
    Carrega dinamicamente a lista de usuários autorizados a partir de:
    1. Variável de ambiente / GitHub Secret AUTH_USERS_JSON
    2. Arquivo local users.json (ignorado pelo Git)
    3. Variável de ambiente / GitHub Secret AUTH_USERS_LIST
    4. Variável PASS_USER_S1 ou PASS_LOGIN com usuários padrão
    """
    users = {}

    # 1. Variável AUTH_USERS_JSON (JSON string)
    auth_json = os.getenv("AUTH_USERS_JSON", "")
    if auth_json:
        try:
            parsed = json.loads(auth_json)
            if isinstance(parsed, list):
                for item in parsed:
                    u = (item.get("user") or item.get("username") or "").strip().lower()
                    if u:
                        users[u] = {
                            "password": item.get("pass") or item.get("password") or "",
                            "nome": item.get("nome") or u,
                            "perfil": item.get("perfil") or "Usuário Corporativo"
                        }
            elif isinstance(parsed, dict):
                for u, item in parsed.items():
                    u_key = u.strip().lower()
                    if isinstance(item, dict):
                        users[u_key] = {
                            "password": item.get("pass") or item.get("password") or "",
                            "nome": item.get("nome") or u,
                            "perfil": item.get("perfil") or "Usuário Corporativo"
                        }
                    elif isinstance(item, str):
                        users[u_key] = {
                            "password": item,
                            "nome": u,
                            "perfil": "Usuário Corporativo"
                        }
        except Exception as e:
            print(f"Aviso ao processar AUTH_USERS_JSON: {e}")

    # 2. Arquivo local users.json
    users_file = os.path.join(PROJECT_DIR, "users.json")
    if not users and os.path.exists(users_file):
        try:
            with open(users_file, "r", encoding="utf-8") as f:
                parsed = json.load(f)
                if isinstance(parsed, list):
                    for item in parsed:
                        u = (item.get("user") or item.get("username") or "").strip().lower()
                        if u:
                            users[u] = {
                                "password": item.get("pass") or item.get("password") or "",
                                "nome": item.get("nome") or u,
                                "perfil": item.get("perfil") or "Usuário Corporativo"
                            }
        except Exception as e:
            print(f"Aviso ao ler users.json: {e}")

    # 3. Variável AUTH_USERS_LIST (Ex: "marcelo.guedes:s1@jira:Marcelo Guedes, rubia.felix:s1@jira:Rubia Felix")
    auth_list = os.getenv("AUTH_USERS_LIST", "")
    if not users and auth_list:
        entries = auth_list.split(",")
        for entry in entries:
            parts = [p.strip() for p in entry.split(":")]
            if len(parts) >= 2:
                u = parts[0].lower()
                pwd = parts[1]
                nome = parts[2] if len(parts) > 2 else u
                perfil = parts[3] if len(parts) > 3 else "Usuário Corporativo"
                users[u] = {"password": pwd, "nome": nome, "perfil": perfil}

    # 4. Fallback simples via PASS_USER_S1 / PASS_LOGIN
    if not users:
        single_pass = os.getenv("PASS_USER_S1", os.getenv("PASS_LOGIN", ""))
        if not single_pass:
            raise ValueError("Nenhum usuário ou senha configurado! Defina AUTH_USERS_JSON ou PASS_USER_S1 no .env ou Secrets.")
        users = {
            "marcelo.guedes": {
                "password": single_pass,
                "nome": "Marcelo Guedes",
                "perfil": "Analista de Sistemas"
            },
            "rubia.felix": {
                "password": single_pass,
                "nome": "Rubia Felix",
                "perfil": "Diretora de Operações"
            }
        }

    return users

def derive_user_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )
    return kdf.derive(password.encode('utf-8'))

def build_encrypted_vault(data_dict: dict, users_dict: dict = None) -> dict:
    """
    Criptografa o dicionário de dados em AES-256-GCM e empacota
    as chaves de acesso para cada usuário autorizado.
    """
    if users_dict is None:
        users_dict = load_configured_users()

    # 1. Gerar Chave Mestra do Cofre
    master_key = AESGCM.generate_key(bit_length=256)
    aesgcm_master = AESGCM(master_key)

    # 2. Criptografar Payload de Dados
    payload_bytes = json.dumps(data_dict, ensure_ascii=False).encode('utf-8')
    data_iv = secrets.token_bytes(12)
    encrypted_data = aesgcm_master.encrypt(data_iv, payload_bytes, None)

    # 3. Envelopar a Chave Mestra para cada usuário
    users_vault = {}
    for username, uinfo in users_dict.items():
        pwd = uinfo.get("password", "")
        if not pwd:
            continue
            
        user_salt = secrets.token_bytes(16)
        user_key = derive_user_key(pwd, user_salt)
        
        aesgcm_user = AESGCM(user_key)
        user_iv = secrets.token_bytes(12)
        wrapped_master_key = aesgcm_user.encrypt(user_iv, master_key, None)
        
        users_vault[username] = {
            "nome": uinfo.get("nome", username),
            "perfil": uinfo.get("perfil", "Usuário"),
            "salt": base64.b64encode(user_salt).decode('ascii'),
            "iv": base64.b64encode(user_iv).decode('ascii'),
            "wrapped_key": base64.b64encode(wrapped_master_key).decode('ascii')
        }

    vault = {
        "version": "1.0",
        "algorithm": "AES-256-GCM / PBKDF2-SHA256",
        "data_iv": base64.b64encode(data_iv).decode('ascii'),
        "encrypted_data": base64.b64encode(encrypted_data).decode('ascii'),
        "users": users_vault
    }

    return vault

if __name__ == "__main__":
    teste_dados = {"mensagem": "Dados protegidos com sucesso pela LGPD S1 Saúde"}
    cofre = build_encrypted_vault(teste_dados)
    print("Cofre criptográfico gerado com sucesso!")
    print(f"- Usuários configurados: {list(cofre['users'].keys())}")
    print(f"- Tamanho do dado criptografado: {len(cofre['encrypted_data'])} bytes")
