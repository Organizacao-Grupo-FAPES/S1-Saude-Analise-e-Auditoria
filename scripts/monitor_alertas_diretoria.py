import os
import sys
import json
import base64
import requests
import pandas as pd
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
excel_src = os.path.join(DATA_DIR, "auditoria_consolidada.xlsx")

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
import env_loader

EMAIL = (os.getenv("JIRA_USER_EMAIL") or os.getenv("JIRA_EMAIL") or "").strip()
TOKEN = (os.getenv("JIRA_API_TOKEN") or os.getenv("JIRA_TOKEN") or "").strip()
BASE_URL = (os.getenv("JIRA_BASE_URL") or "").strip() or "https://s1saude.atlassian.net"

if not EMAIL or not TOKEN:
    print("AVISO: JIRA_USER_EMAIL ou JIRA_API_TOKEN não definidos. Alertas baseados no changelog serão limitados.")

auth_str = f"{EMAIL}:{TOKEN}"
auth_b64 = base64.b64encode(auth_str.encode('ascii')).decode('ascii')
headers = {
    "Authorization": f"Basic {auth_b64}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def parse_iso_date(date_str):
    if not date_str or pd.isna(date_str):
        return None
    try:
        cleaned = str(date_str).replace('Z', '+00:00').strip()
        if 'T' in cleaned:
            dt = datetime.fromisoformat(cleaned)
            return dt.replace(tzinfo=None)
        else:
            return datetime.strptime(cleaned[:19], "%Y-%m-%d %H:%M:%S")
    except Exception:
        try:
            return datetime.strptime(str(date_str)[:10], "%Y-%m-%d")
        except Exception:
            return None

def format_br_date(dt):
    if isinstance(dt, datetime):
        return dt.strftime("%d/%m/%Y")
    if isinstance(dt, str) and len(dt) >= 10:
        parsed = parse_iso_date(dt)
        if parsed:
            return parsed.strftime("%d/%m/%Y")
    return str(dt or "-")

def get_last_status_transition(ticket_key, target_status, default_created_str):
    """
    Busca o historico no Jira Cloud e identifica a ÚLTIMA data
    em que o ticket transitou para o status atual de pendência.
    """
    try:
        r = requests.get(f"{BASE_URL}/rest/api/3/issue/{ticket_key}?expand=changelog", headers=headers, timeout=12)
        if r.status_code == 200:
            data = r.json()
            histories = data.get("changelog", {}).get("histories", [])
            last_date = None
            last_author = "Auditoria S1"
            
            for h in histories:
                for item in h.get("items", []):
                    if item.get("field") == "status":
                        to_str = str(item.get("toString") or "").strip().upper()
                        if to_str == target_status.strip().upper():
                            last_date = parse_iso_date(h.get("created"))
                            last_author = h.get("author", {}).get("displayName", "Auditoria S1")
            
            if last_date:
                return last_date, last_author
    except Exception as e:
        print(f"Aviso ao consultar changelog de {ticket_key}: {e}")
        
    fallback_dt = parse_iso_date(default_created_str) or datetime.now()
    return fallback_dt, "Auditoria S1"

def check_critical_alerts():
    if not os.path.exists(excel_src):
        print("Arquivo de dados não encontrado:", excel_src)
        return
        
    df = pd.read_excel(excel_src)
    vidas = df[df["Tipo Item"] == "Subtarefa"].copy()
    
    aguardando_dir_raw = vidas[vidas["Status Atual"] == "AGUARDANDO DIRETORIA"].to_dict(orient="records")
    pend_cad_raw = vidas[vidas["Status Atual"] == "PENDÊNCIA CADASTRO"].to_dict(orient="records")
    
    now = datetime.now()
    
    # 1. Processar Casos de Diretoria
    itens_aguardando_diretoria = []
    for item in aguardando_dir_raw:
        chave = item.get("Chave", "")
        dt_criacao_str = str(item.get("Data Criação", ""))
        dt_entrada = parse_iso_date(dt_criacao_str)
        
        # Buscar última data de transição para AGUARDANDO DIRETORIA
        dt_pendencia, autor = get_last_status_transition(chave, "AGUARDANDO DIRETORIA", dt_criacao_str)
        dias_espera = max(0, (now - dt_pendencia).days)
        
        itens_aguardando_diretoria.append({
            "chave": chave,
            "beneficiario": item.get("Beneficiário (Nome)", "-"),
            "empresa": item.get("Empresa / Contrato", "-"),
            "vigencia": str(item.get("Vigência", "-")),
            "data_entrada": format_br_date(dt_entrada),
            "data_pendencia": format_br_date(dt_pendencia),
            "dias_espera": dias_espera,
            "tempo_espera_texto": f"+{dias_espera} dias aguardando",
            "autor_pendencia": autor,
            "acao_necessaria": "Parecer Diretoria"
        })
        
    # Ordenar por maior tempo em espera (mais críticos primeiro)
    itens_aguardando_diretoria.sort(key=lambda x: x["dias_espera"], reverse=True)
    
    # 2. Processar Casos de Pendência Cadastro
    motivos_conhecidos = {
        "AUDITORIA-899": "Documento Pendente",
        "AUDITORIA-2246": "Divergência Cadastral",
        "AUDITORIA-2259": "Comprovante de Vínculo"
    }
    
    itens_pendencia_cadastro = []
    for item in pend_cad_raw:
        chave = item.get("Chave", "")
        dt_criacao_str = str(item.get("Data Criação", ""))
        dt_entrada = parse_iso_date(dt_criacao_str)
        
        # Buscar última data de transição para PENDÊNCIA CADASTRO
        dt_pendencia, autor = get_last_status_transition(chave, "PENDÊNCIA CADASTRO", dt_criacao_str)
        dias_espera = max(0, (now - dt_pendencia).days)
        origem = motivos_conhecidos.get(chave, "Inconsistência Documental")
        
        itens_pendencia_cadastro.append({
            "chave": chave,
            "beneficiario": item.get("Beneficiário (Nome)", "-"),
            "empresa": item.get("Empresa / Contrato", "-"),
            "vigencia": str(item.get("Vigência", "-")),
            "data_entrada": format_br_date(dt_entrada),
            "data_pendencia": format_br_date(dt_pendencia),
            "dias_espera": dias_espera,
            "tempo_espera_texto": f"+{dias_espera} dias",
            "autor_pendencia": autor,
            "origem_pendencia": origem
        })
        
    # Ordenar por maior tempo em espera
    itens_pendencia_cadastro.sort(key=lambda x: x["dias_espera"], reverse=True)
    
    # 3. Lotes e Vigências em Risco
    vigencias_criticas = vidas[
        (vidas["Status Atual"] == "ANÁLISE PENDENTE") & 
        (vidas["Vigência"].str.contains("08/2026|09/2026|10/2026", na=False))
    ]
    vig_agrupada = vigencias_criticas.groupby(["Vigência", "Empresa / Contrato"]).size().reset_index(name="Vidas Pendentes")
    
    alertas_payload = {
        "data_geracao": now.strftime("%Y-%m-%d %H:%M:%S"),
        "total_aguardando_diretoria": len(itens_aguardando_diretoria),
        "itens_aguardando_diretoria": itens_aguardando_diretoria,
        "total_pendencia_cadastro": len(itens_pendencia_cadastro),
        "itens_pendencia_cadastro": itens_pendencia_cadastro,
        "total_vidas_vigencia_proxima_pendentes": len(vigencias_criticas),
        "lotes_em_risco": vig_agrupada.to_dict(orient="records")
    }
    
    out_file = os.path.join(DATA_DIR, "alertas_diretoria_hoje.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(alertas_payload, f, ensure_ascii=False, indent=2)
        
    print(f"Relatório de Alertas atualizado com sucesso em: {out_file}")
    print(f"- Itens Aguardando Diretoria: {len(itens_aguardando_diretoria)}")
    print(f"- Itens Pendência Cadastro: {len(itens_pendencia_cadastro)}")
    return alertas_payload

if __name__ == "__main__":
    check_critical_alerts()
