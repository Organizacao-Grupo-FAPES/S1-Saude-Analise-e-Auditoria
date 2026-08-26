import os
import sys
import subprocess
import webbrowser

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(PROJECT_DIR, "scripts")

def executar_passo(numero, total, descricao, script_nome):
    print(f"\n[{numero}/{total}] {descricao}...")
    script_path = os.path.join(SCRIPTS_DIR, script_nome)
    if not os.path.exists(script_path):
        print(f"❌ Erro: Script {script_nome} não encontrado em {SCRIPTS_DIR}")
        sys.exit(1)
    
    resultado = subprocess.run([sys.executable, script_path])
    if resultado.returncode != 0:
        print(f"❌ Falha na execução de {script_nome} (Código: {resultado.returncode})")
        sys.exit(resultado.returncode)

def main():
    print("=================================================================")
    print("   S1 SAÚDE - SINCRONIZAÇÃO E PROCESSAMENTO COMPLETO DA AUDITORIA")
    print("=================================================================")

    passos = [
        ("Extraindo tickets da API Jira Cloud S1 Saúde", "extractor_s1.py"),
        ("Extraindo histórico de interações e changelogs", "extract_interactions.py"),
        ("Processando métricas analíticas e gerando Excel Executivo", "analytics_s1.py"),
        ("Calculando alertas críticos de diretoria e vigências", "monitor_alertas_diretoria.py"),
        ("Reconstruindo Cockpit Web Executivo de Alta Fidelidade", "build_professional_dashboard.py")
    ]

    total_passos = len(passos)
    for idx, (desc, script) in enumerate(passos, 1):
        executar_passo(idx, total_passos, desc, script)

    print("\n" + "="*65)
    print("   ✅ PIPELINE CONCLUÍDO COM SUCESSO!")
    print("   - Base de dados atualizada em: data/")
    print("   - Relatório Executivo Excel atualizado na raiz")
    print("   - Cockpit Web HTML pronto para visualização")
    print("="*65)

    index_path = os.path.join(PROJECT_DIR, "index.html")
    if os.path.exists(index_path):
        print("\nAbrindo o Cockpit no navegador padrão...")
        webbrowser.open(f"file:///{index_path.replace(os.sep, '/')}")

if __name__ == "__main__":
    main()
