#!/bin/bash
cd "$(dirname "$10")"
echo "Iniciando AquaCajay..."
echo "(Se abrirá tu navegador automáticamente en unos segundos)"
pip install -r requirements.txt --quiet
python3 app.py
