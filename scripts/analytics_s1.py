import os
import sys
import json
import pandas as pd
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
excel_src = os.path.join(DATA_DIR, "auditoria_consolidada.xlsx")

def run_analytics():
    if not os.path.exists(excel_src):
        print(f"Arquivo não encontrado: {excel_src}")
        return
        
    df = pd.read_excel(excel_src)
    print(f"Carregados {len(df)} registros para análise...")
    
    # Subtarefas representam as Vidas/Beneficiários
    df_vidas = df[df["Tipo Item"] == "Subtarefa"].copy()
    df_lotes = df[df["Tipo Item"] != "Subtarefa"].copy()
    
    total_registros = len(df)
    total_vidas = len(df_vidas)
    total_lotes = len(df_lotes)
    
    # 1. Status Geral de Vidas
    status_counts = df_vidas["Status Atual"].value_counts().to_dict()
    
    # 2. Distribuição por Vigência
    df_vidas["Vigência"] = df_vidas["Vigência"].fillna("Não Informada").replace("", "Não Informada")
    vigencia_counts = df_vidas["Vigência"].value_counts().to_dict()
    
    # Vigência cruzada com Status
    vigencia_status = pd.crosstab(df_vidas["Vigência"], df_vidas["Status Atual"]).to_dict() if len(df_vidas) > 0 else {}
    
    # 3. Top Empresas por Volume de Vidas
    df_vidas["Empresa / Contrato"] = df_vidas["Empresa / Contrato"].fillna("Não Informada").replace("", "Não Informada")
    empresa_counts = df_vidas["Empresa / Contrato"].value_counts().head(20).to_dict()
    
    # 4. Produtividade por Responsável (Auditor)
    df_vidas["Responsável"] = df_vidas["Responsável"].fillna("Não Atribuído")
    auditor_counts = df_vidas["Responsável"].value_counts().to_dict()
    auditor_status = pd.crosstab(df_vidas["Responsável"], df_vidas["Status Atual"]).to_dict() if len(df_vidas) > 0 else {}
    
    # 5. Tipo Beneficiário (Titular vs Dependente)
    tipo_benef = df_vidas["Tipo Beneficiário"].value_counts().to_dict()
    
    # 6. Tipo de Movimentação
    tipo_mov = df_vidas["Tipo Movimentação"].value_counts().to_dict()
    
    # 7. Análise CPT e APS
    cpt_counts = df_vidas["Análise CPT"].value_counts().to_dict()
    aps_counts = df_vidas["Acompanhamento APS"].value_counts().to_dict()
    
    # 8. Análise de Lead Time de Conclusão e Aging da Fila
    df_vidas["dt_criacao"] = pd.to_datetime(df_vidas["Data Criação"], errors="coerce")
    df_vidas["dt_atualizacao"] = pd.to_datetime(df_vidas["Data Atualização"], errors="coerce")
    
    status_concluidos = ["CADASTRO CONCLUÍDO", "LIBERAR PARA CADASTRAR", "LIBERADO COM CPT", "CONCLUÍDO APS"]
    status_pendentes = ["ANÁLISE PENDENTE", "AUDITORIA EM ANDAMENTO", "PENDÊNCIA CADASTRO", "AGUARDANDO DIRETORIA", "CPT Enviada", "CPT ENVIADA", "APS"]

    df_concluidos = df_vidas[df_vidas["Status Atual"].isin(status_concluidos)].copy()
    df_pendentes = df_vidas[df_vidas["Status Atual"].isin(status_pendentes)].copy()

    df_concluidos["lead_time_dias"] = (df_concluidos["dt_atualizacao"] - df_concluidos["dt_criacao"]).dt.total_seconds() / (24 * 3600)
    df_concluidos["lead_time_dias"] = df_concluidos["lead_time_dias"].clip(lower=0)

    now = pd.Timestamp.now()
    df_pendentes["aging_dias"] = (now - df_pendentes["dt_criacao"]).dt.total_seconds() / (24 * 3600)
    df_pendentes["aging_dias"] = df_pendentes["aging_dias"].clip(lower=0)

    # Lead Time Estatísticas
    lt_mean = float(df_concluidos["lead_time_dias"].mean()) if len(df_concluidos) > 0 else 0.0
    lt_median = float(df_concluidos["lead_time_dias"].median()) if len(df_concluidos) > 0 else 0.0
    lt_min = float(df_concluidos["lead_time_dias"].min()) if len(df_concluidos) > 0 else 0.0
    lt_max = float(df_concluidos["lead_time_dias"].max()) if len(df_concluidos) > 0 else 0.0

    # Aging Estatísticas
    aging_mean = float(df_pendentes["aging_dias"].mean()) if len(df_pendentes) > 0 else 0.0
    aging_median = float(df_pendentes["aging_dias"].median()) if len(df_pendentes) > 0 else 0.0

    # Faixas de Lead Time
    bins_lt = [-1, 3, 7, 15, 30, 60, 9999]
    labels_lt = ["0-3 dias", "4-7 dias", "8-15 dias", "16-30 dias", "31-60 dias", "> 60 dias"]
    lt_buckets = pd.cut(df_concluidos["lead_time_dias"], bins=bins_lt, labels=labels_lt).value_counts().to_dict()

    # Faixas de Aging
    bins_ag = [-1, 7, 15, 30, 60, 120, 9999]
    labels_ag = ["Até 7 dias", "8-15 dias", "16-30 dias", "31-60 dias", "61-120 dias", "> 120 dias"]
    ag_buckets = pd.cut(df_pendentes["aging_dias"], bins=bins_ag, labels=labels_ag).value_counts().to_dict()

    # Top Empresas Pendentes
    top_empresas_pend_df = df_pendentes.groupby("Empresa / Contrato").agg(
        total_pendentes=("Chave", "count"),
        analise_pendente=("Status Atual", lambda s: (s == "ANÁLISE PENDENTE").sum()),
        auditoria_andamento=("Status Atual", lambda s: (s == "AUDITORIA EM ANDAMENTO").sum()),
        criticos_diretoria_cadastro=("Status Atual", lambda s: s.isin(["PENDÊNCIA CADASTRO", "AGUARDANDO DIRETORIA", "CPT Enviada", "CPT ENVIADA"]).sum()),
        tempo_medio_aberto_dias=("aging_dias", "mean"),
        lote_mais_antigo=("Data Criação", "min")
    ).reset_index().sort_values(by="total_pendentes", ascending=False)
    
    # 9. Relatório Consolidado JSON
    analytics_payload = {
        "kpis": {
            "total_registros": total_registros,
            "total_vidas": total_vidas,
            "total_lotes": total_lotes,
            "analise_pendente": int(status_counts.get("ANÁLISE PENDENTE", 0)),
            "auditoria_em_andamento": int(status_counts.get("AUDITORIA EM ANDAMENTO", 0)),
            "liberado_para_cadastrar": int(status_counts.get("LIBERAR PARA CADASTRAR", 0) + status_counts.get("LIBERADO COM CPT", 0)),
            "cadastro_concluido": int(status_counts.get("CADASTRO CONCLUÍDO", 0)),
            "pendencia_cadastro": int(status_counts.get("PENDÊNCIA CADASTRO", 0)),
            "aguardando_diretoria": int(status_counts.get("AGUARDANDO DIRETORIA", 0)),
            "cancelado": int(status_counts.get("CANCELADO", 0)),
            "taxa_liberacao": round(((status_counts.get("LIBERAR PARA CADASTRAR", 0) + status_counts.get("CADASTRO CONCLUÍDO", 0) + status_counts.get("LIBERADO COM CPT", 0)) / max(total_vidas, 1)) * 100, 2),
            "lead_time_medio_dias": round(lt_mean, 1),
            "lead_time_mediana_dias": round(lt_median, 1),
            "lead_time_min_dias": round(lt_min, 1),
            "lead_time_max_dias": round(lt_max, 1),
            "tempo_medio_aberto_pendentes_dias": round(aging_mean, 1),
            "total_vidas_pendentes": len(df_pendentes),
            "total_vidas_concluidas": len(df_concluidos)
        },
        "status_distribution": {k: int(v) for k, v in status_counts.items()},
        "vigencia_distribution": {k: int(v) for k, v in vigencia_counts.items()},
        "top_empresas": {k: int(v) for k, v in empresa_counts.items()},
        "top_empresas_pendentes": top_empresas_pend_df.head(20).to_dict(orient="records"),
        "auditor_distribution": {k: int(v) for k, v in auditor_counts.items()},
        "tipo_beneficiario": {k: int(v) for k, v in tipo_benef.items()},
        "tipo_movimentacao": {k: int(v) for k, v in tipo_mov.items()},
        "analise_cpt": {k: int(v) for k, v in cpt_counts.items()},
        "acompanhamento_aps": {k: int(v) for k, v in aps_counts.items()},
        "lead_time_distribuicao": {str(k): int(v) for k, v in lt_buckets.items()},
        "aging_distribuicao": {str(k): int(v) for k, v in ag_buckets.items()}
    }
    
    analytics_json_path = os.path.join(DATA_DIR, "auditoria_analytics.json")
    with open(analytics_json_path, "w", encoding="utf-8") as f:
        json.dump(analytics_payload, f, ensure_ascii=False, indent=2)
        
    print(f"Analytics JSON salvo em: {analytics_json_path}")
    
    # Gerar Relatório Executivo Multi-Aba em Excel
    report_xlsx = os.path.join(PROJECT_DIR, "Relatorio_Executivo_Auditoria_S1.xlsx")
    with pd.ExcelWriter(report_xlsx, engine='openpyxl') as writer:
        df_vidas.to_excel(writer, sheet_name="Base_Beneficiarios", index=False)
        df_lotes.to_excel(writer, sheet_name="Base_Lotes_Demandas", index=False)
        
        # Resumo por Status
        df_status = pd.DataFrame(list(status_counts.items()), columns=["Status da Auditoria", "Qtd Vidas"])
        df_status["% do Total"] = (df_status["Qtd Vidas"] / max(total_vidas, 1) * 100).round(2)
        df_status.to_excel(writer, sheet_name="Resumo_Status", index=False)
        
        # Top Empresas Pendentes
        top_empresas_pend_df.to_excel(writer, sheet_name="Top_Empresas_Pendentes", index=False)

        # Lead Time de Auditoria
        df_lt_summary = pd.DataFrame([
            {"Métrica": "Lead Time Médio de Conclusão (Dias)", "Valor": round(lt_mean, 1)},
            {"Métrica": "Lead Time Mediana de Conclusão (Dias)", "Valor": round(lt_median, 1)},
            {"Métrica": "Menor Tempo de Conclusão (Dias)", "Valor": round(lt_min, 1)},
            {"Métrica": "Maior Tempo de Conclusão (Dias)", "Valor": round(lt_max, 1)},
            {"Métrica": "Tempo Médio em Aberto das Pendências (Aging Dias)", "Valor": round(aging_mean, 1)},
            {"Métrica": "Total de Vidas Concluídas/Liberadas", "Valor": len(df_concluidos)},
            {"Métrica": "Total de Vidas Pendentes na Fila", "Valor": len(df_pendentes)}
        ])
        df_lt_summary.to_excel(writer, sheet_name="Lead_Time_Auditoria", index=False)

        if len(df_vidas) > 0:
            # Resumo por Vigência
            df_vig = pd.crosstab(df_vidas["Vigência"], df_vidas["Status Atual"], margins=True, margins_name="Total Geral").reset_index()
            df_vig.to_excel(writer, sheet_name="Resumo_Vigencias", index=False)
            
            # Resumo por Empresa
            df_emp = pd.crosstab(df_vidas["Empresa / Contrato"], df_vidas["Status Atual"], margins=True, margins_name="Total Geral").reset_index()
            df_emp.sort_values(by="Total Geral", ascending=False).to_excel(writer, sheet_name="Resumo_Empresas", index=False)
            
            # Resumo por Auditor
            df_aud = pd.crosstab(df_vidas["Responsável"], df_vidas["Status Atual"], margins=True, margins_name="Total Geral").reset_index()
            df_aud.to_excel(writer, sheet_name="Resumo_Auditores", index=False)
        else:
            pd.DataFrame().to_excel(writer, sheet_name="Resumo_Vigencias", index=False)
            pd.DataFrame().to_excel(writer, sheet_name="Resumo_Empresas", index=False)
            pd.DataFrame().to_excel(writer, sheet_name="Resumo_Auditores", index=False)
        
    print(f"Relatório Executivo Excel gerado em: {report_xlsx}")
    return analytics_payload

if __name__ == "__main__":
    run_analytics()
