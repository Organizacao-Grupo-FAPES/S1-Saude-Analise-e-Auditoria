import os
import sys
import json
import base64
import requests
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
import env_loader

EMAIL = os.getenv("JIRA_USER_EMAIL", os.getenv("JIRA_EMAIL", ""))
TOKEN = os.getenv("JIRA_API_TOKEN", os.getenv("JIRA_TOKEN", ""))
BASE_URL = os.getenv("JIRA_BASE_URL", "https://s1saude.atlassian.net")

if not EMAIL or not TOKEN:
    print("AVISO: JIRA_USER_EMAIL ou JIRA_API_TOKEN não definidos no .env ou Secrets.")

auth_str = f"{EMAIL}:{TOKEN}"
auth_b64 = base64.b64encode(auth_str.encode('ascii')).decode('ascii')
headers = {
    "Authorization": f"Basic {auth_b64}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def extract_changelog_interactions():
    print("Buscando histórico de interações e changelogs da equipe no Jira...")
    out_file = os.path.join(DATA_DIR, "interacoes_usuarios.json")
    
    # Carregar interações existentes como baseline
    user_interactions = Counter()
    transition_history = []
    if os.path.exists(out_file):
        try:
            with open(out_file, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                user_interactions.update(old_data.get("user_interactions", {}))
                transition_history = old_data.get("transitions", [])
        except Exception:
            pass

    # Buscar os 50 tickets mais recentes movimentados
    jql = "project = 'AUDITORIA' AND status not in ('ANÁLISE PENDENTE') ORDER BY updated DESC"
    body = {
        "jql": jql,
        "maxResults": 50,
        "fields": ["summary", "status", "assignee", "updated"]
    }

    r = requests.post(f"{BASE_URL}/rest/api/3/search/jql", headers=headers, json=body)
    if r.status_code == 200:
        issues = r.json().get("issues", [])
        print(f"Analisando changelogs de {len(issues)} tickets ativos...")
        for iss in issues:
            k = iss.get("key")
            summary = iss.get("fields", {}).get("summary", "")
            
            cr = requests.get(f"{BASE_URL}/rest/api/3/issue/{k}/changelog", headers=headers)
            if cr.status_code == 200:
                histories = cr.json().get("values", [])
                for h in histories:
                    author = h.get("author", {}).get("displayName", "Desconhecido")
                    created_h = h.get("created", "")
                    for it in h.get("items", []):
                        field_changed = it.get("field")
                        from_str = it.get("fromString")
                        to_str = it.get("toString")

                        user_interactions[author] += 1

                        if field_changed == "status":
                            transition_history.append({
                                "ticket": k,
                                "beneficiario": summary,
                                "autor": author,
                                "de_status": from_str,
                                "para_status": to_str,
                                "data": created_h[:19].replace('T', ' ') if created_h else ""
                            })

    # Deduplicar histórico de transições
    seen = set()
    unique_transitions = []
    for t in transition_history:
        chave_t = f"{t.get('ticket')}_{t.get('data')}_{t.get('para_status')}"
        if chave_t not in seen:
            seen.add(chave_t)
            unique_transitions.append(t)

    interaction_data = {
        "user_interactions": dict(user_interactions),
        "transitions": unique_transitions[:300]
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(interaction_data, f, ensure_ascii=False, indent=2)

    print(f"Arquivo de interações atualizado com sucesso em: {out_file}")
    return interaction_data

if __name__ == "__main__":
    extract_changelog_interactions()
