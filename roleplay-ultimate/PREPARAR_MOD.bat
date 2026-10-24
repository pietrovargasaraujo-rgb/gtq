@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0PREPARAR_MOD.ps1"
if errorlevel 1 (
    echo Falha ao preparar. Leia o erro acima.
    pause
    exit /b 1
)
pause
