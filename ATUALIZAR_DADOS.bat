@echo off
chcp 65001 > nul
title S1 SAÚDE - ATUALIZAÇÃO COMPLETA DE AUDITORIA JIRA
cls
python "%~dp0atualizar_dados.py"
pause
