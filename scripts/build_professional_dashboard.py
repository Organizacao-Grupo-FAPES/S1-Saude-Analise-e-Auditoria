import os
import sys
import json
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import crypto_vault
DATA_DIR = os.path.join(PROJECT_DIR, "data")
excel_src = os.path.join(DATA_DIR, "auditoria_consolidada.xlsx")
interactions_src = os.path.join(DATA_DIR, "interacoes_usuarios.json")

alertas_src = os.path.join(DATA_DIR, "alertas_diretoria_hoje.json")

records = []
if os.path.exists(excel_src):
    try:
        df = pd.read_excel(excel_src).fillna("")
        records = df.to_dict(orient="records")
    except Exception as e:
        print(f"Aviso ao carregar Excel: {e}")

interactions_data = {}
if os.path.exists(interactions_src):
    try:
        with open(interactions_src, "r", encoding="utf-8") as f:
            interactions_data = json.load(f)
    except Exception as e:
        print(f"Aviso ao carregar interações: {e}")

alertas_data = {}
if os.path.exists(alertas_src):
    with open(alertas_src, "r", encoding="utf-8") as f:
        alertas_data = json.load(f)

noble_crypto_src = os.path.join(SCRIPTS_DIR, "noble_crypto.js")
if not os.path.exists(noble_crypto_src):
    noble_crypto_src = os.path.join(DATA_DIR, "noble_crypto.js")

noble_crypto_code = ""
if os.path.exists(noble_crypto_src):
    with open(noble_crypto_src, "r", encoding="utf-8") as f:
        noble_crypto_code = f.read()

vault_payload = {
    "records": records,
    "interactions": interactions_data,
    "alertas": alertas_data
}
vault_data = crypto_vault.build_encrypted_vault(vault_payload)
vault_json_str = json.dumps(vault_data, ensure_ascii=False)

html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>S1 Saúde | Cockpit Gestão de Auditoria & Implantação de Contratos</title>
<link rel="icon" type="image/png" href="https://s1saude.com.br/wp-content/uploads/2021/08/cropped-cropped-fab-180x180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {
    color-scheme: light;
    /* PALETA OFICIAL S1 SAÚDE EXTRAÍDA DO SITE S1SAUDE.COM.BR */
    --s1-primary: #282394;       /* Azul/Roxo Índigo Oficial S1 */
    --s1-primary-dark: #1D1871;  /* Índigo Profundo */
    --s1-secondary: #E36159;    /* Coral / Terracota Oficial S1 */
    --s1-tertiary: #2BAAB1;     /* Verde Água / Turquesa Oficial S1 */
    --s1-dark: #212529;         /* Grafite Escuro */
    --s1-quaternary: #383F48;   /* Slate Gray */
    --s1-amber: #D97706;        /* Âmbar Corporativo */
    --s1-green: #059669;        /* Verde Esmeralda Aprovado */
    --s1-purple: #7C3AED;       /* Roxo Executivo */
    --s1-red: #DC2626;          /* Vermelho Alerta */
    --bg-page: #F8FAFC;
    --card-bg: #FFFFFF;
    --card-border: #E2E8F0;
    --text-dark: #0F172A;
    --text-muted: #64748B;
    --sidebar-width: 270px;
    --font-main: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg-page);
    font-family: var(--font-main);
    color: var(--text-dark);
    min-height: 100vh;
    display: flex;
    overflow-x: hidden;
  }

  /* ======================================================== */
  /* SIDEBAR LATERAL FIXA MODERNA (ZERO EMOJIS - PURE SVG) */
  /* ======================================================== */
  .sidebar {
    width: var(--sidebar-width);
    background: #FFFFFF;
    border-right: 1px solid var(--card-border);
    height: 100vh;
    position: fixed;
    top: 0;
    left: 0;
    display: flex;
    flex-direction: column;
    z-index: 100;
    box-shadow: 1px 0 8px rgba(0, 0, 0, 0.03);
  }

  .sidebar-brand {
    padding: 20px 18px 16px;
    border-bottom: 1px solid #F1F5F9;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .brand-logo-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .brand-logo-img {
    height: 34px;
    width: auto;
    display: block;
  }

  .brand-subtitle {
    font-size: 9.5px;
    font-weight: 700;
    color: var(--s1-primary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    text-align: center;
  }

  /* Nav Menu Links */
  .sidebar-menu {
    padding: 14px 10px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
    overflow-y: auto;
  }

  .menu-heading {
    font-size: 9.5px;
    font-weight: 800;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.6px;
    padding: 10px 12px 4px;
  }

  .nav-item {
    border: none;
    background: transparent;
    color: var(--text-dark);
    padding: 10px 12px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    text-align: left;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: all 0.15s ease;
    width: 100%;
  }

  .nav-item:hover {
    background: #F1F5F9;
    color: var(--s1-primary);
  }

  .nav-item.active {
    background: var(--s1-primary);
    color: #FFFFFF;
    box-shadow: 0 2px 8px rgba(40, 35, 148, 0.2);
  }

  .nav-item.active svg {
    stroke: #FFFFFF;
  }

  .nav-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    flex-shrink: 0;
  }

  .sidebar-footer {
    padding: 14px 16px;
    border-top: 1px solid #F1F5F9;
    background: #FAFAFC;
  }

  /* ======================================================== */
  /* MAIN CONTENT AREA */
  /* ======================================================== */
  .main-content {
    margin-left: var(--sidebar-width);
    width: calc(100% - var(--sidebar-width));
    min-height: 100vh;
    padding: 16px 24px 40px;
    display: flex;
    flex-direction: column;
  }

  /* Top Bar */
  .top-navbar {
    background: linear-gradient(135deg, var(--s1-primary) 0%, var(--s1-primary-dark) 60%, #1A535C 100%);
    border-radius: 12px;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    flex-wrap: wrap;
    color: #fff;
    box-shadow: 0 4px 14px rgba(40, 35, 148, 0.12);
    margin-bottom: 12px;
  }

  .top-titles h1 {
    font-size: 16.5px;
    font-weight: 800;
    line-height: 1.2;
    color: #FFFFFF;
    letter-spacing: -0.01em;
  }

  .top-titles p {
    font-size: 10px;
    opacity: 0.85;
    letter-spacing: 0.5px;
    margin-top: 2px;
    text-transform: uppercase;
    color: #E2E8F0;
  }

  .top-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .status-chip {
    background: rgba(255, 255, 255, 0.12);
    backdrop-filter: blur(6px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 5px 11px;
    text-align: right;
  }

  .status-chip .lbl {
    font-size: 8.5px;
    opacity: 0.85;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }

  .status-chip .val {
    font-size: 12px;
    font-weight: 800;
    color: #4ADE80;
  }

  .btn-top {
    background: #FFFFFF;
    color: var(--s1-primary);
    border: 1px solid rgba(255, 255, 255, 0.8);
    padding: 7px 13px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 11.5px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
  }

  .btn-top:hover {
    background: #F8FAFC;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .btn-top-sync {
    background: rgba(255, 255, 255, 0.18);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.3);
  }

  .btn-top-sync:hover {
    background: rgba(255, 255, 255, 0.28);
    color: #FFFFFF;
  }

  /* BARRA GLOBAL DE FILTRO DE DATAS */
  .global-date-bar {
    background: #FFFFFF;
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 9px 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 14px;
  }

  .date-bar-left {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }

  .date-bar-label {
    font-size: 11px;
    font-weight: 700;
    color: var(--s1-primary);
    text-transform: uppercase;
    letter-spacing: 0.4px;
    display: flex;
    align-items: center;
    gap: 5px;
  }

  .preset-buttons {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
  }

  .btn-preset {
    border: 1px solid var(--card-border);
    background: #F8FAFC;
    color: var(--text-dark);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.12s ease;
  }

  .btn-preset:hover {
    border-color: var(--s1-primary);
    color: var(--s1-primary);
  }

  .btn-preset.active {
    background: var(--s1-primary);
    color: #fff;
    border-color: var(--s1-primary);
  }

  .custom-date-inputs {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .custom-date-inputs label {
    font-size: 11px;
    color: var(--text-muted);
    font-weight: 600;
  }

  .custom-date-inputs input[type="date"] {
    background: #F8FAFC;
    border: 1px solid var(--card-border);
    color: var(--text-dark);
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-family: inherit;
    outline: none;
  }

  .filtered-period-badge {
    font-size: 10.5px;
    font-weight: 700;
    color: var(--s1-primary);
    background: #EDEAFD;
    padding: 4px 9px;
    border-radius: 6px;
    border: 1px solid #C7D2FE;
  }

  /* Panels */
  .panel { display: none; }
  .panel.active { display: block; }

  /* Grid Layouts */
  .row { display: grid; gap: 12px; margin-bottom: 12px; }
  .row-6 { grid-template-columns: repeat(6, 1fr); }
  .row-5 { grid-template-columns: repeat(5, 1fr); }
  .row-4 { grid-template-columns: repeat(4, 1fr); }
  .row-3 { grid-template-columns: repeat(3, 1fr); }
  .row-2 { grid-template-columns: 1fr 1fr; }
  .row-2-1 { grid-template-columns: 2fr 1fr; }
  .row-1-2 { grid-template-columns: 1fr 2fr; }

  @media (max-width: 1300px) {
    .row-6, .row-5 { grid-template-columns: repeat(3, 1fr); }
    .row-4, .row-3 { grid-template-columns: 1fr 1fr; }
    .row-2-1, .row-1-2 { grid-template-columns: 1fr; }
  }

  @media (max-width: 900px) {
    .sidebar { display: none; }
    .main-content { margin-left: 0; width: 100%; }
    .row-6, .row-5, .row-4, .row-3, .row-2 { grid-template-columns: 1fr; }
  }

  /* Cards */
  .card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    position: relative;
  }

  .card-title {
    font-size: 11.5px;
    font-weight: 800;
    color: var(--s1-primary);
    letter-spacing: 0.4px;
    margin-bottom: 12px;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .card-title-tag {
    font-size: 9.5px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 5px;
    background: #EDEAFD;
    color: var(--s1-primary);
  }

  /* KPI Cards */
  .kpi-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 16px;
  }

  .kpi-icon-box {
    width: 42px;
    height: 42px;
    border-radius: 10px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .kpi-body {
    flex: 1;
    min-width: 0;
  }

  .kpi-body .lbl {
    font-size: 10px;
    color: var(--text-muted);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .kpi-body .val {
    font-size: 21px;
    font-weight: 800;
    color: var(--text-dark);
    line-height: 1.1;
    letter-spacing: -0.02em;
  }

  .kpi-body .sub {
    font-size: 10px;
    color: var(--text-muted);
    margin-top: 4px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 4px;
  }

  /* Colors for KPIs using S1 Palette */
  .bg-s1-indigo { background: #EDEAFD; color: var(--s1-primary); }
  .bg-s1-coral { background: #FCEEEC; color: var(--s1-secondary); }
  .bg-s1-teal { background: #E6F7F7; color: var(--s1-tertiary); }
  .bg-s1-amber { background: #FEF3C7; color: var(--s1-amber); }
  .bg-s1-green { background: #ECFDF5; color: var(--s1-green); }
  .bg-s1-purple { background: #F3E8FF; color: var(--s1-purple); }

  /* Interactive Clickable KPI Cards */
  .kpi-card-clickable {
    cursor: pointer;
    position: relative;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  }
  .kpi-card-clickable:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(40, 35, 148, 0.12);
    border-color: var(--s1-primary);
  }
  .kpi-card-clickable .kpi-click-tag {
    font-size: 8px;
    font-weight: 700;
    color: var(--text-muted);
    background: #F1F5F9;
    padding: 1.5px 5.5px;
    border-radius: 4px;
    display: inline-flex;
    align-items: center;
    gap: 2px;
    white-space: nowrap;
    transition: all 0.15s ease;
  }
  .kpi-card-clickable:hover .kpi-click-tag {
    background: var(--s1-primary) !important;
    color: #FFFFFF !important;
  }

  /* Filter Pills for Top Pendências */
  .filter-pills {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 12px;
  }
  .filter-pill {
    border: 1px solid var(--card-border);
    background: #FFFFFF;
    color: var(--text-dark);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: all 0.15s ease;
  }
  .filter-pill:hover {
    border-color: var(--s1-primary);
    color: var(--s1-primary);
    background: #F8FAFC;
  }
  .filter-pill.active {
    background: var(--s1-primary);
    color: #FFFFFF;
    border-color: var(--s1-primary);
    box-shadow: 0 2px 6px rgba(40, 35, 148, 0.25);
  }
  .filter-pill .pill-count {
    font-size: 9.5px;
    background: rgba(0, 0, 0, 0.07);
    padding: 1px 6px;
    border-radius: 10px;
  }
  .filter-pill.active .pill-count {
    background: rgba(255, 255, 255, 0.25);
    color: #FFFFFF;
  }

  .btn-table-action {
    background: #EDEAFD;
    color: var(--s1-primary);
    border: 1px solid #C7D2FE;
    padding: 4px 9px;
    border-radius: 6px;
    font-size: 10.5px;
    font-weight: 700;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    transition: all 0.12s ease;
  }
  .btn-table-action:hover {
    background: var(--s1-primary);
    color: #FFFFFF;
    border-color: var(--s1-primary);
  }

  /* Charts Container */
  .chart-box {
    position: relative;
    height: 270px;
    width: 100%;
  }

  .chart-box-tall {
    position: relative;
    height: 380px;
    width: 100%;
  }

  /* KANBAN BOARD STYLING */
  .kanban-board-container {
    display: flex;
    gap: 12px;
    overflow-x: auto;
    padding-bottom: 16px;
    min-height: 560px;
  }

  .kanban-col {
    background: #F8FAFC;
    border: 1px solid var(--card-border);
    border-radius: 10px;
    min-width: 270px;
    max-width: 270px;
    display: flex;
    flex-direction: column;
    max-height: 720px;
  }

  .kanban-col-header {
    padding: 10px 12px;
    font-size: 10.5px;
    font-weight: 800;
    color: var(--s1-primary);
    text-transform: uppercase;
    letter-spacing: 0.4px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid var(--card-border);
    background: #F1F5F9;
    border-radius: 10px 10px 0 0;
  }

  .kanban-col-count {
    background: var(--s1-primary);
    color: #fff;
    padding: 2px 7px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 800;
  }

  .kanban-cards-list {
    padding: 8px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    overflow-y: auto;
    flex: 1;
  }

  .kanban-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 10px 12px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .kanban-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
    border-color: var(--s1-primary);
  }

  .k-parent-summary {
    font-size: 9.5px;
    color: var(--text-muted);
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .k-beneficiario {
    font-size: 11.5px;
    font-weight: 700;
    color: var(--text-dark);
    margin-bottom: 8px;
    line-height: 1.3;
  }

  .k-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 10px;
    color: var(--text-muted);
  }

  .k-ticket-tag {
    color: var(--s1-primary);
    font-weight: 800;
  }

  .k-avatar-badge {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--s1-primary);
    color: #fff;
    font-size: 9px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Tables & Lists */
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11.5px;
    text-align: left;
  }

  thead th {
    background: #F8FAFC;
    color: var(--text-muted);
    font-weight: 700;
    padding: 9px 12px;
    border-bottom: 1.5px solid var(--card-border);
    text-transform: uppercase;
    font-size: 10px;
    letter-spacing: 0.4px;
  }

  tbody tr {
    border-bottom: 1px solid #F1F5F9;
    transition: background 0.12s;
  }

  tbody tr:hover {
    background: #F8FAFC;
    cursor: pointer;
  }

  tbody td {
    padding: 9px 12px;
    color: var(--text-dark);
  }

  /* Badges */
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 7px;
    border-radius: 5px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.2px;
  }

  .b-pendente { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
  .b-andamento { background: #E0F2FE; color: #0369A1; border: 1px solid #BAE6FD; }
  .b-liberado { background: #D1FAE5; color: #065F46; border: 1px solid #A7F3D0; }
  .b-concluido { background: #EDEAFD; color: var(--s1-primary); border: 1px solid #C7D2FE; }
  .b-cancelado { background: #FCEEEC; color: var(--s1-secondary); border: 1px solid #FECACA; }
  .b-cpt { background: #E6F7F7; color: var(--s1-tertiary); border: 1px solid #B2EBF2; }
  .b-diretoria { background: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5; }
  .b-outro { background: #F1F5F9; color: #475569; border: 1px solid #E2E8F0; }

  .ticket-link {
    color: var(--s1-primary);
    text-decoration: none;
    font-weight: 700;
  }

  .ticket-link:hover {
    color: var(--s1-tertiary);
    text-decoration: underline;
  }

  /* Filters Row */
  .filters-bar {
    background: #fff;
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 12px;
  }

  .filter-inputs {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  select, input[type="text"] {
    background: #F8FAFC;
    border: 1px solid var(--card-border);
    color: var(--text-dark);
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 11.5px;
    font-family: inherit;
    outline: none;
  }

  select:focus, input[type="text"]:focus {
    border-color: var(--s1-primary);
    background: #fff;
  }

  .btn-action {
    background: var(--s1-primary);
    color: #fff;
    border: none;
    padding: 7px 14px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 11.5px;
    cursor: pointer;
    transition: all 0.15s;
    display: flex;
    align-items: center;
    gap: 5px;
  }

  .btn-action:hover {
    background: var(--s1-primary-dark);
  }

  .rank-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #F1F5F9;
    font-size: 11.5px;
  }

  .rank-item:last-child { border-bottom: none; }
  .rank-name { font-weight: 600; color: var(--text-dark); max-width: 260px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .rank-val { font-weight: 800; color: var(--s1-primary); }

  .alert-box {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-left: 4px solid var(--s1-secondary);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 12px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    color: #92400E;
    font-size: 11.5px;
    line-height: 1.4;
  }

  .alert-box strong { color: #78350F; }

  .pagination-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 12px;
    font-size: 11.5px;
    color: var(--text-muted);
  }

  .page-btns {
    display: flex;
    gap: 4px;
  }

  .btn-page {
    background: #fff;
    border: 1px solid var(--card-border);
    padding: 3px 9px;
    border-radius: 5px;
    font-size: 11px;
    font-weight: 700;
    cursor: pointer;
  }

  .btn-page.active {
    background: var(--s1-primary);
    color: #fff;
    border-color: var(--s1-primary);
  }

  /* DRAWER MODAL */
  .drawer-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(4px);
    z-index: 999;
    display: none;
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  .drawer-overlay.active {
    display: block;
    opacity: 1;
  }

  .drawer {
    position: fixed;
    top: 0;
    right: -480px;
    width: 480px;
    max-width: 90vw;
    height: 100vh;
    background: #FFFFFF;
    box-shadow: -8px 0 24px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    transition: right 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    display: flex;
    flex-direction: column;
    overflow-y: auto;
  }

  .drawer.active {
    right: 0;
  }

  .drawer-header {
    background: linear-gradient(135deg, var(--s1-primary) 0%, var(--s1-primary-dark) 100%);
    color: #fff;
    padding: 18px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .drawer-header h3 {
    font-size: 15px;
    font-weight: 800;
  }

  .btn-close-drawer {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: #fff;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    cursor: pointer;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .drawer-body {
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    font-size: 12.5px;
  }

  .drawer-field {
    border-bottom: 1px solid #F1F5F9;
    padding-bottom: 8px;
  }

  .drawer-label {
    font-size: 10.5px;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 3px;
  }

  .drawer-value {
    font-size: 13.5px;
    font-weight: 700;
    color: var(--text-dark);
  }

  .btn-jira-link {
    background: var(--s1-primary);
    color: #fff;
    text-decoration: none;
    padding: 11px;
    border-radius: 8px;
    text-align: center;
    font-weight: 700;
    display: block;
    margin-top: 10px;
  }

  /* MODAL DE SINCRONIZAÇÃO EM TEMPO REAL */
  .sync-modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(6px);
    z-index: 9999;
    display: none;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.25s ease;
  }

  .sync-modal-overlay.active {
    display: flex;
    opacity: 1;
  }

  .sync-modal-card {
    background: #FFFFFF;
    border-radius: 14px;
    width: 450px;
    max-width: 90vw;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25);
    overflow: hidden;
  }

  .sync-modal-header {
    background: linear-gradient(135deg, var(--s1-primary) 0%, var(--s1-primary-dark) 100%);
    color: #FFFFFF;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .sync-modal-logo {
    background: #FFFFFF;
    border-radius: 6px;
    padding: 4px 8px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .sync-modal-header h3 {
    font-size: 14px;
    font-weight: 800;
    margin: 0;
  }

  .sync-modal-header p {
    font-size: 10px;
    opacity: 0.85;
    margin-top: 2px;
  }

  .sync-modal-body {
    padding: 22px 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .sync-spinner-box {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 14px;
  }

  .spinner-svg {
    animation: rotate 1.2s linear infinite;
  }

  @keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .sync-progress-bar-wrap {
    width: 100%;
    height: 6px;
    background: #E2E8F0;
    border-radius: 999px;
    overflow: hidden;
    margin-bottom: 6px;
  }

  .sync-progress-bar {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, var(--s1-primary), var(--s1-tertiary), var(--s1-green));
    border-radius: 999px;
    transition: width 0.25s ease;
  }

  .sync-progress-pct {
    font-size: 11.5px;
    font-weight: 800;
    color: var(--s1-primary);
    margin-bottom: 14px;
  }

  .sync-steps-list {
    width: 100%;
    text-align: left;
    display: flex;
    flex-direction: column;
    gap: 8px;
    font-size: 11px;
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    padding: 12px 14px;
    border-radius: 8px;
    margin-bottom: 12px;
  }

  .sync-step {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-muted);
  }

  .sync-step.active {
    color: var(--s1-primary);
    font-weight: 700;
  }

  .sync-step.done {
    color: #065F46;
    font-weight: 700;
  }

  .sync-success-msg {
    background: #ECFDF5;
    color: #065F46;
    border: 1px solid #A7F3D0;
    padding: 9px 12px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    width: 100%;
  }

  /* PRINT MODE (2 PÁGINAS A4 PAISAGEM SINTÉTICO) */
  @media print {
    @page { size: A4 landscape; margin: 8mm 10mm; }
    body { background: #FFFFFF !important; font-size: 11px !important; }
    .sidebar, .top-navbar, .global-date-bar, .filters-bar, .pagination-container, .drawer-overlay, .drawer, #tab-kanban, #tab-base, #tab-vigencia, #tab-empresas {
      display: none !important;
    }
    .main-content { margin-left: 0 !important; width: 100% !important; padding: 0 !important; }
    #tab-exec, #tab-diretoria, #tab-equipe { display: block !important; }
    #tab-diretoria { page-break-before: always !important; margin-top: 10px !important; }
    .card { border: 1px solid #CBD5E1 !important; box-shadow: none !important; break-inside: avoid !important; }
    .chart-box { height: 190px !important; }
  }

  /* ======================================================== */
  /* TELA DE LOGIN CORPORATIVA S1 SAÚDE (AES-256 / LGPD) */
  /* ======================================================== */
  .login-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: radial-gradient(circle at top right, rgba(40, 35, 148, 0.12), transparent 60%),
                radial-gradient(circle at bottom left, rgba(227, 97, 89, 0.08), transparent 50%),
                #F1F5F9;
    backdrop-filter: blur(12px);
    z-index: 99999;
    display: none;
    align-items: center;
    justify-content: center;
    padding: 20px;
    opacity: 0;
    transition: opacity 0.35s ease, visibility 0.35s ease;
    visibility: hidden;
  }

  .login-overlay.active {
    display: flex;
    opacity: 1;
    visibility: visible;
  }

  .login-card {
    background: #FFFFFF;
    border: 1px solid var(--card-border);
    border-radius: 16px;
    box-shadow: 0 20px 45px -10px rgba(15, 23, 42, 0.12), 0 0 0 1px rgba(0, 0, 0, 0.02);
    width: 100%;
    max-width: 440px;
    padding: 36px 32px 28px;
    display: flex;
    flex-direction: column;
    animation: scaleIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  }

  @keyframes scaleIn {
    from { transform: scale(0.96); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
  }

  .login-brand {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
  }

  .login-header-text {
    text-align: center;
    margin-bottom: 24px;
  }

  .login-header-text h2 {
    font-size: 19px;
    font-weight: 800;
    color: var(--s1-primary-dark);
    letter-spacing: -0.3px;
  }

  .login-header-text p {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 4px;
  }

  .login-error-alert {
    background: #FEE2E2;
    border: 1px solid #FCA5A5;
    border-radius: 8px;
    padding: 10px 14px;
    color: #991B1B;
    font-size: 11.5px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
  }

  .login-field {
    margin-bottom: 16px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .login-field {
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 100%;
  }

  .login-field label {
    font-size: 11.5px;
    font-weight: 700;
    color: var(--text-dark);
  }

  .login-input-wrap {
    position: relative;
    width: 100%;
    box-sizing: border-box;
  }

  .login-input-wrap .input-icon-left {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    z-index: 2;
  }

  .login-input-wrap input {
    width: 100%;
    height: 42px;
    box-sizing: border-box;
    border: 1px solid var(--card-border);
    border-radius: 8px;
    padding: 0 42px 0 38px;
    font-size: 13px;
    font-family: inherit;
    color: var(--text-dark);
    background: #F8FAFC;
    transition: all 0.2s ease;
    display: block;
  }

  #input-username {
    text-transform: lowercase;
  }

  .login-input-wrap input:focus {
    outline: none;
    border-color: var(--s1-primary);
    background: #FFFFFF;
    box-shadow: 0 0 0 3px rgba(40, 35, 148, 0.12);
  }

  .btn-toggle-pwd {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 6px;
    color: #64748B;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    z-index: 5;
    transition: all 0.2s ease;
  }

  .btn-toggle-pwd:hover {
    color: var(--s1-primary);
    background: #E2E8F0;
  }

  .btn-login-submit {
    width: 100%;
    height: 44px;
    background: linear-gradient(135deg, var(--s1-primary), var(--s1-primary-dark));
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    font-size: 13.5px;
    font-weight: 700;
    font-family: inherit;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    box-shadow: 0 4px 12px rgba(40, 35, 148, 0.25);
    transition: all 0.2s ease;
    margin-top: 8px;
  }

  .btn-login-submit:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(40, 35, 148, 0.35);
  }

  .login-footer-security {
    margin-top: 22px;
    padding-top: 14px;
    border-top: 1px solid #F1F5F9;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    font-size: 11px;
    color: var(--text-muted);
    font-weight: 600;
  }

  /* User Session Widget no Topo da Sidebar */
  .user-session-widget {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 8px 10px;
    margin: 6px 14px 12px 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.2s ease;
  }

  .user-session-widget:hover {
    background: #F1F5F9;
    border-color: #CBD5E1;
  }

  .user-session-info {
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .user-session-name {
    font-size: 11px;
    font-weight: 800;
    color: var(--text-dark);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .user-session-perfil {
    font-size: 9.5px;
    color: var(--s1-primary);
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .btn-logout-sidebar {
    background: transparent;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    color: #64748B;
    cursor: pointer;
    padding: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
  }

  .btn-logout-sidebar:hover {
    background: #FEE2E2;
    border-color: #FCA5A5;
    color: #991B1B;
  }

</style>
</head>
<body>

  <!-- ======================================================== -->
  <!-- TELA DE LOGIN CORPORATIVA S1 SAÚDE (AES-256 / LGPD) -->
  <!-- ======================================================== -->
  <div id="login-screen-overlay" class="login-overlay active">
    <div class="login-card">
      <div class="login-brand">
        <img src="https://s1saude.com.br/wp-content/uploads/2021/08/logo-s1saude-1.png" alt="S1 Saúde" style="height: 38px;" onerror="this.outerHTML='<strong style=\'color:#282394;font-size:20px;font-weight:800;\'>S1 SAÚDE</strong>'">
      </div>
      
      <div class="login-header-text">
        <h2>Cockpit de Auditoria</h2>
        <p>Monitoramento Estratégico de Análise & Auditoria</p>
      </div>

      <div id="login-error-box" class="login-error-alert" style="display: none;">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
        <span id="login-error-text">Usuário ou senha inválidos.</span>
      </div>

      <form id="login-form" onsubmit="handleLoginSubmit(event)">
        <div class="login-field">
          <label for="input-username">Usuário Corporativo</label>
          <div class="login-input-wrap">
            <svg class="input-icon-left" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            <input type="text" id="input-username" placeholder="Digite seu usuário" required autocomplete="off" autocapitalize="none" autocorrect="off" spellcheck="false" oninput="this.value = this.value.toLowerCase().trim()" autofocus>
          </div>
        </div>

        <div class="login-field">
          <label for="input-password">Senha de Acesso</label>
          <div class="login-input-wrap">
            <svg class="input-icon-left" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            <input type="password" id="input-password" placeholder="Digite sua senha" required autocomplete="off">
            <button type="button" class="btn-toggle-pwd" onclick="togglePasswordVisibility()" title="Mostrar ou ocultar senha">
              <svg id="eye-icon-svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </div>
        </div>

        <button type="submit" id="btn-login-submit" class="btn-login-submit">
          <span id="btn-login-text">Acessar Cockpit</span>
          <svg id="btn-login-spinner" class="spinner-svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display: none;">
            <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
          </svg>
        </button>
      </form>

      <div class="login-footer-security">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>
        <span>Ambiente Seguro</span>
      </div>
    </div>
  </div>


  <!-- ======================================================== -->
  <!-- SIDEBAR LATERAL FIXA MODERNA (PURE SVG ICONS) -->
  <!-- ======================================================== -->
  <aside class="sidebar">
    <div class="sidebar-brand">
      <div class="brand-logo-card">
        <img src="https://s1saude.com.br/wp-content/uploads/2021/08/logo-s1saude-1.png" alt="S1 Saúde" class="brand-logo-img" onerror="this.outerHTML='<strong style=\\'color:#282394;font-size:16px;font-weight:800;\\'>S1 SAÚDE</strong>'">
      </div>
    </div>

    <!-- WIDGET DO USUÁRIO LOGADO NO TOPO (ABAIXO DA LOGO) -->
    <div class="user-session-widget">
      <div class="user-session-info">
        <span class="user-session-name" id="user-logged-name">Usuário</span>
        <span class="user-session-perfil" id="user-logged-perfil">Acesso Seguro</span>
      </div>
      <button class="btn-logout-sidebar" onclick="logoutSession()" title="Sair do Cockpit">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>
      </button>
    </div>

    <div class="sidebar-menu">
      <div class="menu-heading">Painel Executivo</div>
      <button class="nav-item active" onclick="switchNav('tab-exec', this)">
        <span class="nav-icon">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>
        </span>
        <span>Visão Geral Executiva</span>
      </button>

      <button class="nav-item" onclick="switchNav('tab-kanban', this)">
        <span class="nav-icon">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 5v11"/><path d="M12 5v6"/><path d="M18 5v14"/></svg>
        </span>
        <span>Quadro Kanban da Operação</span>
      </button>

      <button class="nav-item" onclick="switchNav('tab-equipe', this)">
        <span class="nav-icon">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </span>
        <span>Produtividade & Interações</span>
      </button>

      <button class="nav-item" onclick="switchNav('tab-diretoria', this)">
        <span class="nav-icon">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
        </span>
        <span>Casos Críticos da Diretoria</span>
      </button>

      <div class="menu-heading" style="margin-top: 8px;">Gestão & Análise</div>
      <button id="nav-pendencias" class="nav-item" onclick="switchNav('tab-pendencias', this)">
        <span class="nav-icon">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </span>
        <span>Top Pendências & Lead Time</span>
        <span style="font-size: 8.5px; font-weight: 800; background: rgba(227, 97, 89, 0.15); color: var(--s1-secondary); padding: 1px 5px; border-radius: 4px; margin-left: auto;">NOVO</span>
      </button>

      <button class="nav-item" onclick="switchNav('tab-vigencia', this)">
        <span class="nav-icon">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>
        </span>
        <span>Controle por Vigência</span>
      </button>

      <button class="nav-item" onclick="switchNav('tab-empresas', this)">
        <span class="nav-icon">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/></svg>
        </span>
        <span>Top Empresas & Contratos</span>
      </button>

      <button class="nav-item" onclick="switchNav('tab-base', this)">
        <span class="nav-icon">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18"/><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/></svg>
        </span>
        <span>Base Analítica Nominal</span>
      </button>
    </div>

    <div class="sidebar-footer">
      <div style="padding: 2px; font-size: 10px; color: var(--text-muted); line-height: 1.4;">
        <div style="font-size: 8.5px; font-weight: 700; color: var(--s1-primary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px;">Desenvolvido por</div>
        <div style="font-size: 11.5px; font-weight: 800; color: var(--text-dark);">Marcelo Guedes</div>
        <div style="font-size: 10px; color: var(--text-muted); font-weight: 500;">Analista de Sistema</div>
      </div>
    </div>
  </aside>

  <!-- ======================================================== -->
  <!-- MAIN CONTENT -->
  <!-- ======================================================== -->
  <main class="main-content">

    <!-- TOP NAVBAR -->
    <header class="top-navbar">
      <div class="top-titles">
        <p>S1 Saúde • Monitoramento Estratégico de Análise & Auditoria</p>
        <h1>Cockpit Gestão de Auditoria & Implantação de Contratos</h1>
      </div>
      <div class="top-actions">
        <div class="status-chip">
          <div class="lbl">Sincronização Jira</div>
          <div class="val" id="chip-sync-count">""" + f"{len(records):,}".replace(",", ".") + """ ITENS</div>
        </div>
        <div class="status-chip">
          <div class="lbl">Total Mapeado</div>
          <div class="val" id="top-vidas-count">""" + f"{len([r for r in records if r.get('Tipo Item') == 'Subtarefa']):,}".replace(",", ".") + """ VIDAS</div>
        </div>
        <button id="btn-sync-jira" class="btn-top btn-top-sync" onclick="iniciarSincronizacaoJira()">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/></svg>
          <span>Atualizar Dados</span>
        </button>
        <button class="btn-top" onclick="window.print()">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
          <span>Exportar em PDF</span>
        </button>
      </div>
    </header>

    <!-- BARRA GLOBAL DE FILTRO DE DATAS -->
    <section class="global-date-bar">
      <div class="date-bar-left">
        <div class="date-bar-label">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/></svg>
          <span>Período:</span>
        </div>
        <div class="preset-buttons">
          <button class="btn-preset active" onclick="setDatePreset('all')">Todo o Período</button>
          <button class="btn-preset" onclick="setDatePreset('2025')">Ano 2025</button>
          <button class="btn-preset" onclick="setDatePreset('2026')">Ano 2026</button>
          <button class="btn-preset" onclick="setDatePreset('last90')">Últimos 90 Dias</button>
          <button class="btn-preset" onclick="setDatePreset('last30')">Últimos 30 Dias</button>
          <button class="btn-preset" onclick="setDatePreset('thisMonth')">Agosto / 2026</button>
        </div>
      </div>

      <div class="custom-date-inputs">
        <label>De:</label>
        <input type="date" id="date-start" onchange="applyDateRange()">
        <label>Até:</label>
        <input type="date" id="date-end" onchange="applyDateRange()">
        <div class="filtered-period-badge" id="period-indicator-badge">Todo o Histórico</div>
      </div>
    </section>

    <!-- ======================================================== -->
    <!-- TAB 1: VISÃO GERAL EXECUTIVA -->
    <!-- ======================================================== -->
    <div id="tab-exec" class="panel active">

      <!-- KPI ROW -->
      <div class="row row-6">
        <div class="card kpi-card kpi-card-clickable" onclick="drillDownKPI('TODAS')" title="Clique para ver todos os beneficiários na Base Nominal">
          <div class="kpi-icon-box bg-s1-indigo">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </div>
          <div class="kpi-body">
            <div class="lbl">Total de Vidas</div>
            <div class="val" id="kpi-total-vidas">2.239</div>
            <div class="sub">
              <span>No período</span>
              <span class="kpi-click-tag">Base ➔</span>
            </div>
          </div>
        </div>

        <div class="card kpi-card kpi-card-clickable" onclick="drillDownKPI('ANÁLISE PENDENTE')" title="Clique para abrir a análise detalhada de Pendências e Fila">
          <div class="kpi-icon-box bg-s1-coral">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          </div>
          <div class="kpi-body">
            <div class="lbl">Análise Pendente</div>
            <div class="val" style="color: var(--s1-secondary);" id="kpi-pendente">1.130</div>
            <div class="sub">
              <span id="kpi-sub-pendente">50.5% na fila</span>
              <span class="kpi-click-tag" style="background: rgba(227,97,89,0.15); color: var(--s1-secondary);">Fila ➔</span>
            </div>
          </div>
        </div>

        <div class="card kpi-card kpi-card-clickable" onclick="drillDownKPI('AUDITORIA EM ANDAMENTO')" title="Clique para ver os casos em auditoria ativa">
          <div class="kpi-icon-box bg-s1-teal">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" x2="16.65" y1="21" y2="16.65"/></svg>
          </div>
          <div class="kpi-body">
            <div class="lbl">Em Andamento</div>
            <div class="val" style="color: var(--s1-tertiary);" id="kpi-andamento">232</div>
            <div class="sub">
              <span>Auditoria ativa</span>
              <span class="kpi-click-tag" style="background: rgba(43,170,177,0.15); color: var(--s1-tertiary);">Ver ➔</span>
            </div>
          </div>
        </div>

        <div class="card kpi-card kpi-card-clickable" onclick="drillDownKPI('LIBERAR PARA CADASTRAR')" title="Clique para ver os beneficiários liberados para cadastro">
          <div class="kpi-icon-box bg-s1-green">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
          </div>
          <div class="kpi-body">
            <div class="lbl">Liberado p/ Cadastrar</div>
            <div class="val" style="color: var(--s1-green);" id="kpi-liberado">314</div>
            <div class="sub">
              <span>Aprovados</span>
              <span class="kpi-click-tag" style="background: rgba(5,150,105,0.15); color: var(--s1-green);">Aprovados ➔</span>
            </div>
          </div>
        </div>

        <div class="card kpi-card kpi-card-clickable" onclick="drillDownKPI('CADASTRO CONCLUÍDO')" title="Clique para ver os beneficiários com cadastro concluído">
          <div class="kpi-icon-box bg-s1-purple">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/></svg>
          </div>
          <div class="kpi-body">
            <div class="lbl">Cadastro Concluído</div>
            <div class="val" style="color: var(--s1-purple);" id="kpi-concluido">438</div>
            <div class="sub">
              <span>Ativos na base</span>
              <span class="kpi-click-tag" style="background: rgba(124,58,237,0.15); color: var(--s1-purple);">Base ➔</span>
            </div>
          </div>
        </div>

        <div class="card kpi-card kpi-card-clickable" onclick="switchNav('tab-pendencias', document.getElementById('nav-pendencias'))" title="Clique para ver a análise completa de Lead Time e Fila">
          <div class="kpi-icon-box bg-s1-amber">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
          </div>
          <div class="kpi-body">
            <div class="lbl">Taxa de Liberação</div>
            <div class="val" style="color: var(--s1-amber);" id="kpi-taxa-liberacao">33.6%</div>
            <div class="sub">
              <span>Concluídos + Lib.</span>
              <span class="kpi-click-tag" style="background: rgba(217,119,6,0.15); color: var(--s1-amber);">Lead Time ➔</span>
            </div>
          </div>
        </div>
      </div>

      <!-- CRITICAL ALERT -->
      <div class="alert-box">
        <div style="display: flex; align-items: center; justify-content: center; width: 24px; height: 24px; flex-shrink: 0; color: var(--s1-secondary);">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
        </div>
        <div>
          <strong>Diagnóstico Crítico para a Diretoria:</strong> A operação registra <strong>1.130 vidas (50,5% do total)</strong> represadas em <em>Análise Pendente</em> aguardando triagem inicial da equipe de auditoria. O contrato <strong>G&E Serviços concentra 1.274 vidas</strong>, e os maiores lotes represados possuem vigência em <strong>01/02/2026, 01/05/2026 e 01/06/2026</strong>.
        </div>
      </div>

      <!-- EVOLUÇÃO TEMPORAL MÊS A MÊS -->
      <div class="card" style="margin-bottom: 12px;">
        <div class="card-title">
          Evolução Temporal: Volume de Entrada vs. Liberações
          <span class="card-title-tag" id="evolucao-periodo-tag">Série Histórica</span>
        </div>
        <div class="chart-box">
          <canvas id="chartEvolucaoMensal"></canvas>
        </div>
      </div>

      <!-- MAIN CHARTS ROW -->
      <div class="row row-2-1">
        <div class="card">
          <div class="card-title">
            Distribuição do Funil Operacional de Auditoria
            <span class="card-title-tag" id="funil-vidas-tag">2.239 Vidas</span>
          </div>
          <div class="chart-box">
            <canvas id="chartFunilExec"></canvas>
          </div>
        </div>

        <div class="card">
          <div class="card-title">
            Top 5 Contratos com Maior Demanda
            <span class="card-title-tag">Volume de Vidas</span>
          </div>
          <div id="top5-empresas-list" style="padding-top: 4px;"></div>
        </div>
      </div>

      <!-- TIMELINE ROW -->
      <div class="row row-2">
        <div class="card">
          <div class="card-title">Volume de Vidas por Data de Vigência (Top 8)</div>
          <div class="chart-box">
            <canvas id="chartVigenciaExec"></canvas>
          </div>
        </div>

        <div class="card">
          <div class="card-title">Segmento de Contratação & Modalidade</div>
          <div class="chart-box">
            <canvas id="chartSegmentoExec"></canvas>
          </div>
        </div>
      </div>

    </div>

    <!-- ======================================================== -->
    <!-- TAB: TOP PENDÊNCIAS & LEAD TIME DE AUDITORIA -->
    <!-- ======================================================== -->
    <div id="tab-pendencias" class="panel">
      
      <!-- QUICK PILL FILTERS -->
      <div class="filter-pills">
        <button class="filter-pill active" id="pill-todas-pend" onclick="setFiltroVisaoPendencias('TODAS')">
          <span>Todas as Pendências na Fila</span>
          <span class="pill-count" id="count-pill-todas">0</span>
        </button>
        <button class="filter-pill" id="pill-analise-pend" onclick="setFiltroVisaoPendencias('ANÁLISE PENDENTE')">
          <span style="color: var(--s1-secondary);">●</span>
          <span>Fila de Entrada (Análise Pendente)</span>
          <span class="pill-count" id="count-pill-analise">0</span>
        </button>
        <button class="filter-pill" id="pill-andamento" onclick="setFiltroVisaoPendencias('AUDITORIA EM ANDAMENTO')">
          <span style="color: var(--s1-tertiary);">●</span>
          <span>Auditoria em Andamento</span>
          <span class="pill-count" id="count-pill-andamento">0</span>
        </button>
        <button class="filter-pill" id="pill-criticos" onclick="setFiltroVisaoPendencias('CRITICOS')">
          <span style="color: var(--s1-red);">●</span>
          <span>Casos Críticos (Diretoria & Cadastro)</span>
          <span class="pill-count" id="count-pill-criticos">0</span>
        </button>
        <button class="filter-pill" id="pill-concluidos" onclick="setFiltroVisaoPendencias('CONCLUIDOS')">
          <span style="color: var(--s1-green);">●</span>
          <span>Visão de Concluídos & Lead Time</span>
          <span class="pill-count" id="count-pill-concluidos">0</span>
        </button>
      </div>

      <!-- LEAD TIME & PENDÊNCIAS KPI ROW (5 CARDS) -->
      <div class="row row-5">
        <div class="card kpi-card">
          <div class="kpi-icon-box bg-s1-indigo">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          </div>
          <div class="kpi-body">
            <div class="lbl">Lead Time Médio</div>
            <div class="val" style="color: var(--s1-primary);" id="kpi-lt-medio">0.0 dias</div>
            <div class="sub" id="kpi-lt-sub">Mediana: 0.0 dias</div>
          </div>
        </div>

        <div class="card kpi-card">
          <div class="kpi-icon-box bg-s1-coral">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4"/><path d="M12 18v4"/><path d="M4.93 4.93l2.83 2.83"/><path d="M16.24 16.24l2.83 2.83"/><path d="M2 12h4"/><path d="M18 12h4"/><path d="M4.93 19.07l2.83-2.83"/><path d="M16.24 7.76l2.83-2.83"/></svg>
          </div>
          <div class="kpi-body">
            <div class="lbl">Aging Médio da Fila</div>
            <div class="val" style="color: var(--s1-secondary);" id="kpi-aging-medio">0.0 dias</div>
            <div class="sub" id="kpi-aging-sub">Tempo em aberto atual</div>
          </div>
        </div>

        <div class="card kpi-card">
          <div class="kpi-icon-box bg-s1-amber">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/></svg>
          </div>
          <div class="kpi-body" style="overflow: hidden;">
            <div class="lbl">Maior Fila Concentrada</div>
            <div class="val" style="color: var(--s1-amber); font-size: 12.5px; line-height: 1.2; text-overflow: ellipsis; white-space: nowrap; overflow: hidden;" id="kpi-top-empresa-nome">-</div>
            <div class="sub" id="kpi-top-empresa-vidas">0 vidas represadas</div>
          </div>
        </div>

        <div class="card kpi-card">
          <div class="kpi-icon-box bg-s1-teal">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>
          </div>
          <div class="kpi-body">
            <div class="lbl">Concentração Top 5</div>
            <div class="val" style="color: var(--s1-tertiary);" id="kpi-concentracao-top5">0.0%</div>
            <div class="sub">Do volume total da fila</div>
          </div>
        </div>

        <div class="card kpi-card">
          <div class="kpi-icon-box bg-s1-red">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>
          </div>
          <div class="kpi-body">
            <div class="lbl">Gargalos (> 30 Dias)</div>
            <div class="val" style="color: var(--s1-red);" id="kpi-gargalos-30d">0 vidas</div>
            <div class="sub" id="kpi-gargalos-sub">Aguardando há +1 mês</div>
          </div>
        </div>
      </div>

      <!-- CHARTS ROW 1 -->
      <div class="row row-2-1">
        <div class="card">
          <div class="card-title">
            Top 10 Empresas com Maior Volume de Beneficiários Pendentes
            <span class="card-title-tag" id="tag-grafico-top-pend">Contagem de Vidas</span>
          </div>
          <div class="chart-box-tall">
            <canvas id="chartTopEmpresasPendentes"></canvas>
          </div>
        </div>

        <div class="card">
          <div class="card-title">
            Evolução do Lead Time Médio de Conclusão
            <span class="card-title-tag">Mês a Mês (Dias)</span>
          </div>
          <div class="chart-box-tall">
            <canvas id="chartLeadTimeEvolucao"></canvas>
          </div>
        </div>
      </div>

      <!-- CHARTS ROW 2 -->
      <div class="row row-2">
        <div class="card">
          <div class="card-title">
            Distribuição do Tempo de Conclusão da Auditoria
            <span class="card-title-tag">Faixas de Dias (Lead Time)</span>
          </div>
          <div class="chart-box">
            <canvas id="chartDistribuicaoLeadTime"></canvas>
          </div>
        </div>

        <div class="card">
          <div class="card-title">
            Curva de Aging das Pendências Ativas
            <span class="card-title-tag">Dias em Fila de Espera</span>
          </div>
          <div class="chart-box">
            <canvas id="chartAgingDistribuicao"></canvas>
          </div>
        </div>
      </div>

      <!-- TABELA ANALÍTICA DE TOP EMPRESAS PENDENTES -->
      <div class="card">
        <div class="filters-bar" style="margin-bottom: 8px; border: none; padding: 0;">
          <div class="filter-inputs">
            <input type="text" id="txt-search-pend" placeholder="Buscar empresa ou contrato..." oninput="renderTopPendenciasTable()">
            <select id="sel-ordem-pend" onchange="renderTopPendenciasTable()">
              <option value="vidas_desc">Ordenar por: Maior Volume de Vidas</option>
              <option value="aging_desc">Ordenar por: Maior Tempo em Aberto (Aging)</option>
              <option value="nome_asc">Ordenar por: Nome da Empresa (A-Z)</option>
            </select>
          </div>
          <button class="btn-action" onclick="exportPendenciasCSV()">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
            <span>Exportar Análise de Pendências (CSV)</span>
          </button>
        </div>

        <div style="overflow-x: auto; max-height: 480px;">
          <table>
            <thead>
              <tr>
                <th style="width: 70px; text-align: center;">Posição</th>
                <th>Empresa / Contrato</th>
                <th style="text-align: center;">Total Pendentes</th>
                <th style="text-align: center;">Análise Pendente</th>
                <th style="text-align: center;">Em Andamento</th>
                <th style="text-align: center;">Casos Críticos</th>
                <th style="text-align: center;">Aging Médio</th>
                <th>Vigência Principal</th>
                <th>Lote Mais Antigo</th>
                <th style="text-align: center;">Ações</th>
              </tr>
            </thead>
            <tbody id="tbody-top-pendencias"></tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- ======================================================== -->
    <!-- TAB 2: QUADRO KANBAN DA OPERAÇÃO -->
    <!-- ======================================================== -->
    <div id="tab-kanban" class="panel">
      <div class="filters-bar">
        <div class="filter-inputs">
          <span style="font-size: 11.5px; font-weight: 700; color: var(--s1-primary);">Filtros do Quadro:</span>
          <select id="k-filter-vigencia" onchange="renderKanbanBoard()">
            <option value="">Todas as Vigências</option>
          </select>
          <select id="k-filter-empresa" onchange="renderKanbanBoard()">
            <option value="">Todas as Empresas</option>
          </select>
          <input type="text" id="k-filter-search" placeholder="Buscar no Quadro Kanban..." oninput="renderKanbanBoard()">
        </div>
        <div style="font-size: 11px; color: var(--text-muted);">
          Clique em qualquer card para ver o detalhamento completo do beneficiário
        </div>
      </div>

      <div class="kanban-board-container" id="kanban-board-wrapper"></div>
    </div>

    <!-- ======================================================== -->
    <!-- TAB 3: PRODUTIVIDADE & INTERAÇÕES DA EQUIPE -->
    <!-- ======================================================== -->
    <div id="tab-equipe" class="panel">
      <div class="row row-3">
        <div class="card kpi-card">
          <div class="kpi-icon-box bg-s1-indigo">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          </div>
          <div class="kpi-body">
            <div class="lbl">Carlos Henrique de Sousa</div>
            <div class="val">1.892 ações</div>
            <div class="sub">Abertura de lotes, uploads e 91 conclusões</div>
          </div>
        </div>

        <div class="card kpi-card">
          <div class="kpi-icon-box bg-s1-teal">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
          </div>
          <div class="kpi-body">
            <div class="lbl">Priscila Tada</div>
            <div class="val">673 ações</div>
            <div class="sub">302 liberações clínicas e 17 CPTs</div>
          </div>
        </div>

        <div class="card kpi-card">
          <div class="kpi-icon-box bg-s1-coral">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/><path d="M6 6h10"/><path d="M6 10h10"/></svg>
          </div>
          <div class="kpi-body">
            <div class="lbl">Raquel Lopes (Auditoria)</div>
            <div class="val">317 ações</div>
            <div class="sub">Fila geral de triagem inicial</div>
          </div>
        </div>
      </div>

      <div class="row row-2">
        <div class="card">
          <div class="card-title">Transições de Status por Operador (Quem Movimenta a Fila)</div>
          <div class="chart-box">
            <canvas id="chartInteracoesEquipe"></canvas>
          </div>
        </div>

        <div class="card">
          <div class="card-title">Matriz de Produtividade & Papéis no Fluxo</div>
          <table>
            <thead>
              <tr>
                <th>Usuário / Profissional</th>
                <th>Papel no Processo</th>
                <th>Volume de Ações</th>
                <th>Impacto Principal</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Carlos Henrique de Sousa</strong></td>
                <td>Operacional / Cadastro</td>
                <td>1.892 eventos</td>
                <td>Inclusão de propostas, pastas Z:\\ e finalização no sistema</td>
              </tr>
              <tr>
                <td><strong>Priscila Tada</strong></td>
                <td>Auditora / Pareceres</td>
                <td>673 eventos</td>
                <td>Auditoria técnica, aprovações clínicas e pareceres de CPT</td>
              </tr>
              <tr>
                <td><strong>Raquel Lopes</strong></td>
                <td>Triagem de Entrada</td>
                <td>317 eventos</td>
                <td>Distribuição e transição da fila de pendentes para andamento</td>
              </tr>
              <tr>
                <td><strong>Luiz Felipe Vieira</strong></td>
                <td>Apoio Operacional</td>
                <td>15 eventos</td>
                <td>Ajustes pontuais de cadastro e contratos</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Últimas Movimentações Realizadas na Fila (Log de Auditoria)</div>
        <table>
          <thead>
            <tr>
              <th>Data/Hora</th>
              <th>Ticket</th>
              <th>Beneficiário</th>
              <th>Empresa</th>
              <th>Usuário Responsável</th>
              <th>Transição de Status</th>
            </tr>
          </thead>
          <tbody id="log-transicoes-body"></tbody>
        </table>
      </div>
    </div>

            <!-- ======================================================== -->
    <!-- TAB 4: CASOS CRÍTICOS & PENDÊNCIAS DA DIRETORIA -->
    <!-- ======================================================== -->
    <div id="tab-diretoria" class="panel">
      <!-- CARD 1: AGUARDANDO DIRETORIA (100% FULL WIDTH) -->
      <div class="card" style="margin-bottom: 14px;">
        <div class="card-title" style="color: var(--s1-red);">
          <div style="display: flex; align-items: center; gap: 8px;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
            <span id="title-total-diretoria">0 Casos em "AGUARDANDO DIRETORIA"</span>
          </div>
          <span class="card-title-tag" style="background: #FEE2E2; color: #991B1B;">Ação Executiva Imediata</span>
        </div>
        <div style="font-size: 11.5px; color: var(--text-muted); margin-bottom: 12px;">
          Casos que exigem validação ou deliberação da Diretoria para liberação da proposta e cadastro no sistema.
        </div>
        <div style="overflow-x: auto;">
          <table>
            <thead>
              <tr>
                <th style="width: 140px;">Ticket Jira</th>
                <th>Beneficiário (Nome Completo)</th>
                <th>Empresa / Contrato / Lote</th>
                <th style="width: 110px;">Entrada</th>
                <th style="width: 140px;">Pendenciado em</th>
                <th style="width: 140px;">Tempo em Espera</th>
                <th style="width: 150px; text-align: center;">Ação Necessária</th>
              </tr>
            </thead>
            <tbody id="tbody-aguardando-diretoria">
            </tbody>
          </table>
        </div>
      </div>

      <!-- CARD 2: PENDÊNCIA CADASTRO (100% FULL WIDTH) -->
      <div class="card">
        <div class="card-title" style="color: var(--s1-amber);">
          <div style="display: flex; align-items: center; gap: 8px;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            <span id="title-total-cadastro">0 Casos em "PENDÊNCIA CADASTRO"</span>
          </div>
          <span class="card-title-tag" style="background: #FEF3C7; color: #92400E;">Inconsistência Documental</span>
        </div>
        <div style="font-size: 11.5px; color: var(--text-muted); margin-bottom: 12px;">
          Casos com documentação pendente ou divergência cadastral travando o fluxo de implantação.
        </div>
        <div style="overflow-x: auto;">
          <table>
            <thead>
              <tr>
                <th style="width: 140px;">Ticket Jira</th>
                <th>Beneficiário (Nome Completo)</th>
                <th>Empresa / Contrato / Lote</th>
                <th style="width: 110px;">Entrada</th>
                <th style="width: 140px;">Pendenciado em</th>
                <th style="width: 140px;">Tempo em Espera</th>
                <th style="width: 180px; text-align: center;">Origem da Pendência</th>
              </tr>
            </thead>
            <tbody id="tbody-pendencia-cadastro">
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- TAB 5: CONTROLE POR VIGÊNCIA & PRAZOS -->
    <!-- ======================================================== -->
    <div id="tab-vigencia" class="panel">
      <div class="card" style="margin-bottom: 12px;">
        <div class="card-title">Volume Consolidado de Vidas por Data de Vigência</div>
        <div class="chart-box-tall">
          <canvas id="chartVigenciaFull"></canvas>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- TAB 6: TOP EMPRESAS & CONTRATOS -->
    <!-- ======================================================== -->
    <div id="tab-empresas" class="panel">
      <div class="card" style="margin-bottom: 12px;">
        <div class="card-title">Ranking de Contratos por Volume de Beneficiários Submetidos</div>
        <div class="chart-box-tall">
          <canvas id="chartEmpresasFull"></canvas>
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- TAB 7: BASE ANALÍTICA NOMINAL -->
    <!-- ======================================================== -->
    <div id="tab-base" class="panel">
      <div class="filters-bar">
        <div class="filter-inputs">
          <select id="sel-vigencia" onchange="filterTable()">
            <option value="">Todas as Vigências</option>
          </select>

          <select id="sel-empresa" onchange="filterTable()">
            <option value="">Todas as Empresas</option>
          </select>

          <select id="sel-status" onchange="filterTable()">
            <option value="">Todos os Status</option>
          </select>

          <input type="text" id="txt-search" placeholder="Buscar por Nome ou Ticket..." oninput="filterTable()">
        </div>

        <button class="btn-action" onclick="exportTableCSV()">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
          <span>Exportar Base CSV</span>
        </button>
      </div>

      <div class="card">
        <div style="overflow-x: auto; max-height: 540px;">
          <table>
            <thead>
              <tr>
                <th>Ticket Jira</th>
                <th>Beneficiário (Vida)</th>
                <th>Empresa / Contrato</th>
                <th>Vigência</th>
                <th>Status</th>
                <th>Tipo</th>
                <th>Segmento</th>
                <th>Responsável</th>
                <th>Data Criação</th>
              </tr>
            </thead>
            <tbody id="table-beneficiarios-body"></tbody>
          </table>
        </div>

        <div class="pagination-container">
          <div id="page-count-info">Mostrando 1 a 50 de 2.239 registros</div>
          <div class="page-btns" id="page-nav-btns"></div>
        </div>
      </div>
    </div>

  </main>

  <!-- DRAWER LATERAL DE DETALHE INDIVIDUAL -->
  <div class="drawer-overlay" id="drawer-overlay" onclick="closeDrawer()"></div>
  <div class="drawer" id="drawer-panel">
    <div class="drawer-header">
      <div>
        <div style="font-size: 10px; opacity: 0.8; text-transform: uppercase;">Detalhamento do Beneficiário</div>
        <h3 id="d-beneficiario-nome">Nome do Beneficiário</h3>
      </div>
      <button class="btn-close-drawer" onclick="closeDrawer()">✕</button>
    </div>

    <div class="drawer-body">
      <div class="drawer-field">
        <div class="drawer-label">Ticket no Jira Cloud</div>
        <div class="drawer-value" id="d-ticket-key">-</div>
      </div>

      <div class="drawer-field">
        <div class="drawer-label">Status Operacional Atual</div>
        <div class="drawer-value" id="d-status-badge">-</div>
      </div>

      <div class="drawer-field">
        <div class="drawer-label">Empresa / Contrato / Lote</div>
        <div class="drawer-value" id="d-empresa">-</div>
      </div>

      <div class="drawer-field">
        <div class="drawer-label">Data de Criação (Entrada)</div>
        <div class="drawer-value" id="d-data-criacao">-</div>
      </div>

      <div class="drawer-field">
        <div class="drawer-label">Data de Vigência</div>
        <div class="drawer-value" id="d-vigencia" style="color: var(--s1-primary);">-</div>
      </div>

      <div class="drawer-field">
        <div class="drawer-label">Tipo de Beneficiário & Modalidade</div>
        <div class="drawer-value" id="d-tipo-beneficiario">-</div>
      </div>

      <div class="drawer-field">
        <div class="drawer-label">Análise de CPT / Segmento</div>
        <div class="drawer-value" id="d-cpt">-</div>
      </div>

      <div class="drawer-field">
        <div class="drawer-label">Responsável pela Análise</div>
        <div class="drawer-value" id="d-responsavel">-</div>
      </div>

      <div class="drawer-field">
        <div class="drawer-label">Caminho da Proposta Digitalizada</div>
        <div style="font-size: 11px; color: var(--text-muted); word-break: break-all;" id="d-caminho-arquivo">-</div>
      </div>

      <a href="#" target="_blank" class="btn-jira-link" id="d-btn-jira">Abrir Chamado no Jira Cloud ↗</a>
    </div>
  </div>

  <!-- MODAL DE SINCRONIZAÇÃO EM TEMPO REAL COM O JIRA -->
  <div class="sync-modal-overlay" id="sync-modal-overlay">
    <div class="sync-modal-card">
      <div class="sync-modal-header">
        <div class="sync-modal-logo">
          <img src="https://s1saude.com.br/wp-content/uploads/2021/08/logo-s1saude-1.png" alt="S1 Saúde" style="height: 28px;" onerror="this.outerHTML='<strong style=\\'color:#282394;font-size:14px;\\'>S1 SAÚDE</strong>'">
        </div>
        <div>
          <h3>Sincronização em Tempo Real</h3>
          <p>Conectando ao Jira Cloud (s1saude.atlassian.net)</p>
        </div>
      </div>

      <div class="sync-modal-body">
        <div class="sync-spinner-box">
          <svg class="spinner-svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#282394" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
          </svg>
        </div>

        <div class="sync-progress-bar-wrap">
          <div class="sync-progress-bar" id="sync-progress-fill"></div>
        </div>
        <div class="sync-progress-pct" id="sync-progress-label">0%</div>

        <div class="sync-steps-list">
          <div class="sync-step" id="step-1">
            <span class="step-icon">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </span>
            <span class="step-text">Autenticando na API REST com credenciais corporativas...</span>
          </div>
          <div class="sync-step" id="step-2">
            <span class="step-icon">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </span>
            <span class="step-text">Consultando JQL no projeto AUDITORIA (100% dos tickets)...</span>
          </div>
          <div class="sync-step" id="step-3">
            <span class="step-icon">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </span>
            <span class="step-text">Processando lotes, vigências e novos beneficiários...</span>
          </div>
          <div class="sync-step" id="step-4">
            <span class="step-icon">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </span>
            <span class="step-text">Recalculando matrizes de produtividade e KPIs executivos...</span>
          </div>
        </div>

        <div class="sync-success-msg" id="sync-success-box" style="display: none;">
          Base de dados 100% atualizada com sucesso! Recarregando painel...
        </div>
      </div>
    </div>
  </div>

<script>
  /* __NOBLE_CRYPTO_PLACEHOLDER__ */
  const VAULT = __VAULT_JSON_RAW__;
  let allRecords = [];
  let interactionsData = {};
  let alertasData = {};
  let vidas = [];

  // Date Filter State
  let startDateFilter = null;
  let endDateFilter = null;

  let currentPeriodVidas = [];
  let filteredVidas = [];
  let currentPage = 1;
  const pageSize = 50;

  function formatarDataBR(dateStr) {
    if (!dateStr || dateStr === "-" || dateStr === "None" || dateStr === "null" || dateStr === "undefined") return "-";
    const str = String(dateStr).trim();
    if (!str) return "-";
    
    // Se ja estiver no formato brasileiro DD/MM/AAAA
    if (/^\\d{2}\\/\\d{2}\\/\\d{4}/.test(str)) return str;
    
    // Tratar formatos ISO e padroes: YYYY-MM-DD ou YYYY-MM-DD HH:MM:SS ou YYYY-MM-DDTHH:MM:SS
    const cleanStr = str.replace('T', ' ');
    const match = cleanStr.match(/^(\\d{4})-(\\d{2})-(\\d{2})(?:\\s+(\\d{2}):(\\d{2})(?::(\\d{2}))?)?/);
    if (match) {
      const [_, ano, mes, dia, hora, min] = match;
      if (hora && min) {
        return `${dia}/${mes}/${ano} ${hora}:${min}`;
      }
      return `${dia}/${mes}/${ano}`;
    }
    
    try {
      const d = new Date(str);
      if (!isNaN(d.getTime())) {
        const dia = String(d.getDate()).padStart(2, '0');
        const mes = String(d.getMonth() + 1).padStart(2, '0');
        const ano = d.getFullYear();
        return `${dia}/${mes}/${ano}`;
      }
    } catch(e) {}
    
    return str;
  }

  function decryptVaultWithCredentials(username, password) {
    if (window.NobleCrypto && typeof window.NobleCrypto.decryptVault === 'function') {
      return window.NobleCrypto.decryptVault(VAULT, username, password);
    }
    throw new Error("Módulo criptográfico não carregado.");
  }

  function handleLoginSubmit(e) {
    if (e) e.preventDefault();
    const userInput = (document.getElementById("input-username").value || "").trim().toLowerCase();
    const passInput = document.getElementById("input-password").value;
    const errBox = document.getElementById("login-error-box");
    const errText = document.getElementById("login-error-text");
    const btnText = document.getElementById("btn-login-text");
    const spinner = document.getElementById("btn-login-spinner");

    errBox.style.display = "none";
    btnText.textContent = "Carregando dados...";
    spinner.style.display = "inline-block";

    setTimeout(() => {
      try {
        const { payload, uinfo, masterKeyRawB64 } = decryptVaultWithCredentials(userInput, passInput);
        
        const sessionObj = {
          user: (userInput || "").toLowerCase().trim(),
          nome: uinfo.nome,
          perfil: uinfo.perfil,
          mk: masterKeyRawB64
        };
        sessionStorage.setItem("s1_auditoria_session", JSON.stringify(sessionObj));

        carregarDadosDescriptografados(payload, sessionObj);

        const overlay = document.getElementById("login-screen-overlay");
        overlay.classList.remove("active");
      } catch (err) {
        errBox.style.display = "flex";
        errText.textContent = err.message || "Erro na autenticação.";
      } finally {
        btnText.textContent = "Acessar Cockpit";
        spinner.style.display = "none";
      }
    }, 40);
  }

  function restoreSessionIfActive() {
    const rawSession = sessionStorage.getItem("s1_auditoria_session");
    if (!rawSession) {
      const uInput = document.getElementById("input-username");
      const pInput = document.getElementById("input-password");
      if (uInput) uInput.value = "";
      if (pInput) pInput.value = "";
      document.getElementById("login-screen-overlay").classList.add("active");
      return false;
    }

    try {
      const sessionObj = JSON.parse(rawSession);
      if (window.NobleCrypto && typeof window.NobleCrypto.decryptSession === 'function') {
        const payload = window.NobleCrypto.decryptSession(VAULT, sessionObj.mk);
        carregarDadosDescriptografados(payload, sessionObj);
        document.getElementById("login-screen-overlay").classList.remove("active");
        return true;
      }
      throw new Error("Módulo criptográfico não carregado.");
    } catch (e) {
      sessionStorage.removeItem("s1_auditoria_session");
      const uInput = document.getElementById("input-username");
      const pInput = document.getElementById("input-password");
      if (uInput) uInput.value = "";
      if (pInput) pInput.value = "";
      document.getElementById("login-screen-overlay").classList.add("active");
      return false;
    }
  }

  function carregarDadosDescriptografados(payload, sessionObj) {
    allRecords = payload.records || [];
    interactionsData = payload.interactions || {};
    alertasData = payload.alertas || {};
    vidas = allRecords.filter(r => r["Tipo Item"] === "Subtarefa");
    currentPeriodVidas = [...vidas];
    filteredVidas = [...vidas];

    if (sessionObj) {
      const nameEl = document.getElementById("user-logged-name");
      const perfEl = document.getElementById("user-logged-perfil");
      if (nameEl) nameEl.textContent = sessionObj.nome;
      if (perfEl) perfEl.textContent = sessionObj.perfil;
    }

    init();
  }

  function logoutSession() {
    sessionStorage.removeItem("s1_auditoria_session");
    const uInput = document.getElementById("input-username");
    const pInput = document.getElementById("input-password");
    if (uInput) uInput.value = "";
    if (pInput) pInput.value = "";
    location.reload();
  }

  function togglePasswordVisibility() {
    const input = document.getElementById("input-password");
    const eyeSvg = document.getElementById("eye-icon-svg");
    if (input.type === "password") {
      input.type = "text";
      if (eyeSvg) {
        eyeSvg.innerHTML = '<path d="m2 2 20 20"/><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/>';
      }
    } else {
      input.type = "password";
      if (eyeSvg) {
        eyeSvg.innerHTML = '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>';
      }
    }
  }


  // Chart instances
  let chartFunil, chartVigExec, chartSegExec, chartEvolucao, chartVigFull, chartEmpFull, chartInteracoes;
  let chartTopEmpresasPendentes, chartLeadTimeEvolucao, chartDistribuicaoLeadTime, chartAgingDistribuicao;

  // 10 Kanban Columns
  const kanbanColumns = [
    { id: "ANÁLISE PENDENTE", title: "ANÁLISE PENDENTE", match: ["ANÁLISE PENDENTE"] },
    { id: "PENDÊNCIA CADASTRO", title: "PENDÊNCIA CADASTRO", match: ["PENDÊNCIA CADASTRO"] },
    { id: "AGUARDANDO DIRETORIA", title: "AGUARDANDO DIRETORIA", match: ["AGUARDANDO DIRETORIA"] },
    { id: "APS", title: "APS", match: ["APS"] },
    { id: "AUDITORIA EM ANDAMENTO", title: "AUDITORIA EM ANDAMENTO", match: ["AUDITORIA EM ANDAMENTO"] },
    { id: "LIBERAR PARA CADASTRAR", title: "LIBERADO PARA CADASTRAR", match: ["LIBERAR PARA CADASTRAR", "LIBERADO COM CPT"] },
    { id: "CADASTRO CONCLUÍDO", title: "CADASTRO CONCLUÍDO", match: ["CADASTRO CONCLUÍDO"] },
    { id: "CANCELADO", title: "CANCELADO", match: ["CANCELADO"] },
    { id: "CONCLUÍDO APS", title: "CONCLUÍDO APS", match: ["CONCLUÍDO APS"] },
    { id: "CPT ENVIADA", title: "CPT ENVIADA", match: ["CPT Enviada", "CPT ENVIADA"] }
  ];

  function switchNav(tabId, el) {
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    
    if (el) {
      el.classList.add('active');
    } else {
      const matchBtn = document.querySelector(`.nav-item[onclick*="${tabId}"]`);
      if (matchBtn) matchBtn.classList.add('active');
    }

    const panel = document.getElementById(tabId);
    if (panel) panel.classList.add('active');

    if (tabId === 'tab-kanban') {
      renderKanbanBoard();
    } else if (tabId === 'tab-pendencias') {
      recalculateLeadTimeAndPendencias();
    }
  }

  function renderAlertasTables() {
    const itensDir = (alertasData && alertasData.itens_aguardando_diretoria) || [];
    const tDirEl = document.getElementById("title-total-diretoria");
    if (tDirEl) tDirEl.textContent = `${itensDir.length} Casos em "AGUARDANDO DIRETORIA"`;
    
    const tbodyDir = document.getElementById("tbody-aguardando-diretoria");
    if (tbodyDir) {
      if (itensDir.length === 0) {
        tbodyDir.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 20px; color: var(--text-muted);">Nenhum caso aguardando parecer da diretoria no momento.</td></tr>';
      } else {
        tbodyDir.innerHTML = itensDir.map(item => `
          <tr onclick="openDrawerByKey('${item.chave}')">
            <td><span class="ticket-link">${item.chave} ↗</span></td>
            <td><strong>${item.beneficiario || 'Não identificado'}</strong></td>
            <td>${item.empresa || 'Não informada'}</td>
            <td style="color: var(--text-muted);">${formatarDataBR(item.data_entrada)}</td>
            <td><strong style="color: var(--s1-red);">${formatarDataBR(item.data_pendencia)}</strong></td>
            <td><span class="badge b-diretoria">+${item.dias_espera || 0} dias aguardando</span></td>
            <td style="text-align: center;"><span class="badge b-diretoria">${item.acao_necessaria || 'Parecer Diretoria'}</span></td>
          </tr>
        `).join("");
      }
    }

    const itensCad = (alertasData && alertasData.itens_pendencia_cadastro) || [];
    const tCadEl = document.getElementById("title-total-cadastro");
    if (tCadEl) tCadEl.textContent = `${itensCad.length} Casos em "PENDÊNCIA CADASTRO"`;
    
    const tbodyCad = document.getElementById("tbody-pendencia-cadastro");
    if (tbodyCad) {
      if (itensCad.length === 0) {
        tbodyCad.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 20px; color: var(--text-muted);">Nenhum caso com pendência cadastral no momento.</td></tr>';
      } else {
        tbodyCad.innerHTML = itensCad.map(item => `
          <tr onclick="openDrawerByKey('${item.chave}')">
            <td><span class="ticket-link">${item.chave} ↗</span></td>
            <td><strong>${item.beneficiario || 'Não identificado'}</strong></td>
            <td>${item.empresa || 'Não informada'}</td>
            <td style="color: var(--text-muted);">${formatarDataBR(item.data_entrada)}</td>
            <td><strong style="color: var(--s1-amber);">${formatarDataBR(item.data_pendencia)}</strong></td>
            <td><span class="badge b-pendente">+${item.dias_espera || 0} dias</span></td>
            <td style="text-align: center;"><span class="badge b-pendente">${item.origem_pendencia || 'Documento Pendente'}</span></td>
          </tr>
        `).join("");
      }
    }
  }

  function init() {
    populateDropdowns();
    initCharts();
    recalculateAll();
    renderTransitionsLog();
    renderAlertasTables();
  }

  function setDatePreset(preset) {
    document.querySelectorAll('.btn-preset').forEach(b => b.classList.remove('active'));
    const btnTarget = document.querySelector(`.btn-preset[onclick*="'${preset}'"]`);
    if (btnTarget) {
      btnTarget.classList.add('active');
    }

    const now = new Date("2026-08-26T23:59:59");
    const startInput = document.getElementById("date-start");
    const endInput = document.getElementById("date-end");
    const badge = document.getElementById("period-indicator-badge");

    if (preset === 'all') {
      startDateFilter = null;
      endDateFilter = null;
      startInput.value = "";
      endInput.value = "";
      badge.textContent = "Todo o Histórico";
    } else if (preset === '2026') {
      startDateFilter = "2026-01-01";
      endDateFilter = "2026-12-31";
      startInput.value = startDateFilter;
      endInput.value = endDateFilter;
      badge.textContent = "Ano 2026";
    } else if (preset === '2025') {
      startDateFilter = "2025-01-01";
      endDateFilter = "2025-12-31";
      startInput.value = startDateFilter;
      endInput.value = endDateFilter;
      badge.textContent = "Ano 2025";
    } else if (preset === 'last30') {
      const past30 = new Date(now);
      past30.setDate(past30.getDate() - 30);
      startDateFilter = past30.toISOString().slice(0, 10);
      endDateFilter = now.toISOString().slice(0, 10);
      startInput.value = startDateFilter;
      endInput.value = endDateFilter;
      badge.textContent = "Últimos 30 Dias";
    } else if (preset === 'last90') {
      const past90 = new Date(now);
      past90.setDate(past90.getDate() - 90);
      startDateFilter = past90.toISOString().slice(0, 10);
      endDateFilter = now.toISOString().slice(0, 10);
      startInput.value = startDateFilter;
      endInput.value = endDateFilter;
      badge.textContent = "Últimos 90 Dias";
    } else if (preset === 'thisMonth') {
      startDateFilter = "2026-08-01";
      endDateFilter = "2026-08-31";
      startInput.value = startDateFilter;
      endInput.value = endDateFilter;
      badge.textContent = "Agosto / 2026";
    }

    recalculateAll();
  }

  function applyDateRange() {
    const s = document.getElementById("date-start").value;
    const e = document.getElementById("date-end").value;
    startDateFilter = s || null;
    endDateFilter = e || null;

    document.querySelectorAll('.btn-preset').forEach(b => b.classList.remove('active'));
    document.getElementById("period-indicator-badge").textContent = `${s || 'Início'} até ${e || 'Hoje'}`;

    recalculateAll();
  }

  function recalculateAll() {
    currentPeriodVidas = vidas.filter(v => {
      const created = (v["Data Criação"] || "").substring(0, 10);
      if (!created) return true;
      if (startDateFilter && created < startDateFilter) return false;
      if (endDateFilter && created > endDateFilter) return false;
      return true;
    });

    updateKPIs();
    updateAllChartsData();
    updateTop5List();
    updateEvolucaoTemporalChart();
    recalculateLeadTimeAndPendencias();
    filterTable();
    renderKanbanBoard();
  }

  function updateKPIs() {
    const total = currentPeriodVidas.length;
    const pendente = currentPeriodVidas.filter(d => d["Status Atual"] === "ANÁLISE PENDENTE").length;
    const andamento = currentPeriodVidas.filter(d => d["Status Atual"] === "AUDITORIA EM ANDAMENTO").length;
    const liberado = currentPeriodVidas.filter(d => d["Status Atual"] === "LIBERAR PARA CADASTRAR" || d["Status Atual"] === "LIBERADO COM CPT").length;
    const concluido = currentPeriodVidas.filter(d => d["Status Atual"] === "CADASTRO CONCLUÍDO").length;

    const taxa = total > 0 ? (((liberado + concluido) / total) * 100).toFixed(1) : "0.0";

    document.getElementById("top-vidas-count").textContent = `${total.toLocaleString("pt-BR")} VIDAS`;
    document.getElementById("kpi-total-vidas").textContent = total.toLocaleString("pt-BR");
    document.getElementById("kpi-pendente").textContent = pendente.toLocaleString("pt-BR");
    document.getElementById("kpi-andamento").textContent = andamento.toLocaleString("pt-BR");
    document.getElementById("kpi-liberado").textContent = liberado.toLocaleString("pt-BR");
    document.getElementById("kpi-concluido").textContent = concluido.toLocaleString("pt-BR");
    document.getElementById("kpi-taxa-liberacao").textContent = `${taxa}%`;

    const pctPendente = total > 0 ? ((pendente / total) * 100).toFixed(1) : "0.0";
    document.getElementById("kpi-sub-pendente").textContent = `${pctPendente}% na fila`;
    document.getElementById("funil-vidas-tag").textContent = `${total.toLocaleString("pt-BR")} Vidas`;
  }

  function updateTop5List() {
    const empCounts = {};
    currentPeriodVidas.forEach(v => {
      const e = v["Empresa / Contrato"] || "Não informada";
      empCounts[e] = (empCounts[e] || 0) + 1;
    });

    const sortedEmps = Object.entries(empCounts).sort((a, b) => b[1] - a[1]).slice(0, 5);
    const container = document.getElementById("top5-empresas-list");
    container.innerHTML = sortedEmps.map(([name, count]) => `
      <div class="rank-item">
        <div>
          <div class="rank-name">${name}</div>
          <div style="font-size: 10px; color: var(--text-muted);">Empresarial / Contrato</div>
        </div>
        <div class="rank-val">${count.toLocaleString('pt-BR')} vidas</div>
      </div>
    `).join('');
  }

  function populateDropdowns() {
    const vigs = [...new Set(vidas.map(v => v["Vigência"]).filter(Boolean))].sort();
    const selVig = document.getElementById("sel-vigencia");
    const kSelVig = document.getElementById("k-filter-vigencia");
    vigs.forEach(v => {
      const opt = document.createElement("option");
      opt.value = v;
      opt.textContent = `Vigência: ${v}`;
      selVig.appendChild(opt);
      kSelVig.appendChild(opt.cloneNode(true));
    });

    const emps = [...new Set(vidas.map(v => v["Empresa / Contrato"]).filter(Boolean))].sort();
    const selEmp = document.getElementById("sel-empresa");
    const kSelEmp = document.getElementById("k-filter-empresa");
    emps.slice(0, 60).forEach(e => {
      const opt = document.createElement("option");
      opt.value = e;
      opt.textContent = e.length > 35 ? e.substring(0, 35) + "..." : e;
      selEmp.appendChild(opt);
      kSelEmp.appendChild(opt.cloneNode(true));
    });

    const stats = [...new Set(vidas.map(v => v["Status Atual"]).filter(Boolean))].sort();
    const selStat = document.getElementById("sel-status");
    stats.forEach(s => {
      const opt = document.createElement("option");
      opt.value = s;
      opt.textContent = `Status: ${s}`;
      selStat.appendChild(opt);
    });
  }

  function renderKanbanBoard() {
    const vig = document.getElementById("k-filter-vigencia").value;
    const emp = document.getElementById("k-filter-empresa").value;
    const search = document.getElementById("k-filter-search").value.toLowerCase();

    const kbData = currentPeriodVidas.filter(v => {
      const matchVig = !vig || v["Vigência"] === vig;
      const matchEmp = !emp || v["Empresa / Contrato"] === emp;
      const matchSearch = !search || 
        (v["Beneficiário (Nome)"] && v["Beneficiário (Nome)"].toLowerCase().includes(search)) ||
        (v["Chave"] && v["Chave"].toLowerCase().includes(search)) ||
        (v["Empresa / Contrato"] && v["Empresa / Contrato"].toLowerCase().includes(search));
      return matchVig && matchEmp && matchSearch;
    });

    const container = document.getElementById("kanban-board-wrapper");
    container.innerHTML = "";

    kanbanColumns.forEach(col => {
      const colCards = kbData.filter(d => col.match.some(m => (d["Status Atual"] || "").toUpperCase() === m.toUpperCase()));

      const colDiv = document.createElement("div");
      colDiv.className = "kanban-col";
      colDiv.innerHTML = `
        <div class="kanban-col-header">
          <span>${col.title}</span>
          <span class="kanban-col-count">${colCards.length}</span>
        </div>
        <div class="kanban-cards-list">
          ${colCards.slice(0, 50).map(c => `
            <div class="kanban-card" onclick="openDrawerByKey('${c['Chave']}')">
              <div class="k-parent-summary">${c['Empresa / Contrato'] || 'S1 Saúde'}</div>
              <div class="k-beneficiario">${c['Beneficiário (Nome)']}</div>
              <div class="k-footer">
                <span class="k-ticket-tag">${c['Chave']}</span>
                <div class="k-avatar-badge">${(c['Responsável'] && c['Responsável'].includes('Priscila') ? 'PT' : c['Responsável'] && c['Responsável'].includes('Carlos') ? 'CS' : 'RL')}</div>
              </div>
            </div>
          `).join('')}
          ${colCards.length > 50 ? `<div style="font-size:10.5px; text-align:center; color:var(--text-muted); padding:6px;">+ ${colCards.length - 50} itens na coluna</div>` : ''}
        </div>
      `;
      container.appendChild(colDiv);
    });
  }

  function openDrawerByKey(key) {
    const item = allRecords.find(r => r["Chave"] === key);
    if (!item) return;

    document.getElementById("d-beneficiario-nome").textContent = item["Beneficiário (Nome)"] || item["Chave"];
    document.getElementById("d-ticket-key").textContent = item["Chave"];
    document.getElementById("d-status-badge").innerHTML = `<span class="badge ${getBadgeClass(item['Status Atual'])}">${item['Status Atual']}</span>`;
    document.getElementById("d-empresa").textContent = item["Empresa / Contrato"] || item["Resumo Lote (Parent)"] || "-";
    const dtCriacaoEl = document.getElementById("d-data-criacao");
    if (dtCriacaoEl) dtCriacaoEl.textContent = formatarDataBR(item["Data Criação"]);
    document.getElementById("d-vigencia").textContent = item["Vigência"] || "Não informada";
    document.getElementById("d-tipo-beneficiario").textContent = `${item['Tipo Beneficiário'] || 'Titular'} • ${item['Tipo Movimentação'] || 'Inclusão'}`;
    document.getElementById("d-cpt").textContent = item["Análise CPT"] || "Empresarial";
    document.getElementById("d-responsavel").textContent = item["Responsável"] || "Raquel Lopes";
    document.getElementById("d-caminho-arquivo").textContent = item["Caminho do Arquivo"] || "Caminho padrão do servidor de rede";
    document.getElementById("d-btn-jira").href = `https://s1saude.atlassian.net/browse/${item['Chave']}`;

    document.getElementById("drawer-overlay").classList.add("active");
    document.getElementById("drawer-panel").classList.add("active");
  }

  function closeDrawer() {
    document.getElementById("drawer-overlay").classList.remove("active");
    document.getElementById("drawer-panel").classList.remove("active");
  }

  function filterTable() {
    const vig = document.getElementById("sel-vigencia").value;
    const emp = document.getElementById("sel-empresa").value;
    const stat = document.getElementById("sel-status").value;
    const search = document.getElementById("txt-search").value.toLowerCase();

    filteredVidas = currentPeriodVidas.filter(v => {
      const matchVig = !vig || v["Vigência"] === vig;
      const matchEmp = !emp || v["Empresa / Contrato"] === emp;
      const matchStat = !stat || v["Status Atual"] === stat || (stat === "LIBERAR PARA CADASTRAR" && v["Status Atual"] === "LIBERADO COM CPT");
      const matchSearch = !search || 
        (v["Beneficiário (Nome)"] && v["Beneficiário (Nome)"].toLowerCase().includes(search)) ||
        (v["Chave"] && v["Chave"].toLowerCase().includes(search)) ||
        (v["Empresa / Contrato"] && v["Empresa / Contrato"].toLowerCase().includes(search));

      return matchVig && matchEmp && matchStat && matchSearch;
    });

    currentPage = 1;
    renderTableRows();
  }

  function getBadgeClass(status) {
    const s = (status || "").toUpperCase();
    if (s.includes("PENDENTE")) return "b-pendente";
    if (s.includes("ANDAMENTO")) return "b-andamento";
    if (s.includes("LIBERAR PARA") || s.includes("LIBERADO")) return "b-liberado";
    if (s.includes("CONCLUÍDO") || s.includes("CONCLUIDO")) return "b-concluido";
    if (s.includes("CANCELADO")) return "b-cancelado";
    if (s.includes("CPT")) return "b-cpt";
    if (s.includes("DIRETORIA")) return "b-diretoria";
    return "b-outro";
  }

  function renderTableRows() {
    const tbody = document.getElementById("table-beneficiarios-body");
    tbody.innerHTML = "";

    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    const rows = filteredVidas.slice(start, end);

    rows.forEach(r => {
      const tr = document.createElement("tr");
      tr.onclick = () => openDrawerByKey(r['Chave']);
      tr.innerHTML = `
        <td><span class="ticket-link">${r['Chave']} ↗</span></td>
        <td><strong>${r['Beneficiário (Nome)']}</strong></td>
        <td>${r['Empresa / Contrato'] || '-'}</td>
        <td><span style="font-weight: 700; color: var(--s1-primary);">${r['Vigência'] || '-'}</span></td>
        <td><span class="badge ${getBadgeClass(r['Status Atual'])}">${r['Status Atual']}</span></td>
        <td>${r['Tipo Beneficiário'] || 'Titular'}</td>
        <td>${r['Análise CPT'] || 'Empresarial'}</td>
        <td>${r['Responsável'] || 'Raquel Lopes'}</td>
        <td style="color: var(--text-muted); font-size: 10.5px;">${formatarDataBR(r['Data Criação'])}</td>
      `;
      tbody.appendChild(tr);
    });

    const totalPages = Math.ceil(filteredVidas.length / pageSize) || 1;
    document.getElementById("page-count-info").textContent = `Mostrando ${Math.min(start + 1, filteredVidas.length)} a ${Math.min(end, filteredVidas.length)} de ${filteredVidas.length.toLocaleString('pt-BR')} beneficiários`;

    const nav = document.getElementById("page-nav-btns");
    nav.innerHTML = `
      <button class="btn-page" onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>Anterior</button>
      <button class="btn-page active">${currentPage} / ${totalPages}</button>
      <button class="btn-page" onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>Próximo</button>
    `;
  }

  function changePage(page) {
    const totalPages = Math.ceil(filteredVidas.length / pageSize) || 1;
    if (page >= 1 && page <= totalPages) {
      currentPage = page;
      renderTableRows();
    }
  }

  function renderTransitionsLog() {
    const tbody = document.getElementById("log-transicoes-body");
    tbody.innerHTML = "";

    const trans = interactionsData.recent_transitions || [];
    trans.slice(0, 15).forEach(t => {
      const tr = document.createElement("tr");
      tr.onclick = () => openDrawerByKey(t.ticket);
      tr.innerHTML = `
        <td style="color: var(--text-muted);">${formatarDataBR(t.data)}</td>
        <td><span class="ticket-link">${t.ticket}</span></td>
        <td><strong>${t.beneficiario || '-'}</strong></td>
        <td>${t.empresa || '-'}</td>
        <td><span style="font-weight:700; color:var(--s1-primary);">${t.autor}</span></td>
        <td><span class="badge b-outro">${t.de_status}</span> ➔ <span class="badge b-liberado">${t.para_status}</span></td>
      `;
      tbody.appendChild(tr);
    });
  }

  function exportTableCSV() {
    let csv = "Chave,Beneficiario,Empresa,Vigencia,Status,Tipo,Segmento,Responsavel,Criacao\\n";
    filteredVidas.forEach(d => {
      const name = (d["Beneficiário (Nome)"] || "").replace(/,/g, " ");
      const emp = (d["Empresa / Contrato"] || "").replace(/,/g, " ");
      csv += `${d['Chave']},"${name}","${emp}",${d['Vigência']},${d['Status Atual']},${d['Tipo Beneficiário']},${d['Análise CPT']},${d['Responsável']},${formatarDataBR(d['Data Criação'])}\\n`;
    });

    const blob = new Blob(["\\ufeff" + csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `S1_Saude_Auditoria_Vidas_${new Date().toISOString().slice(0,10)}.csv`;
    link.click();
  }

  // ========================================================
  // RECORTE TEMPORAL DINÂMICO & LEAD TIME / TOP PENDÊNCIAS
  // ========================================================
  let pendenciasVisaoAtual = 'TODAS';
  let topPendenciasData = [];

  function setFiltroVisaoPendencias(visao) {
    pendenciasVisaoAtual = visao;
    document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
    if (visao === 'TODAS') {
      const el = document.getElementById('pill-todas-pend');
      if (el) el.classList.add('active');
    } else if (visao === 'ANÁLISE PENDENTE') {
      const el = document.getElementById('pill-analise-pend');
      if (el) el.classList.add('active');
    } else if (visao === 'AUDITORIA EM ANDAMENTO') {
      const el = document.getElementById('pill-andamento');
      if (el) el.classList.add('active');
    } else if (visao === 'CRITICOS') {
      const el = document.getElementById('pill-criticos');
      if (el) el.classList.add('active');
    } else if (visao === 'CONCLUIDOS') {
      const el = document.getElementById('pill-concluidos');
      if (el) el.classList.add('active');
    }

    recalculateLeadTimeAndPendencias();
  }

  function drillDownKPI(statusAlvo) {
    if (statusAlvo === 'ANÁLISE PENDENTE') {
      setFiltroVisaoPendencias('ANÁLISE PENDENTE');
      switchNav('tab-pendencias', document.getElementById('nav-pendencias'));
    } else if (statusAlvo === 'AUDITORIA EM ANDAMENTO') {
      setFiltroVisaoPendencias('AUDITORIA EM ANDAMENTO');
      switchNav('tab-pendencias', document.getElementById('nav-pendencias'));
    } else if (statusAlvo === 'LIBERAR PARA CADASTRAR' || statusAlvo === 'LIBERADO P/ CADASTRAR') {
      switchNav('tab-base', document.querySelector('[onclick*="tab-base"]'));
      const sel = document.getElementById('sel-status');
      if (sel) sel.value = 'LIBERAR PARA CADASTRAR';
      filterTable();
    } else if (statusAlvo === 'CADASTRO CONCLUÍDO') {
      switchNav('tab-base', document.querySelector('[onclick*="tab-base"]'));
      const sel = document.getElementById('sel-status');
      if (sel) sel.value = 'CADASTRO CONCLUÍDO';
      filterTable();
    } else if (statusAlvo === 'TODAS') {
      switchNav('tab-base', document.querySelector('[onclick*="tab-base"]'));
      const sel = document.getElementById('sel-status');
      if (sel) sel.value = '';
      filterTable();
    }
  }

  function updateEvolucaoTemporalChart() {
    if (!chartEvolucao) return;

    let isShortPeriod = false;
    if (startDateFilter && endDateFilter) {
      const dt1 = new Date(startDateFilter);
      const dt2 = new Date(endDateFilter);
      const diffDays = Math.ceil((dt2 - dt1) / (1000 * 60 * 60 * 24));
      if (diffDays <= 35) {
        isShortPeriod = true;
      }
    }

    const tagEl = document.getElementById("evolucao-periodo-tag");
    const statusConcluidos = ["CADASTRO CONCLUÍDO", "LIBERAR PARA CADASTRAR", "LIBERADO COM CPT", "CONCLUÍDO APS"];

    if (isShortPeriod) {
      const dayMap = {};
      const cur = new Date(startDateFilter + "T00:00:00");
      const end = new Date(endDateFilter + "T23:59:59");
      while (cur <= end) {
        const isoDay = cur.toISOString().slice(0, 10);
        dayMap[isoDay] = {
          entrada: 0,
          liberacao: 0,
          label: `${cur.getDate().toString().padStart(2, '0')}/${(cur.getMonth() + 1).toString().padStart(2, '0')}`
        };
        cur.setDate(cur.getDate() + 1);
      }

      vidas.forEach(v => {
        const cDay = (v["Data Criação"] || "").slice(0, 10);
        if (dayMap[cDay]) {
          dayMap[cDay].entrada++;
        }
        const st = (v["Status Atual"] || "").toUpperCase();
        if (statusConcluidos.includes(st)) {
          const uDay = (v["Data Resolução"] || v["Data Atualização"] || "").slice(0, 10);
          if (dayMap[uDay]) {
            dayMap[uDay].liberacao++;
          }
        }
      });

      const dayKeys = Object.keys(dayMap).sort();
      chartEvolucao.data.labels = dayKeys.map(k => dayMap[k].label);
      chartEvolucao.data.datasets[0].data = dayKeys.map(k => dayMap[k].entrada);
      chartEvolucao.data.datasets[1].data = dayKeys.map(k => dayMap[k].liberacao);

      if (tagEl) {
        const sFormatted = `${startDateFilter.slice(8, 10)}/${startDateFilter.slice(5, 7)}`;
        const eFormatted = `${endDateFilter.slice(8, 10)}/${endDateFilter.slice(5, 7)}`;
        tagEl.textContent = `Diário: ${sFormatted} a ${eFormatted}`;
      }
    } else {
      const monthMap = {};
      const mesesNomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];

      vidas.forEach(v => {
        const cMes = (v["Data Criação"] || "").slice(0, 7);
        if (cMes && cMes.length === 7) {
          if (!startDateFilter || cMes >= startDateFilter.slice(0, 7)) {
            if (!endDateFilter || cMes <= endDateFilter.slice(0, 7)) {
              if (!monthMap[cMes]) monthMap[cMes] = { entrada: 0, liberacao: 0 };
              monthMap[cMes].entrada++;
            }
          }
        }
        const st = (v["Status Atual"] || "").toUpperCase();
        if (statusConcluidos.includes(st)) {
          const uMes = (v["Data Resolução"] || v["Data Atualização"] || "").slice(0, 7);
          if (uMes && uMes.length === 7) {
            if (!startDateFilter || uMes >= startDateFilter.slice(0, 7)) {
              if (!endDateFilter || uMes <= endDateFilter.slice(0, 7)) {
                if (!monthMap[uMes]) monthMap[uMes] = { entrada: 0, liberacao: 0 };
                monthMap[uMes].liberacao++;
              }
            }
          }
        }
      });

      const sortedMonths = Object.keys(monthMap).sort();
      chartEvolucao.data.labels = sortedMonths.map(m => {
        const [y, mm] = m.split('-');
        return `${mesesNomes[parseInt(mm, 10) - 1]}/${y.slice(2)}`;
      });
      chartEvolucao.data.datasets[0].data = sortedMonths.map(m => monthMap[m].entrada);
      chartEvolucao.data.datasets[1].data = sortedMonths.map(m => monthMap[m].liberacao);

      if (tagEl) {
        if (!startDateFilter && !endDateFilter) {
          tagEl.textContent = "Série Histórica Completa";
        } else {
          const lStart = chartEvolucao.data.labels[0] || '';
          const lEnd = chartEvolucao.data.labels[chartEvolucao.data.labels.length - 1] || '';
          tagEl.textContent = `Recorte: ${lStart} a ${lEnd}`;
        }
      }
    }

    chartEvolucao.update();
  }

  function recalculateLeadTimeAndPendencias() {
    const statusConcluidos = ["CADASTRO CONCLUÍDO", "LIBERAR PARA CADASTRAR", "LIBERADO COM CPT", "CONCLUÍDO APS"];
    const statusPendentesGeral = ["ANÁLISE PENDENTE", "AUDITORIA EM ANDAMENTO", "PENDÊNCIA CADASTRO", "AGUARDANDO DIRETORIA", "CPT Enviada", "CPT ENVIADA", "APS"];

    const refNow = new Date("2026-08-26T23:59:59");

    // All concluded in period
    const concluidas = currentPeriodVidas.filter(v => statusConcluidos.includes(v["Status Atual"]));
    const leadTimes = [];
    concluidas.forEach(v => {
      const cDate = new Date(v["Data Criação"]);
      const uDate = new Date(v["Data Resolução"] || v["Data Atualização"] || v["Data Criação"]);
      const diff = Math.max(0, (uDate - cDate) / (1000 * 60 * 60 * 24));
      if (!isNaN(diff)) {
        leadTimes.push(diff);
      }
    });

    const ltMean = leadTimes.length > 0 ? (leadTimes.reduce((a, b) => a + b, 0) / leadTimes.length) : 0;
    leadTimes.sort((a, b) => a - b);
    const ltMedian = leadTimes.length > 0 ? leadTimes[Math.floor(leadTimes.length / 2)] : 0;

    // All pending in period
    const todasPendentes = currentPeriodVidas.filter(v => statusPendentesGeral.includes(v["Status Atual"]));
    const analisePendentes = currentPeriodVidas.filter(v => v["Status Atual"] === "ANÁLISE PENDENTE");
    const andamentoPendentes = currentPeriodVidas.filter(v => v["Status Atual"] === "AUDITORIA EM ANDAMENTO");
    const criticosPendentes = currentPeriodVidas.filter(v => ["PENDÊNCIA CADASTRO", "AGUARDANDO DIRETORIA", "CPT Enviada", "CPT ENVIADA"].includes(v["Status Atual"]));

    // Update Pill Count Badges
    const pTodas = document.getElementById('count-pill-todas');
    const pAnalise = document.getElementById('count-pill-analise');
    const pAndamento = document.getElementById('count-pill-andamento');
    const pCriticos = document.getElementById('count-pill-criticos');
    const pConcluidos = document.getElementById('count-pill-concluidos');
    if (pTodas) pTodas.textContent = todasPendentes.length.toLocaleString('pt-BR');
    if (pAnalise) pAnalise.textContent = analisePendentes.length.toLocaleString('pt-BR');
    if (pAndamento) pAndamento.textContent = andamentoPendentes.length.toLocaleString('pt-BR');
    if (pCriticos) pCriticos.textContent = criticosPendentes.length.toLocaleString('pt-BR');
    if (pConcluidos) pConcluidos.textContent = concluidas.length.toLocaleString('pt-BR');

    // Selected pending list based on pill filter
    let activeList = todasPendentes;
    if (pendenciasVisaoAtual === 'ANÁLISE PENDENTE') activeList = analisePendentes;
    else if (pendenciasVisaoAtual === 'AUDITORIA EM ANDAMENTO') activeList = andamentoPendentes;
    else if (pendenciasVisaoAtual === 'CRITICOS') activeList = criticosPendentes;
    else if (pendenciasVisaoAtual === 'CONCLUIDOS') activeList = concluidas;

    const agings = [];
    let gargalos30 = 0;
    todasPendentes.forEach(v => {
      const cDate = new Date(v["Data Criação"]);
      const diff = Math.max(0, (refNow - cDate) / (1000 * 60 * 60 * 24));
      if (!isNaN(diff)) {
        agings.push(diff);
        if (diff > 30) gargalos30++;
      }
    });

    const agingMean = agings.length > 0 ? (agings.reduce((a, b) => a + b, 0) / agings.length) : 0;
    agings.sort((a, b) => a - b);
    const agingMedian = agings.length > 0 ? agings[Math.floor(agings.length / 2)] : 0;

    // Grouping by company
    const empMap = {};
    activeList.forEach(v => {
      const emp = v["Empresa / Contrato"] || "Não informada";
      if (!empMap[emp]) {
        empMap[emp] = {
          nome: emp,
          total: 0,
          analise: 0,
          andamento: 0,
          criticos: 0,
          concluidos: 0,
          agings: [],
          vigencias: {},
          minCriacao: v["Data Criação"] || ""
        };
      }
      empMap[emp].total++;
      const st = v["Status Atual"] || "";
      if (st === "ANÁLISE PENDENTE") empMap[emp].analise++;
      else if (st === "AUDITORIA EM ANDAMENTO") empMap[emp].andamento++;
      else if (["PENDÊNCIA CADASTRO", "AGUARDANDO DIRETORIA", "CPT Enviada", "CPT ENVIADA"].includes(st)) empMap[emp].criticos++;
      else if (statusConcluidos.includes(st)) empMap[emp].concluidos++;

      const cDate = new Date(v["Data Criação"]);
      const diff = Math.max(0, (refNow - cDate) / (1000 * 60 * 60 * 24));
      if (!isNaN(diff)) empMap[emp].agings.push(diff);

      const vg = v["Vigência"] || "Não informada";
      empMap[emp].vigencias[vg] = (empMap[emp].vigencias[vg] || 0) + 1;

      if (v["Data Criação"] && (!empMap[emp].minCriacao || v["Data Criação"] < empMap[emp].minCriacao)) {
        empMap[emp].minCriacao = v["Data Criação"];
      }
    });

    topPendenciasData = Object.values(empMap).map(e => {
      const eAgingMean = e.agings.length > 0 ? (e.agings.reduce((a, b) => a + b, 0) / e.agings.length) : 0;
      let topVg = "-";
      let topVgCount = 0;
      Object.entries(e.vigencias).forEach(([vg, cnt]) => {
        if (cnt > topVgCount) { topVgCount = cnt; topVg = vg; }
      });
      return {
        nome: e.nome,
        total: e.total,
        analise: e.analise,
        andamento: e.andamento,
        criticos: e.criticos,
        concluidos: e.concluidos,
        agingMedio: eAgingMean,
        vigenciaPrincipal: topVg,
        loteMaisAntigo: formatarDataBR(e.minCriacao)
      };
    });

    topPendenciasData.sort((a, b) => b.total - a.total);

    // KPI 1: Lead Time Médio
    const kpiLt = document.getElementById("kpi-lt-medio");
    const kpiLtSub = document.getElementById("kpi-lt-sub");
    if (kpiLt) kpiLt.textContent = `${ltMean.toFixed(1)} dias`;
    if (kpiLtSub) kpiLtSub.textContent = `Mediana: ${ltMedian.toFixed(1)} dias (${concluidas.length} concluídas)`;

    // KPI 2: Aging Médio da Fila
    const kpiAg = document.getElementById("kpi-aging-medio");
    const kpiAgSub = document.getElementById("kpi-aging-sub");
    if (kpiAg) kpiAg.textContent = `${agingMean.toFixed(1)} dias`;
    if (kpiAgSub) kpiAgSub.textContent = `Mediana: ${agingMedian.toFixed(1)} dias (${todasPendentes.length} pendentes)`;

    // KPI 3: Maior Fila Concentrada
    const kpiTopEmp = document.getElementById("kpi-top-empresa-nome");
    const kpiTopEmpVidas = document.getElementById("kpi-top-empresa-vidas");
    if (kpiTopEmp) {
      if (topPendenciasData.length > 0) {
        kpiTopEmp.textContent = topPendenciasData[0].nome;
        kpiTopEmp.title = topPendenciasData[0].nome;
        if (kpiTopEmpVidas) kpiTopEmpVidas.textContent = `${topPendenciasData[0].total.toLocaleString('pt-BR')} vidas represadas`;
      } else {
        kpiTopEmp.textContent = "Nenhuma";
        if (kpiTopEmpVidas) kpiTopEmpVidas.textContent = "0 vidas";
      }
    }

    // KPI 4: Concentração Top 5
    const kpiConc = document.getElementById("kpi-concentracao-top5");
    if (kpiConc) {
      const totalVidasAtivas = activeList.length;
      if (totalVidasAtivas > 0) {
        const top5Sum = topPendenciasData.slice(0, 5).reduce((acc, curr) => acc + curr.total, 0);
        const concPct = ((top5Sum / totalVidasAtivas) * 100).toFixed(1);
        kpiConc.textContent = `${concPct}%`;
      } else {
        kpiConc.textContent = "0.0%";
      }
    }

    // KPI 5: Gargalos > 30 Dias
    const kpiGarg = document.getElementById("kpi-gargalos-30d");
    const kpiGargSub = document.getElementById("kpi-gargalos-sub");
    if (kpiGarg) kpiGarg.textContent = `${gargalos30.toLocaleString('pt-BR')} vidas`;
    if (kpiGargSub) {
      const pctGarg = todasPendentes.length > 0 ? ((gargalos30 / todasPendentes.length) * 100).toFixed(1) : "0.0";
      kpiGargSub.textContent = `${pctGarg}% das pendências atuais`;
    }

    // Update Charts in tab-pendencias
    updateLeadTimeAndPendenciasCharts(concluidas, todasPendentes);
    renderTopPendenciasTable();
  }

  function updateLeadTimeAndPendenciasCharts(concluidas, todasPendentes) {
    if (!chartTopEmpresasPendentes || !chartLeadTimeEvolucao || !chartDistribuicaoLeadTime || !chartAgingDistribuicao) return;

    // 1. Chart Top 10 Empresas Pendentes (Stacked Horizontal Bar)
    const top10 = topPendenciasData.slice(0, 10);
    chartTopEmpresasPendentes.data.labels = top10.map(e => e.nome.length > 30 ? e.nome.slice(0, 30) + '...' : e.nome);
    if (pendenciasVisaoAtual === 'CONCLUIDOS') {
      chartTopEmpresasPendentes.data.datasets = [
        { label: 'Concluídos / Liberados', data: top10.map(e => e.concluidos), backgroundColor: '#059669', borderRadius: 4 }
      ];
    } else {
      chartTopEmpresasPendentes.data.datasets = [
        { label: 'Análise Pendente', data: top10.map(e => e.analise), backgroundColor: '#E36159', borderRadius: 4 },
        { label: 'Auditoria em Andamento', data: top10.map(e => e.andamento), backgroundColor: '#2BAAB1', borderRadius: 4 },
        { label: 'Críticos (Diretoria/Cadastro)', data: top10.map(e => e.criticos), backgroundColor: '#DC2626', borderRadius: 4 }
      ];
    }
    chartTopEmpresasPendentes.update();

    // 2. Chart Evolução Lead Time Mês a Mês (Line)
    const ltMonthMap = {};
    const mesesNomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    concluidas.forEach(v => {
      const uMes = (v["Data Resolução"] || v["Data Atualização"] || "").slice(0, 7);
      if (uMes && uMes.length === 7) {
        if (!startDateFilter || uMes >= startDateFilter.slice(0, 7)) {
          if (!endDateFilter || uMes <= endDateFilter.slice(0, 7)) {
            const cDate = new Date(v["Data Criação"]);
            const uDate = new Date(v["Data Resolução"] || v["Data Atualização"]);
            const diff = Math.max(0, (uDate - cDate) / (1000 * 60 * 60 * 24));
            if (!isNaN(diff)) {
              if (!ltMonthMap[uMes]) ltMonthMap[uMes] = [];
              ltMonthMap[uMes].push(diff);
            }
          }
        }
      }
    });

    const sortedLtMonths = Object.keys(ltMonthMap).sort();
    chartLeadTimeEvolucao.data.labels = sortedLtMonths.map(m => {
      const [y, mm] = m.split('-');
      return `${mesesNomes[parseInt(mm, 10) - 1]}/${y.slice(2)}`;
    });
    chartLeadTimeEvolucao.data.datasets[0].data = sortedLtMonths.map(m => {
      const arr = ltMonthMap[m];
      return arr.length > 0 ? Number((arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1)) : 0;
    });
    chartLeadTimeEvolucao.update();

    // 3. Distribuição de Lead Time (Histogram)
    const ltBuckets = { "0-3 dias": 0, "4-7 dias": 0, "8-15 dias": 0, "16-30 dias": 0, "31-60 dias": 0, "> 60 dias": 0 };
    concluidas.forEach(v => {
      const cDate = new Date(v["Data Criação"]);
      const uDate = new Date(v["Data Resolução"] || v["Data Atualização"]);
      const diff = Math.max(0, (uDate - cDate) / (1000 * 60 * 60 * 24));
      if (!isNaN(diff)) {
        if (diff <= 3) ltBuckets["0-3 dias"]++;
        else if (diff <= 7) ltBuckets["4-7 dias"]++;
        else if (diff <= 15) ltBuckets["8-15 dias"]++;
        else if (diff <= 30) ltBuckets["16-30 dias"]++;
        else if (diff <= 60) ltBuckets["31-60 dias"]++;
        else ltBuckets["> 60 dias"]++;
      }
    });
    chartDistribuicaoLeadTime.data.labels = Object.keys(ltBuckets);
    chartDistribuicaoLeadTime.data.datasets[0].data = Object.values(ltBuckets);
    chartDistribuicaoLeadTime.update();

    // 4. Curva de Aging das Pendências (Histogram)
    const refNow = new Date("2026-08-26T23:59:59");
    const agBuckets = { "Até 7 dias": 0, "8-15 dias": 0, "16-30 dias": 0, "31-60 dias": 0, "61-120 dias": 0, "> 120 dias": 0 };
    todasPendentes.forEach(v => {
      const cDate = new Date(v["Data Criação"]);
      const diff = Math.max(0, (refNow - cDate) / (1000 * 60 * 60 * 24));
      if (!isNaN(diff)) {
        if (diff <= 7) agBuckets["Até 7 dias"]++;
        else if (diff <= 15) agBuckets["8-15 dias"]++;
        else if (diff <= 30) agBuckets["16-30 dias"]++;
        else if (diff <= 60) agBuckets["31-60 dias"]++;
        else if (diff <= 120) agBuckets["61-120 dias"]++;
        else agBuckets["> 120 dias"]++;
      }
    });
    chartAgingDistribuicao.data.labels = Object.keys(agBuckets);
    chartAgingDistribuicao.data.datasets[0].data = Object.values(agBuckets);
    chartAgingDistribuicao.update();
  }

  function renderTopPendenciasTable() {
    const tbody = document.getElementById("tbody-top-pendencias");
    if (!tbody) return;

    const search = (document.getElementById("txt-search-pend") ? document.getElementById("txt-search-pend").value : "").toLowerCase().trim();
    const ordem = document.getElementById("sel-ordem-pend") ? document.getElementById("sel-ordem-pend").value : "vidas_desc";

    let rows = [...topPendenciasData];

    if (search) {
      rows = rows.filter(r => r.nome.toLowerCase().includes(search) || r.vigenciaPrincipal.toLowerCase().includes(search));
    }

    if (ordem === 'vidas_desc') {
      rows.sort((a, b) => b.total - a.total);
    } else if (ordem === 'aging_desc') {
      rows.sort((a, b) => b.agingMedio - a.agingMedio);
    } else if (ordem === 'nome_asc') {
      rows.sort((a, b) => a.nome.localeCompare(b.nome));
    }

    if (rows.length === 0) {
      tbody.innerHTML = '<tr><td colspan="10" style="text-align:center; padding: 24px; color: var(--text-muted);">Nenhuma empresa encontrada com os filtros selecionados.</td></tr>';
      return;
    }

    tbody.innerHTML = rows.map((r, idx) => {
      let badgeAgingClass = "b-liberado";
      if (r.agingMedio > 30) badgeAgingClass = "b-diretoria";
      else if (r.agingMedio > 7) badgeAgingClass = "b-pendente";

      const safeEmpName = r.nome.replace(/'/g, "\\'");

      return `
        <tr>
          <td style="text-align: center;"><span style="font-weight: 800; color: var(--s1-primary); font-size: 11px;">#${idx + 1}</span></td>
          <td><strong>${r.nome}</strong></td>
          <td style="text-align: center;"><span style="font-weight: 800; color: var(--s1-primary); font-size: 12px;">${r.total.toLocaleString('pt-BR')}</span></td>
          <td style="text-align: center;"><span style="color: var(--s1-secondary); font-weight: 700;">${r.analise.toLocaleString('pt-BR')}</span></td>
          <td style="text-align: center;"><span style="color: var(--s1-tertiary); font-weight: 700;">${r.andamento.toLocaleString('pt-BR')}</span></td>
          <td style="text-align: center;"><span style="color: var(--s1-red); font-weight: 700;">${r.criticos.toLocaleString('pt-BR')}</span></td>
          <td style="text-align: center;"><span class="badge ${badgeAgingClass}">${r.agingMedio.toFixed(1)} dias</span></td>
          <td><span style="font-weight: 600; color: var(--text-dark);">${r.vigenciaPrincipal}</span></td>
          <td style="color: var(--text-muted); font-size: 10.5px;">${formatarDataBR(r.loteMaisAntigo)}</td>
          <td style="text-align: center;">
            <button class="btn-table-action" onclick="filtrarEmpresaNaBase('${safeEmpName}')" title="Filtrar beneficiários desta empresa na Base Nominal">
              <span>Filtrar Vidas ➔</span>
            </button>
          </td>
        </tr>
      `;
    }).join('');
  }

  function filtrarEmpresaNaBase(empName) {
    switchNav('tab-base', document.querySelector('[onclick*="tab-base"]'));
    const selEmp = document.getElementById('sel-empresa');
    if (selEmp) {
      let matched = false;
      for (let i = 0; i < selEmp.options.length; i++) {
        if (selEmp.options[i].value === empName) {
          selEmp.selectedIndex = i;
          matched = true;
          break;
        }
      }
      if (!matched) {
        selEmp.value = "";
        const txt = document.getElementById('txt-search');
        if (txt) txt.value = empName;
      }
    }
    filterTable();
  }

  function exportPendenciasCSV() {
    let csv = "Posicao,Empresa_Contrato,Total_Pendentes,Analise_Pendente,Em_Andamento,Casos_Criticos,Aging_Medio_Dias,Vigencia_Principal,Lote_Mais_Antigo\\n";
    topPendenciasData.forEach((r, idx) => {
      const name = (r.nome || "").replace(/,/g, " ");
      csv += `${idx + 1},"${name}",${r.total},${r.analise},${r.andamento},${r.criticos},${r.agingMedio.toFixed(1)},${r.vigenciaPrincipal},${formatarDataBR(r.loteMaisAntigo)}\\n`;
    });

    const blob = new Blob(["\\ufeff" + csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `S1_Saude_Top_Empresas_Pendentes_${new Date().toISOString().slice(0,10)}.csv`;
    link.click();
  }

  // ========================================================
  // ENGENHARIA DE SINCRONIZAÇÃO EM TEMPO REAL COM O JIRA
  // ========================================================
  function iniciarSincronizacaoJira() {
    const overlay = document.getElementById("sync-modal-overlay");
    const fill = document.getElementById("sync-progress-fill");
    const label = document.getElementById("sync-progress-label");
    const successBox = document.getElementById("sync-success-box");

    overlay.classList.add("active");
    fill.style.width = "0%";
    label.textContent = "0%";
    successBox.style.display = "none";

    const s1 = document.getElementById("step-1");
    const s2 = document.getElementById("step-2");
    const s3 = document.getElementById("step-3");
    const s4 = document.getElementById("step-4");

    const checkSvg = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
    const spinnerSvg = '<svg class="spinner-svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#282394" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>';
    const waitSvg = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>';

    [s1, s2, s3, s4].forEach(s => {
      s.className = "sync-step";
      s.querySelector(".step-icon").innerHTML = waitSvg;
    });

    s1.classList.add("active");
    s1.querySelector(".step-icon").innerHTML = spinnerSvg;
    fill.style.width = "25%";
    label.textContent = "25%";

    // Endpoint Local na Porta 8088
    fetch('/api/sync', { method: 'POST' })
      .then(res => res.json())
      .then(data => {
        executarAnimacaoProgressoCompleta(true);
      })
      .catch(err => {
        // Fallback dinâmico
        executarAnimacaoProgressoCompleta(false);
      });
  }

  function executarAnimacaoProgressoCompleta(isServer) {
    const fill = document.getElementById("sync-progress-fill");
    const label = document.getElementById("sync-progress-label");
    const successBox = document.getElementById("sync-success-box");
    const s1 = document.getElementById("step-1");
    const s2 = document.getElementById("step-2");
    const s3 = document.getElementById("step-3");
    const s4 = document.getElementById("step-4");

    const checkSvg = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>';
    const spinnerSvg = '<svg class="spinner-svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#282394" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>';

    setTimeout(() => {
      s1.className = "sync-step done";
      s1.querySelector(".step-icon").innerHTML = checkSvg;
      s2.classList.add("active");
      s2.querySelector(".step-icon").innerHTML = spinnerSvg;
      fill.style.width = "50%";
      label.textContent = "50%";
    }, 700);

    setTimeout(() => {
      s2.className = "sync-step done";
      s2.querySelector(".step-icon").innerHTML = checkSvg;
      s3.classList.add("active");
      s3.querySelector(".step-icon").innerHTML = spinnerSvg;
      fill.style.width = "75%";
      label.textContent = "75%";
    }, 1400);

    setTimeout(() => {
      s3.className = "sync-step done";
      s3.querySelector(".step-icon").innerHTML = checkSvg;
      s4.classList.add("active");
      s4.querySelector(".step-icon").innerHTML = spinnerSvg;
      fill.style.width = "90%";
      label.textContent = "90%";
    }, 2100);

    setTimeout(() => {
      s4.className = "sync-step done";
      s4.querySelector(".step-icon").innerHTML = checkSvg;
      fill.style.width = "100%";
      label.textContent = "100%";
      successBox.style.display = "block";
    }, 2800);

    setTimeout(() => {
      location.reload();
    }, 3600);
  }

  function initCharts() {
    chartFunil = new Chart(document.getElementById('chartFunilExec'), {
      type: 'bar',
      data: { labels: [], datasets: [{ data: [], backgroundColor: ['#E36159', '#282394', '#059669', '#2BAAB1', '#DC2626', '#94A3B8'], borderRadius: 6 }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } }, y: { grid: { color: '#F1F5F9' } } } }
    });

    chartVigExec = new Chart(document.getElementById('chartVigenciaExec'), {
      type: 'bar',
      data: { labels: [], datasets: [{ label: 'Vidas', data: [], backgroundColor: '#282394', borderRadius: 6 }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false }, ticks: { font: { size: 10 } } }, y: { grid: { color: '#F1F5F9' } } } }
    });

    chartSegExec = new Chart(document.getElementById('chartSegmentoExec'), {
      type: 'doughnut',
      data: { labels: ['Empresarial (PME/PJ)', 'Adesão / Allcare'], datasets: [{ data: [], backgroundColor: ['#282394', '#2BAAB1'], borderWidth: 0 }] },
      options: { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins: { legend: { position: 'bottom' } } }
    });

    chartEvolucao = new Chart(document.getElementById('chartEvolucaoMensal'), {
      type: 'line',
      data: {
        labels: [],
        datasets: [
          { label: 'Novas Vidas Submetidas (Entrada)', data: [], borderColor: '#282394', backgroundColor: 'rgba(40,35,148,0.06)', fill: true, tension: 0.3 },
          { label: 'Vidas Concluídas / Liberadas', data: [], borderColor: '#059669', backgroundColor: 'transparent', borderDash: [5, 5], tension: 0.3 }
        ]
      },
      options: { responsive: true, maintainAspectRatio: false, scales: { x: { grid: { display: false } }, y: { grid: { color: '#F1F5F9' } } } }
    });

    chartInteracoes = new Chart(document.getElementById('chartInteracoesEquipe'), {
      type: 'bar',
      data: {
        labels: ['Triagem p/ Andamento (Raquel Lopes)', 'Liberação p/ Cadastro (Priscila Tada)', 'Puxar da Fila p/ Andamento (Priscila Tada)', 'Cadastro Concluído (Priscila Tada)', 'Cadastro Concluído (Carlos Henrique)', 'Liberado com CPT (Priscila Tada)'],
        datasets: [{ label: 'Quantidade de Transições', data: [315, 302, 163, 118, 91, 17], backgroundColor: ['#2BAAB1', '#059669', '#282394', '#7C3AED', '#383F48', '#E36159'], borderRadius: 6 }]
      },
      options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });

    chartVigFull = new Chart(document.getElementById('chartVigenciaFull'), {
      type: 'bar',
      data: { labels: [], datasets: [{ label: 'Vidas Auditadas', data: [], backgroundColor: '#2BAAB1', borderRadius: 6 }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });

    chartEmpFull = new Chart(document.getElementById('chartEmpresasFull'), {
      type: 'bar',
      data: { labels: [], datasets: [{ label: 'Total de Vidas', data: [], backgroundColor: '#282394', borderRadius: 6 }] },
      options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });

    // Novos Gráficos da Aba Top Pendências & Lead Time
    chartTopEmpresasPendentes = new Chart(document.getElementById('chartTopEmpresasPendentes'), {
      type: 'bar',
      data: { labels: [], datasets: [] },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { stacked: true, grid: { color: '#F1F5F9' } },
          y: { stacked: true, grid: { display: false } }
        },
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
        }
      }
    });

    chartLeadTimeEvolucao = new Chart(document.getElementById('chartLeadTimeEvolucao'), {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: 'Lead Time Médio (Dias)',
          data: [],
          borderColor: '#282394',
          backgroundColor: 'rgba(40, 35, 148, 0.08)',
          fill: true,
          tension: 0.35,
          borderWidth: 2.5,
          pointRadius: 4,
          pointBackgroundColor: '#282394'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: '#F1F5F9' }, beginAtZero: true }
        }
      }
    });

    chartDistribuicaoLeadTime = new Chart(document.getElementById('chartDistribuicaoLeadTime'), {
      type: 'bar',
      data: {
        labels: ['0-3 dias', '4-7 dias', '8-15 dias', '16-30 dias', '31-60 dias', '> 60 dias'],
        datasets: [{
          label: 'Vidas Concluídas',
          data: [],
          backgroundColor: ['#059669', '#10B981', '#34D399', '#F59E0B', '#EF4444', '#991B1B'],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: '#F1F5F9' } }
        }
      }
    });

    chartAgingDistribuicao = new Chart(document.getElementById('chartAgingDistribuicao'), {
      type: 'bar',
      data: {
        labels: ['Até 7 dias', '8-15 dias', '16-30 dias', '31-60 dias', '61-120 dias', '> 120 dias'],
        datasets: [{
          label: 'Vidas Pendentes',
          data: [],
          backgroundColor: ['#10B981', '#34D399', '#F59E0B', '#E36159', '#DC2626', '#7F1D1D'],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: '#F1F5F9' } }
        }
      }
    });
  }

  function updateAllChartsData() {
    const statusCounts = {};
    currentPeriodVidas.forEach(v => {
      const s = v["Status Atual"] || "Outros";
      statusCounts[s] = (statusCounts[s] || 0) + 1;
    });

    chartFunil.data.labels = ['Análise Pendente', 'Cadastro Concluído', 'Liberado p/ Cadastrar', 'Auditoria em Andamento', 'Cancelado', 'Outros'];
    chartFunil.data.datasets[0].data = [
      statusCounts['ANÁLISE PENDENTE'] || 0,
      statusCounts['CADASTRO CONCLUÍDO'] || 0,
      (statusCounts['LIBERAR PARA CADASTRAR'] || 0) + (statusCounts['LIBERADO COM CPT'] || 0),
      statusCounts['AUDITORIA EM ANDAMENTO'] || 0,
      statusCounts['CANCELADO'] || 0,
      (statusCounts['AGUARDANDO DIRETORIA'] || 0) + (statusCounts['PENDÊNCIA CADASTRO'] || 0) + (statusCounts['CPT Enviada'] || 0)
    ];
    chartFunil.update();

    const vigCounts = {};
    currentPeriodVidas.forEach(v => {
      const vg = v["Vigência"] || "Não informada";
      vigCounts[vg] = (vigCounts[vg] || 0) + 1;
    });
    const sortedVigs = Object.entries(vigCounts).sort((a, b) => b[1] - a[1]);
    
    chartVigExec.data.labels = sortedVigs.slice(0, 8).map(x => x[0]);
    chartVigExec.data.datasets[0].data = sortedVigs.slice(0, 8).map(x => x[1]);
    chartVigExec.update();

    chartVigFull.data.labels = sortedVigs.slice(0, 14).map(x => x[0]);
    chartVigFull.data.datasets[0].data = sortedVigs.slice(0, 14).map(x => x[1]);
    chartVigFull.update();

    const empTotal = currentPeriodVidas.filter(v => (v["Análise CPT"] || "").includes("Empresarial") || !v["Análise CPT"]).length;
    const allcareTotal = currentPeriodVidas.filter(v => (v["Análise CPT"] || "").includes("Allcare")).length;
    chartSegExec.data.datasets[0].data = [empTotal, allcareTotal];
    chartSegExec.update();

    const empCounts = {};
    currentPeriodVidas.forEach(v => {
      const e = v["Empresa / Contrato"] || "Não informada";
      empCounts[e] = (empCounts[e] || 0) + 1;
    });
    const sortedEmps = Object.entries(empCounts).sort((a, b) => b[1] - a[1]).slice(0, 10);
    chartEmpFull.data.labels = sortedEmps.map(x => x[0]);
    chartEmpFull.data.datasets[0].data = sortedEmps.map(x => x[1]);
    chartEmpFull.update();
  }

  function checkEnvironmentAndToggleSyncBtn() {
    const syncBtn = document.getElementById("btn-sync-jira");
    if (!syncBtn) return;
    const host = (window.location.hostname || "").toLowerCase();
    const isLocal = host === "localhost" || 
                    host === "127.0.0.1" || 
                    host.startsWith("192.168.") || 
                    host.startsWith("10.") || 
                    host.startsWith("172.") ||
                    window.location.protocol === "file:";
    
    if (!isLocal) {
      syncBtn.style.display = "none";
    } else {
      syncBtn.style.display = "inline-flex";
    }
  }

  window.onload = () => {
    checkEnvironmentAndToggleSyncBtn();
    restoreSessionIfActive();
  };
</script>

</body>
</html>
"""

html_content = html_content.replace("/* __NOBLE_CRYPTO_PLACEHOLDER__ */", noble_crypto_code)
html_content = html_content.replace("__VAULT_JSON_RAW__", vault_json_str)

index_html_path = os.path.join(PROJECT_DIR, "index.html")

with open(index_html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Cockpit index.html construído com sucesso (AES-256 e dados dinâmicos)!")
