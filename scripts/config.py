"""Configuración común de la evaluación MIMP (pliego 039).

Rutas, periodo y constantes reutilizadas por todos los scripts.
No contiene datos: solo parámetros. Ver INSTRUCCIONES.md.
"""
from __future__ import annotations

from pathlib import Path

# --- Rutas del repo ---------------------------------------------------------
RAIZ = Path(__file__).resolve().parent.parent
DIR_FUENTES = RAIZ / "00_fuentes"
DIR_CRUDA = RAIZ / "01_data_cruda"
DIR_PROCESADA = RAIZ / "02_data_procesada"
DIR_ANALISIS = RAIZ / "03_analisis"
DIR_ENTREGABLES = RAIZ / "04_entregables"

# --- Parámetros del encargo -------------------------------------------------
# SUPUESTO: periodo de análisis 2019-2025 (ajustable; confirmar en README).
ANIO_INICIO = 2019
ANIO_FIN = 2025
PERIODO = list(range(ANIO_INICIO, ANIO_FIN + 1))

PLIEGO_MIMP = "039"

# Campos de trazabilidad obligatorios en TODO dato que entre al análisis.
CAMPOS_TRAZABILIDAD = ("fuente", "url", "fecha_descarga")

# Marcador estándar para datos no obtenidos (regla inviolable n.º 1).
def no_disponible(url: str) -> str:
    return f"[NO DISPONIBLE — requiere descarga manual desde {url}]"


# Servicios/programas del pliego 039 (SUPUESTO de alcance; confirmar en Fase 1).
UNIDADES_PLIEGO_039 = [
    "Programa Warmi Ñan (ex-AURORA)",
    "INABIF",
    "CONADIS",
    "DGNNA",
]

# Recordatorio de salvaguarda: indicadores multisectoriales = CONTEXTO, no
# eficacia directa del MIMP (feminicidios -> MP/PJ; desapariciones -> Mininter/PNP).
INDICADORES_CONTEXTO_MULTISECTORIAL = [
    "feminicidios",
    "tentativas_feminicidio",
    "violaciones",
    "personas_desaparecidas",
]
