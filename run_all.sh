#!/usr/bin/env bash
# Pipeline reproducible de la evaluación MIMP.
set -e
cd "$(dirname "$0")"
python3 scripts/fase2_descarga_presupuesto.py      # descarga+filtra CSV MEF (pliego 039)
python3 scripts/fase3_procesar_presupuesto.py      # series e indicadores -> 02/03
python3 scripts/fase6_og.py                        # imagen OG
python3 scripts/fase6_tablero.py                   # docs/index.html (GitHub Pages)
# Entregables Word/Excel (requieren openpyxl + python-docx; usar .venv):
#   python -m venv .venv && ./.venv/bin/pip install -r scripts/requirements.txt
./.venv/bin/python scripts/fase6_base.py    2>/dev/null || python3 scripts/fase6_base.py
./.venv/bin/python scripts/fase6_informe.py 2>/dev/null || python3 scripts/fase6_informe.py
echo "Listo. Entregables en 04_entregables/ ; tablero en docs/index.html"
