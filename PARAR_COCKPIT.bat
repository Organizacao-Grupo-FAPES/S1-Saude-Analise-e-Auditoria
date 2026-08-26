@echo off
chcp 65001 > nul
echo Encerrando processo do Cockpit S1 Saúde na porta 8088...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8088 ^| findstr LISTENING') do (
    taskkill /f /pid %%a > nul 2>&1
    echo Processo com PID %%a finalizado.
)
echo Servidor encerrado com sucesso!
timeout /t 2 > nul
