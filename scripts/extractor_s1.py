import os
import sys
import re
import json
import base64
import requests
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
import env_loader

EMAIL = (os.getenv("JIRA_USER_EMAIL") or os.getenv("JIRA_EMAIL") or "").strip()
TOKEN = (os.getenv("JIRA_API_TOKEN") or os.getenv("JIRA_TOKEN") or "").strip()
BASE_URL = (os.getenv("JIRA_BASE_URL") or "").strip() or "https://s1saude.atlassian.net"

if not EMAIL or not TOKEN:
    print("❌ ERRO CRÍTICO: JIRA_USER_EMAIL ou JIRA_API_TOKEN não definidos!")
    print(f"   - JIRA_USER_EMAIL presente: {'SIM' if EMAIL else 'NÃO'}")
    print(f"   - JIRA_API_TOKEN presente: {'SIM' if TOKEN else 'NÃO'}")
    print("   Configure os Secrets em: Settings -> Secrets and variables -> Actions")
    sys.exit(1)

auth_str = f"{EMAIL}:{TOKEN}"
auth_b64 = base64.b64encode(auth_str.encode('ascii')).decode('ascii')
headers = {
    "Authorization": f"Basic {auth_b64}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def parse_parent_summary(summary):
    summary = summary or ""
    empresa = summary
    vigencia = ""
    movimentacao = "INCLUSÃO"
    
    vig_match = re.search(r'VIG[EÊ]NCIA\s*[:\-]?\s*(\d{2}/\d{2}/\d{4}|\d{2}/\d{2}/\d{2})', summary, re.IGNORECASE)
    if vig_match:
        vigencia = vig_match.group(1)
        
    mov_match = re.search(r'\b(INCLUS[AÃ]O|EXCLUS[AÃ]O|CANCELAMENTO|ALTERA[CÇ][AÃ]O|MIGRA[CÇ][AÃ]O|RENOVA[CÇ][AÃ]O)\b', summary, re.IGNORECASE)
    if mov_match:
        movimentacao = mov_match.group(1).upper()
        
    emp_match = re.split(r'\s*-\s*VIG[EÊ]NCIA', summary, flags=re.IGNORECASE)
    if emp_match:
        empresa = emp_match[0].strip()
        
    return empresa, vigencia, movimentacao

def fetch_all_auditoria_issues():
    jql = "project = 'AUDITORIA' ORDER BY created DESC"
    print(f"Iniciando extração do Jira S1 Saúde: {jql}")
    
    next_page_token = None
    all_issues = []
    
    fields_to_request = [
        "summary", "status", "issuetype", "priority", "created", "updated",
        "resolutiondate", "resolution", "reporter", "assignee", "description",
        "parent", "subtasks",
        "customfield_10091", "customfield_10092", "customfield_10093",
        "customfield_10094", "customfield_10095", "customfield_10096",
        "customfield_10098", "customfield_10027", "customfield_10058"
    ]
    
    while True:
        body = {
            "jql": jql,
            "maxResults": 100,
            "fields": fields_to_request
        }
        if next_page_token:
            body["nextPageToken"] = next_page_token
            
        r = requests.post(f"{BASE_URL}/rest/api/3/search/jql", headers=headers, json=body)
        if r.status_code != 200:
            print(f"❌ Erro na requisição Jira (Status {r.status_code}): {r.text}")
            if len(all_issues) == 0:
                print(f"❌ Falha crítica ao acessar a API do Jira em: {BASE_URL}")
                print("   Verifique se as credenciais JIRA_USER_EMAIL e JIRA_API_TOKEN estão corretas.")
                sys.exit(1)
            break
            
        data = r.json()
        issues = data.get("issues", [])
        all_issues.extend(issues)
        print(f"Carregados {len(all_issues)} tickets...")
        
        is_last = data.get("isLast", True)
        next_page_token = data.get("nextPageToken")
        if is_last or not next_page_token or len(issues) == 0:
            break
            
    print(f"\nExtração concluída com sucesso! Total extraído: {len(all_issues)} tickets.")
    
    raw_file = os.path.join(DATA_DIR, "auditoria_raw.json")
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(all_issues, f, ensure_ascii=False, indent=2)
    print(f"Arquivo bruto salvo em: {raw_file}")
    
    return all_issues

def process_and_save(issues):
    records = []
    
    for iss in issues:
        key = iss.get("key", "")
        f = iss.get("fields", {})
        summary = f.get("summary", "") or ""
        issuetype = f.get("issuetype", {}).get("name", "") if f.get("issuetype") else ""
        status = f.get("status", {}).get("name", "") if f.get("status") else ""
        priority = f.get("priority", {}).get("name", "") if f.get("priority") else ""
        
        created = str(f.get("created", ""))[:19].replace('T', ' ')
        updated = str(f.get("updated", ""))[:19].replace('T', ' ')
        resolutiondate = str(f.get("resolutiondate", ""))[:19].replace('T', ' ') if f.get("resolutiondate") else ""
        resolution = f.get("resolution", {}).get("name", "") if f.get("resolution") else ""
        
        assignee_obj = f.get("assignee")
        assignee = assignee_obj.get("displayName", "Não Atribuído") if assignee_obj else "Não Atribuído"
        
        reporter_obj = f.get("reporter")
        reporter = reporter_obj.get("displayName", "Desconhecido") if reporter_obj else "Desconhecido"
        
        parent_obj = f.get("parent")
        parent_key = parent_obj.get("key", "") if parent_obj else ""
        parent_summary = parent_obj.get("fields", {}).get("summary", "") if parent_obj else ""
        parent_status = parent_obj.get("fields", {}).get("status", {}).get("name", "") if parent_obj else ""
        
        if issuetype == "Subtarefa":
            beneficiario = summary
            empresa, vigencia, movimentacao = parse_parent_summary(parent_summary)
            tipo_registro = "Beneficiário (Vida)"
        else:
            beneficiario = "-"
            empresa, vigencia, movimentacao = parse_parent_summary(summary)
            tipo_registro = "Lote / Demanda Principal"
            
        cpt_raw = f.get("customfield_10092") or f.get("customfield_10091")
        if isinstance(cpt_raw, dict):
            analise_cpt = cpt_raw.get("value", "")
        elif isinstance(cpt_raw, list) and len(cpt_raw) > 0 and isinstance(cpt_raw[0], dict):
            analise_cpt = cpt_raw[0].get("value", "")
        else:
            analise_cpt = str(cpt_raw or "")
            
        benef_tipo_raw = f.get("customfield_10096")
        if isinstance(benef_tipo_raw, dict):
            tipo_beneficiario = benef_tipo_raw.get("value", "")
        else:
            tipo_beneficiario = str(benef_tipo_raw or "Titular")
            
        aps_raw = f.get("customfield_10093") or f.get("customfield_10094")
        if isinstance(aps_raw, dict):
            acompanhamento_aps = aps_raw.get("value", "")
        else:
            acompanhamento_aps = str(aps_raw or "")
            
        caminho_arquivo = str(f.get("customfield_10098") or "")
        
        records.append({
            "Chave": key,
            "Tipo Registro": tipo_registro,
            "Tipo Item": issuetype,
            "Beneficiário (Nome)": beneficiario,
            "Empresa / Contrato": empresa,
            "Vigência": vigencia,
            "Tipo Movimentação": movimentacao,
            "Status Atual": status,
            "Prioridade": priority,
            "Responsável": assignee,
            "Relator": reporter,
            "Tipo Beneficiário": tipo_beneficiario,
            "Análise CPT": analise_cpt,
            "Acompanhamento APS": acompanhamento_aps,
            "Chave Lote (Parent)": parent_key,
            "Resumo Lote (Parent)": parent_summary,
            "Status Lote": parent_status,
            "Data Criação": created,
            "Data Atualização": updated,
            "Data Resolução": resolutiondate,
            "Resolução": resolution,
            "Caminho do Arquivo": caminho_arquivo
        })
        
    df = pd.DataFrame(records)
    
    excel_path = os.path.join(DATA_DIR, "auditoria_consolidada.xlsx")
    df.to_excel(excel_path, index=False)
    print(f"Planilha consolidada salva em: {excel_path} ({len(df)} registros)")
    
    return df

if __name__ == "__main__":
    issues = fetch_all_auditoria_issues()
    df = process_and_save(issues)
    print("Processamento concluído com sucesso!")
