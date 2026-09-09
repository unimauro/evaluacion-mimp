"""Fase 2 — Descarga y filtrado del presupuesto MIMP (pliego 039) desde MEF Datos Abiertos.

Fuente: MEF Datos Abiertos «Presupuesto y Ejecución de Gasto – Devengado Mensual».
Cada CSV anual pesa ~2–2.6 GB (TODOS los pliegos del Perú). Este script lo procesa en
STREAMING (no lo guarda entero): descarga, filtra PLIEGO='039' (MIMP) y escribe solo
las filas del MIMP en 01_data_cruda/, con trazabilidad (fuente + URL + fecha de descarga).

No inventa nada: si un año falla, lo registra y sigue. Reporta las cifras al final.

Uso:  python scripts/fase2_descarga_presupuesto.py [AÑO ...]
      (sin argumentos procesa 2019–2025)
"""
from __future__ import annotations

import csv
import io
import sys
import urllib.request
from datetime import date

from config import DIR_CRUDA, PERIODO

FECHA_DESCARGA = date.today().isoformat()  # 2026-09-08

BASE = "https://fs.datosabiertos.mef.gob.pe/datastorefiles"
URLS = {
    2019: f"{BASE}/2019-Gasto-Devengado.csv",
    2020: f"{BASE}/2020-Gasto-Devengado.csv",
    2021: f"{BASE}/2021-Gasto-Devengado.csv",
    2022: f"{BASE}/2022-Gasto-Devengado.csv",
    2023: f"{BASE}/2023-Gasto-Devengado.csv",
    2024: f"{BASE}/2024-Gasto-Devengado.csv",
    2025: f"{BASE}/2025-Gasto-Devengado-Mensual.csv",
}

I_PLIEGO = 5
I_PLIEGO_NOMBRE = 6


def es_mimp(fila: list[str]) -> bool:
    """MIMP = pliego 039. Se acepta '039'/'39' o el nombre con 'MUJER' (robustez)."""
    pliego = fila[I_PLIEGO].strip().lstrip("0") or "0"
    nombre = fila[I_PLIEGO_NOMBRE].upper()
    return pliego == "39" or "MUJER Y POBLACIONES" in nombre


def procesar_anio(anio: int) -> dict:
    url = URLS[anio]
    salida = DIR_CRUDA / f"mef_devengado_pliego039_{anio}_desc{FECHA_DESCARGA}.csv"
    print(f"[{anio}] descargando y filtrando en streaming desde {url}", flush=True)

    req = urllib.request.Request(url, headers={"User-Agent": "evaluacion-mimp/1.0"})
    n_total = n_mimp = 0
    nombres_pliego: set[str] = set()

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            texto = io.TextIOWrapper(resp, encoding="utf-8-sig", newline="")
            lector = csv.reader(texto)
            cabecera = next(lector)
            with open(salida, "w", newline="", encoding="utf-8") as fout:
                escritor = csv.writer(fout)
                escritor.writerow(cabecera)
                for fila in lector:
                    n_total += 1
                    if len(fila) > I_PLIEGO_NOMBRE and es_mimp(fila):
                        escritor.writerow(fila)
                        n_mimp += 1
                        nombres_pliego.add(fila[I_PLIEGO_NOMBRE])
    except Exception as e:  # noqa: BLE001 — registrar y seguir (regla n.º 4 de reporte)
        print(f"[{anio}] ERROR: {e}", flush=True)
        return {"anio": anio, "url": url, "ok": False, "error": str(e)}

    print(
        f"[{anio}] OK — {n_mimp:,} filas MIMP de {n_total:,} totales "
        f"→ {salida.name} | pliego(s): {sorted(nombres_pliego)}",
        flush=True,
    )
    return {
        "anio": anio,
        "url": url,
        "ok": True,
        "filas_mimp": n_mimp,
        "filas_totales": n_total,
        "archivo": salida.name,
        "pliego_nombre": sorted(nombres_pliego),
    }


def main() -> None:
    anios = [int(a) for a in sys.argv[1:]] or list(PERIODO)
    resultados = [procesar_anio(a) for a in anios if a in URLS]

    print("\n===== RESUMEN FASE 2 (descarga presupuesto) =====")
    for r in resultados:
        if r["ok"]:
            print(
                f"  {r['anio']}: {r['filas_mimp']:,} filas MIMP → {r['archivo']} "
                f"({r['pliego_nombre']})"
            )
        else:
            print(f"  {r['anio']}: [NO DISPONIBLE] {r['error']} — {r['url']}")


if __name__ == "__main__":
    main()
