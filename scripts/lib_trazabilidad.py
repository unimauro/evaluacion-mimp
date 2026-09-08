"""Validador de trazabilidad (regla inviolable n.º 2).

Ningún dato entra al análisis sin: valor + fuente + URL exacta + fecha de descarga.
Estas funciones hacen cumplir esa regla sobre los DataFrames antes de analizar.
"""
from __future__ import annotations

import pandas as pd

from config import CAMPOS_TRAZABILIDAD


class ErrorTrazabilidad(ValueError):
    """Se lanza cuando un dataset no cumple la regla de trazabilidad."""


def validar_trazabilidad(df: pd.DataFrame, nombre: str) -> pd.DataFrame:
    """Verifica que existan y estén llenas las columnas de trazabilidad.

    No inventa nada: si faltan columnas o hay celdas vacías en fuente/url/
    fecha_descarga, aborta indicando qué filas fallan.
    """
    faltantes = [c for c in CAMPOS_TRAZABILIDAD if c not in df.columns]
    if faltantes:
        raise ErrorTrazabilidad(
            f"[{nombre}] faltan columnas de trazabilidad: {faltantes}"
        )

    vacias = df[list(CAMPOS_TRAZABILIDAD)].isna().any(axis=1)
    if vacias.any():
        filas = df.index[vacias].tolist()
        raise ErrorTrazabilidad(
            f"[{nombre}] {vacias.sum()} fila(s) sin fuente/url/fecha_descarga: {filas}"
        )
    return df


def cargar_procesado(ruta, nombre: str) -> pd.DataFrame | None:
    """Carga un CSV procesado y valida su trazabilidad.

    Devuelve None (con aviso) si el archivo no existe o está vacío, en vez de
    fabricar datos. Así el pipeline es reproducible y honesto ante gaps.
    """
    from pathlib import Path

    ruta = Path(ruta)
    if not ruta.exists():
        print(f"[AVISO] {nombre}: no existe {ruta} — dato pendiente (Fase 2).")
        return None

    df = pd.read_csv(ruta)
    if df.empty:
        print(f"[AVISO] {nombre}: {ruta} está vacío — plantilla sin poblar aún.")
        return None

    return validar_trazabilidad(df, nombre)
