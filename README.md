# S1 Saúde | Cockpit Executivo de Auditoria & Implantação de Contratos

Plataforma de inteligência de dados, governança de auditoria médica e monitoramento operacional de movimentações cadastrais e implantação de contratos da **S1 Saúde** ([s1saude.com.br](https://s1saude.com.br)).

---

## 🎯 Objetivo do Projeto

Centralizar e transformar os dados operacionais do Jira Cloud (Projeto `AUDITORIA`) em insights estratégicos para a Diretoria, Gerência de Operações e equipe de Auditoria/Cadastro:

1. **Visão Executiva do Funil:** Acompanhamento em tempo real de vidas em *Análise Pendente*, *Auditoria em Andamento*, *Liberar para Cadastrar*, *Cadastro Concluído* e *Cancelados*.
2. **Monitoramento de Vigências ANS:** Detecção preventiva de lotes e vidas com vigência iminente para evitar quebra de SLA regulatório.
3. **Métricas de CPT & APS:** Visibilidade das análises de Cobertura Parcial Temporária e encaminhamentos para Atenção Primária à Saúde.
4. **Produtividade da Equipe:** Mapeamento de transições e movimentações operacionais por analista (Priscila Tada, Raquel Lopes, Carlos Henrique, etc.).
5. **Acesso Multi-Dispositivo na Rede:** Visualização interativa local e na rede corporativa (`0.0.0.0:8088`).

---

## 📂 Estrutura de Diretórios

```
S1-JIRA-ANALISE-AUDITORIA/
│
├── 📂 data/                                -> Armazenamento de dados e caches
│   ├── auditoria_raw.json                  -> Dados brutos da API Jira Cloud
│   ├── auditoria_consolidada.xlsx          -> Base tabular processada (2.550+ registros)
│   ├── auditoria_analytics.json            -> Indicadores e agregações consolidadas
│   ├── interacoes_usuarios.json            -> Histórico de transições e changelog
│   └── alertas_diretoria_hoje.json         -> Casos críticos e pendências ativas
│
├── 📂 scripts/                             -> Módulos do pipeline de dados
│   ├── extractor_s1.py                     -> Extração automatizada via Jira Cloud API v3 (JQL)
│   ├── extract_interactions.py             -> Extração de changelogs e movimentações
│   ├── analytics_s1.py                     -> Processamento analítico e geração do Excel Executivo
│   ├── monitor_alertas_diretoria.py        -> Cálculo de casos em alerta e riscos de vigência
│   └── build_professional_dashboard.py     -> Construtor do Cockpit HTML autônomo
│
├── 📂 docs/                                -> Documentação técnica e operacional
│   ├── ARQUITETURA.md                      -> Arquitetura do pipeline e fluxos de dados
│   └── GUIA_OPERACIONAL.md                 -> Manual operacional para diretoria e analistas
│
├── 🌐 index.html                            -> Cockpit Executivo Oficial (Protegido AES-256)
├── 📄 Relatorio_Executivo_Auditoria_S1.xlsx -> Relatório Executivo Multi-Aba
├── 📄 servidor_local.py                     -> Servidor HTTP Multi-Thread (Porta 8088 | 0.0.0.0)
├── 📄 atualizar_dados.py                    -> Orquestrador do pipeline de sincronização
│
├── 🚀 INICIAR_PAINEL_S1.bat                 -> Iniciar servidor com console visível
├── 🚀 INICIAR_COCKPIT_OCULTO.vbs            -> Iniciar servidor em segundo plano silencioso
├── 🛑 PARAR_COCKPIT.bat                     -> Encerrar serviço na porta 8088
├── 🔄 ATUALIZAR_DADOS.bat                   -> Executar pipeline completo de sincronização
├── 📄 README.md                             -> Este manual geral
└── 📄 .gitignore                            -> Arquivos ignorados pelo controle de versão
```

---

## 🚀 Como Utilizar

### 1. Iniciar o Cockpit Web (Servidor Local e de Rede)

* **Com tela de console (Recomendado para diagnóstico):**
  Dê dois cliques em `INICIAR_PAINEL_S1.bat`.
* **Em segundo plano (Modo silencioso/invisível):**
  Dê dois cliques em `INICIAR_COCKPIT_OCULTO.vbs`.

O painel abrirá automaticamente no seu navegador. Os endereços de acesso são:
* **Localmente:** `http://localhost:8088/index.html`
* **Na Rede da Empresa:** `http://192.168.1.178:8088/index.html`

### 2. Encerrar o Servidor
Execute o arquivo `PARAR_COCKPIT.bat`.

### 3. Sincronizar Dados com o Jira

Você pode atualizar os dados de duas formas:
1. **Pela Interface:** Clique no botão azul **"Sincronizar Jira"** no cabeçalho do Cockpit.
2. **Por Linha de Comando / Batch:** Execute `ATUALIZAR_DADOS.bat` ou rode `python atualizar_dados.py`.

---

## 📊 Relatório Executivo em Excel

O arquivo `Relatorio_Executivo_Auditoria_S1.xlsx` é gerado automaticamente a cada sincronização e contém 6 abas estruturadas:

1. **`Base_Beneficiarios`:** Detalhamento individual de cada vida (subtarefa) com status, CPT, APS, empresa e vigência.
2. **`Base_Lotes_Demandas`:** Lista de chamados principais de implantação/movimentação.
3. **`Resumo_Status`:** Tabela executiva com distribuição percentual por status.
4. **`Resumo_Vigencias`:** Matriz cruzada de Vigências x Status da Auditoria.
5. **`Resumo_Empresas`:** Top contratos por volume e estágio de implantação.
6. **`Resumo_Auditores`:** Produtividade e distribuição de carga por responsável.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10+
* **Bibliotecas Python:** `pandas`, `requests`, `openpyxl`, `http.server`, `socketserver`
* **Frontend:** HTML5 Semântico, CSS3 Moderno (Design System S1 Saúde), JavaScript Vanilla, Chart.js v4
* **Integração:** Jira Cloud REST API v3 (JQL Search)
