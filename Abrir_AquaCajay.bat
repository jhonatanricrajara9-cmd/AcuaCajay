@echo off
title AquaCajay
cd /d "%~dp0"

echo Iniciando AquaCajay...
echo (Se abrira tu navegador automaticamente en unos segundos)
echo.

pip install -r requirements.txt --quiet

python app.py

pause
