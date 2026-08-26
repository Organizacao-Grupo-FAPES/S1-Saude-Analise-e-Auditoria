@echo off
chcp 65001 > nul
title S1 SAÚDE - PAINEL EXECUTIVO DE AUDITORIA & SYNC
cls
echo ====================================================================
echo             S1 SAÚDE - PAINEL EXECUTIVO DA DIRETORIA
echo ====================================================================
echo.
echo [1/2] Iniciando Servidor Local e de Rede na porta 8088...
echo [2/2] Abrindo Dashboard no Navegador...
echo.
echo Para fechar o servidor, feche esta janela ou pressione Ctrl+C.
echo.
start "" http://localhost:8088/index.html
python "%~dp0servidor_local.py"
pause
