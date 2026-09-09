"""Fase 3 — Procesamiento del presupuesto MIMP (múltiples cortes).

Lee los CSV crudos filtrados por Fase 2 (01_data_cruda/mef_devengado_pliego039_AAAA_*.csv)
y produce datasets limpios en 02_data_procesada/ + un JSON para el tablero en 03_analisis/.

Cortes generados (todos con trazabilidad fuente+url+fecha):
  - serie_anual: PIA, PIM, certificado, comprometido, devengado, girado, % ejecución.
  - por Unidad Ejecutora / Programa Ppto / Genérica de gasto / Fuente de financiamiento /
    Categoría (corriente vs capital) / Departamento (meta) / devengado mensual.

No inventa nada: si falta el CSV de un año, lo omite y lo reporta.
Uso:  python scripts/fase3_procesar_presupuesto.py
"""
from __future__ import annotations

import csv
import glob
import json
import re
import sys
from collections import defaultdict

from config import DIR_CRUDA, DIR_PROCESADA, DIR_ANALISIS

csv.field_size_limit(sys.maxsize)

FUENTE = "MEF Datos Abiertos – Presupuesto y Ejecución de Gasto (Devengado)"
BASE_URL = "https://fs.datosabiertos.mef.gob.pe/datastorefiles"

# Índices (esquema MEF 73 columnas, verificado 2026-09-08).
I_ANO = 0
I_EJEC = 9
I_PROG = 17
I_DEPT = 34
I_FF = 36
I_CAT = 42
I_GEN = 46
I_PIA, I_PIM, I_CERT, I_COMP = 55, 56, 57, 58
I_DEV_MESES = list(range(59, 71))  # ene..dic
I_DEV_ANUAL, I_GIRADO = 71, 72
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


def f(x: str) -> float:
    x = (x or "").strip().replace(",", "")
    try:
        return float(x)
    except ValueError:
        return 0.0


def url_anio(anio: str) -> str:
    return (f"{BASE_URL}/2025-Gasto-Devengado-Mensual.csv" if anio == "2025"
            else f"{BASE_URL}/{anio}-Gasto-Devengado.csv")


def nuevo():
    return {"pia": 0.0, "pim": 0.0, "cert": 0.0, "comp": 0.0, "dev": 0.0, "girado": 0.0}


def acum(d, fila):
    d["pia"] += f(fila[I_PIA]); d["pim"] += f(fila[I_PIM])
    d["cert"] += f(fila[I_CERT]); d["comp"] += f(fila[I_COMP])
    d["dev"] += f(fila[I_DEV_ANUAL]); d["girado"] += f(fila[I_GIRADO])


def ejec_pct(d):
    return round(100 * d["dev"] / d["pim"], 2) if d["pim"] else None


def main() -> None:
    archivos = sorted(glob.glob(str(DIR_CRUDA / "mef_devengado_pliego039_*_desc*.csv")))
    if not archivos:
        print("[AVISO] no hay CSV crudos. Corre antes la Fase 2.")
        return

    serie = defaultdict(nuevo)
    por_ue = defaultdict(nuevo)
    por_prog = defaultdict(nuevo)
    por_gen = defaultdict(nuevo)
    por_ff = defaultdict(nuevo)
    por_cat = defaultdict(nuevo)
    por_dept = defaultdict(nuevo)
    mensual = defaultdict(lambda: [0.0] * 12)  # anio -> devengado por mes
    fecha_por_anio = {}

    for ruta in archivos:
        anio = re.search(r"pliego039_(\d{4})_", ruta).group(1)
        fecha = re.search(r"_desc(\d{4}-\d{2}-\d{2})", ruta).group(1)
        fecha_por_anio[anio] = fecha
        n = 0
        with open(ruta, encoding="utf-8", newline="") as fh:
            r = csv.reader(fh)
            next(r, None)
            for fila in r:
                if len(fila) <= I_GIRADO:
                    continue
                acum(serie[anio], fila)
                acum(por_ue[(anio, fila[I_EJEC])], fila)
                acum(por_prog[(anio, fila[I_PROG])], fila)
                acum(por_gen[(anio, fila[I_GEN])], fila)
                acum(por_ff[(anio, fila[I_FF])], fila)
                acum(por_cat[(anio, fila[I_CAT])], fila)
                acum(por_dept[(anio, fila[I_DEPT])], fila)
                for i, ci in enumerate(I_DEV_MESES):
                    mensual[anio][i] += f(fila[ci])
                n += 1
        print(f"[{anio}] {n:,} filas procesadas")

    DIR_PROCESADA.mkdir(exist_ok=True)
    DIR_ANALISIS.mkdir(exist_ok=True)
    anios = sorted(serie)

    def escribir(nombre, encabezado_clave, mapa):
        ruta = DIR_PROCESADA / nombre
        with open(ruta, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow([*encabezado_clave, "pia", "pim", "certificado", "comprometido",
                        "devengado", "girado", "ejecucion_pct_dev_pim",
                        "fuente", "url", "fecha_descarga"])
            for clave in sorted(mapa):
                d = mapa[clave]
                anio = clave[0] if isinstance(clave, tuple) else clave
                w.writerow([*(clave if isinstance(clave, tuple) else [clave]),
                            round(d["pia"], 2), round(d["pim"], 2), round(d["cert"], 2),
                            round(d["comp"], 2), round(d["dev"], 2), round(d["girado"], 2),
                            ejec_pct(d), FUENTE, url_anio(anio), fecha_por_anio[anio]])
        print(f"→ {ruta.name}")

    escribir("presupuesto_mimp_serie_anual.csv", ["anio"], serie)
    escribir("presupuesto_mimp_por_ue.csv", ["anio", "unidad_ejecutora"], por_ue)
    escribir("presupuesto_mimp_por_programa.csv", ["anio", "programa_ppto"], por_prog)
    escribir("presupuesto_mimp_por_generica.csv", ["anio", "generica_gasto"], por_gen)
    escribir("presupuesto_mimp_por_fuente.csv", ["anio", "fuente_financiamiento"], por_ff)
    escribir("presupuesto_mimp_por_categoria.csv", ["anio", "categoria_gasto"], por_cat)
    escribir("presupuesto_mimp_por_departamento.csv", ["anio", "departamento_meta"], por_dept)

    # --- JSON compacto para el tablero (03_analisis) ---
    def top_por_categoria(mapa, k=12):
        """Top-k etiquetas por devengado total del periodo + serie por año."""
        tot = defaultdict(float)
        for (anio, etq), d in mapa.items():
            tot[etq] += d["dev"]
        top = [e for e, _ in sorted(tot.items(), key=lambda x: -x[1])[:k]]
        return {
            "labels": top,
            "por_anio": {anio: {etq: round(mapa[(anio, etq)]["dev"], 2)
                                for etq in top if (anio, etq) in mapa}
                         for anio in anios},
        }

    dash = {
        "meta": {"fuente": FUENTE, "url_base": BASE_URL, "pliego": "039 - MIMP",
                 "fecha_descarga": fecha_por_anio, "periodo": anios},
        "serie_anual": [{"anio": a, "pia": round(serie[a]["pia"], 2),
                         "pim": round(serie[a]["pim"], 2),
                         "certificado": round(serie[a]["cert"], 2),
                         "comprometido": round(serie[a]["comp"], 2),
                         "devengado": round(serie[a]["dev"], 2),
                         "girado": round(serie[a]["girado"], 2),
                         "no_ejecutado": round(serie[a]["pim"] - serie[a]["dev"], 2),
                         "ejecucion_pct": ejec_pct(serie[a])} for a in anios],
        "mensual": {a: [round(v, 2) for v in mensual[a]] for a in anios},
        "meses": MESES,
        "por_ue": top_por_categoria(por_ue),
        "por_programa": top_por_categoria(por_prog),
        "por_generica": top_por_categoria(por_gen),
        "por_fuente": top_por_categoria(por_ff),
        "por_categoria": top_por_categoria(por_cat, k=6),
        "por_departamento": top_por_categoria(por_dept, k=15),
    }
    out_json = DIR_ANALISIS / "presupuesto_dashboard.json"
    out_json.write_text(json.dumps(dash, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"→ {out_json.name}")

    print("\n===== SERIE ANUAL MIMP (soles corrientes) =====")
    print(f"{'Año':>5} {'PIA':>16} {'PIM':>16} {'Devengado':>16} {'Ejec%':>7} {'No ejec.':>15}")
    for a in anios:
        d = serie[a]
        print(f"{a:>5} {d['pia']:>16,.0f} {d['pim']:>16,.0f} {d['dev']:>16,.0f} "
              f"{(ejec_pct(d) or 0):>6.1f}% {d['pim']-d['dev']:>15,.0f}")


if __name__ == "__main__":
    main()
