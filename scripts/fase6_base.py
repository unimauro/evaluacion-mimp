"""Fase 6 — Base de datos Excel (Base_Datos_MIMP.xlsx).

Consolida los datasets del proyecto en un libro Excel: una hoja por dimensión (leyendo
los CSV de 01_data_cruda/ y 02_data_procesada/) + una hoja "Fuentes" con la trazabilidad
(fuente + URL + fecha de descarga) de cada dataset. No inventa nada: solo reempaqueta lo
que ya está en los CSV.

Uso:  python scripts/fase6_base.py   (requiere openpyxl; usar el .venv del repo)
"""
from __future__ import annotations

import csv
import glob

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from config import DIR_CRUDA, DIR_PROCESADA, DIR_ENTREGABLES

# Hoja -> patrón de archivo (primero procesado, si no, crudo). Orden = dimensiones.
HOJAS = [
    ("Presupuesto (serie)", DIR_PROCESADA, "presupuesto_mimp_serie_anual.csv"),
    ("Presupuesto x UE", DIR_PROCESADA, "presupuesto_mimp_por_ue.csv"),
    ("Presupuesto x programa", DIR_PROCESADA, "presupuesto_mimp_por_programa.csv"),
    ("Presupuesto x depto", DIR_PROCESADA, "presupuesto_mimp_por_departamento.csv"),
    ("ENDES prevalencia", DIR_CRUDA, "endes_prevalencia_*.csv"),
    ("Meta vs real (12m)", DIR_CRUDA, "violencia_12meses_real_*.csv"),
    ("Feminicidios", DIR_CRUDA, "feminicidios_serie_*.csv"),
    ("Violencia sexual", DIR_CRUDA, "violaciones_serie_*.csv"),
    ("Violencia x depto", DIR_CRUDA, "violencia_por_departamento_*.csv"),
    ("Atenciones CEM x tipo", DIR_CRUDA, "cem_atenciones_por_tipo_*.csv"),
    ("Linea 100", DIR_CRUDA, "linea100_serie_*.csv"),
    ("N CEM", DIR_CRUDA, "cem_numero_serie_*.csv"),
    ("Embarazo adolescente", DIR_CRUDA, "embarazo_adolescente_*.csv"),
    ("DEMUNA", DIR_CRUDA, "demuna_serie_*.csv"),
    ("Personal (PTE)", DIR_CRUDA, "personal_mimp_pte_*.csv"),
    ("Metas de planes", DIR_CRUDA, "metas_planes_*.csv"),
    ("Marco normativo", DIR_CRUDA, "normas_mimp_*.csv"),
    ("Titulares", DIR_CRUDA, "titulares_mimp_confirmado_*.csv"),
]

HEAD_FILL = PatternFill("solid", fgColor="6D28D9")
HEAD_FONT = Font(bold=True, color="FFFFFF", size=10)


def resolver(carpeta, patron):
    arch = sorted(glob.glob(str(carpeta / patron)))
    return arch[-1] if arch else None


def volcar(ws, ruta):
    with open(ruta, encoding="utf-8", newline="") as f:
        for i, fila in enumerate(csv.reader(f)):
            ws.append(fila)
            if i == 0:
                for c in range(1, len(fila) + 1):
                    cell = ws.cell(row=1, column=c)
                    cell.fill = HEAD_FILL; cell.font = HEAD_FONT
                    cell.alignment = Alignment(vertical="center")
    ws.freeze_panes = "A2"
    # Ancho aproximado
    for col in ws.columns:
        w = max((len(str(c.value)) for c in col if c.value), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max(w + 2, 10), 60)


def main() -> None:
    wb = Workbook()
    wb.remove(wb.active)

    # Portada
    port = wb.create_sheet("Portada")
    port["A1"] = "Base de datos — Evaluación de la gestión del MIMP (pliego 039), 2017–2025"
    port["A1"].font = Font(bold=True, size=13)
    port["A3"] = "Cada hoja es un dataset con su trazabilidad (columnas fuente/url/fecha)."
    port["A4"] = "Regla del proyecto: ninguna cifra sin fuente + URL + fecha de descarga (2026-09-08)."
    port["A5"] = "Repositorio reproducible: evaluacion-mimp. Datos: MEF, INEI-ENDES, Warmi Ñan, INEI/PNP, PTE, El Peruano."
    port.column_dimensions["A"].width = 100

    fuentes = [("Hoja", "Dataset (archivo)", "Fuente", "URL", "Fecha descarga")]
    for nombre, carpeta, patron in HOJAS:
        ruta = resolver(carpeta, patron)
        if not ruta:
            continue
        ws = wb.create_sheet(nombre[:31])
        volcar(ws, ruta)
        # Trazabilidad: primera fila de datos con columnas fuente/url/fecha
        with open(ruta, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        fte = url = fecha = ""
        for r in rows:
            fte = r.get("fuente", fte) or fte
            url = r.get("url", url) or url
            fecha = r.get("fecha_descarga", r.get("fecha_consulta", fecha)) or fecha
            if url.startswith("http"):
                break
        fuentes.append((nombre, ruta.split("/")[-1], fte[:80], url, fecha))

    wf = wb.create_sheet("Fuentes")
    for i, fila in enumerate(fuentes):
        wf.append(fila)
        if i == 0:
            for c in range(1, len(fila) + 1):
                cell = wf.cell(row=1, column=c); cell.fill = HEAD_FILL; cell.font = HEAD_FONT
    wf.freeze_panes = "A2"
    for col, w in zip("ABCDE", (22, 42, 55, 70, 15)):
        wf.column_dimensions[col].width = w

    # Reordenar: Portada primero, Fuentes al final
    wb.move_sheet("Portada", -(wb.sheetnames.index("Portada")))
    DIR_ENTREGABLES.mkdir(exist_ok=True)
    out = DIR_ENTREGABLES / "Base_Datos_MIMP.xlsx"
    wb.save(out)
    print(f"→ {out} ({len(wb.sheetnames)} hojas)")


if __name__ == "__main__":
    main()
