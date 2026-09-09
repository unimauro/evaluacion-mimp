"""Fase 6 — Informe de evaluación en Word (Informe_Evaluacion_MIMP.docx).

Genera el informe con resumen ejecutivo, hallazgos por dimensión, contraste de hipótesis
H1-H6, conclusiones, recomendaciones y limitaciones. Toma las cifras del JSON procesado
(presupuesto) y de los CSV de agentes; toda cifra referida es trazable a esos datasets
(ver Base_Datos_MIMP.xlsx y la hoja Fuentes).

Uso:  python scripts/fase6_informe.py   (requiere python-docx; usar el .venv del repo)
"""
from __future__ import annotations

import csv
import glob
import json

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from config import DIR_ANALISIS, DIR_CRUDA, DIR_ENTREGABLES

ACCENT = RGBColor(0x6D, 0x28, 0xD9)


def leer(patron, carpeta=DIR_CRUDA):
    arch = sorted(glob.glob(str(carpeta / patron)))
    if not arch:
        return []
    with open(arch[-1], encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


pres = json.loads((DIR_ANALISIS / "presupuesto_dashboard.json").read_text(encoding="utf-8"))
serie = pres["serie_anual"]
p0, pN = serie[0], serie[-1]
crec = (pN["pia"] / p0["pia"] - 1) * 100

doc = Document()
# Estilo base
st = doc.styles["Normal"]
st.font.name = "Calibri"; st.font.size = Pt(11)


def h(txt, lvl=1):
    p = doc.add_heading(txt, level=lvl)
    for run in p.runs:
        run.font.color.rgb = ACCENT
    return p


def parr(txt, bold=False, italic=False, size=11):
    p = doc.add_paragraph()
    r = p.add_run(txt); r.bold = bold; r.italic = italic; r.font.size = Pt(size)
    return p


# --- Portada ---
t = doc.add_heading("Evaluación de la gestión del MIMP", 0)
for r in t.runs:
    r.font.color.rgb = ACCENT
parr("Ministerio de la Mujer y Poblaciones Vulnerables — pliego 039 · periodo 2017–2025", bold=True)
parr("¿Redujo la violencia de género, o solo gastó?", italic=True, size=13)
parr("Evaluación independiente a partir de datos abiertos oficiales. "
     "Fecha de corte de descargas: 2026-09-08. Repositorio reproducible: evaluacion-mimp.", size=9)
doc.add_paragraph()

# --- Resumen ejecutivo ---
h("1. Resumen ejecutivo")
parr(f"Entre 2017 y 2025 el MIMP casi triplicó su presupuesto (PIA de S/ {p0['pia']/1e6:.0f} millones a "
     f"S/ {pN['pia']/1e6:.0f} millones, +{crec:.0f}%) y lo ejecuta al {pN['ejecucion_pct']:.0f}%. Sin embargo, "
     "no hay evidencia consistente de que la violencia de género esté cediendo en los hechos: los feminicidios "
     "siguen estancados (130–170 casos al año), las denuncias por violencia sexual casi se duplicaron (+90% entre "
     "2016 y 2024) y el ministerio no cumple la meta que él mismo se fijó en su Política Nacional de Igualdad de "
     "Género. La única señal favorable —la prevalencia autorreportada de la ENDES— es metodológicamente discutible "
     "y está estancada desde 2020.")
parr("La gestión es diligente en el gasto, no en resultados: planta laboral precaria (99% en régimen CAS), "
     "cobertura de servicios concentrada en Lima y conducción institucional inestable (~15 titulares en 9 años). "
     "Salvaguarda: la violencia es un problema multisectorial; no se atribuye causalidad exclusiva al MIMP.")

# --- Hallazgos por dimensión ---
h("2. Hallazgos por dimensión")

h("2.1 Presupuesto y ejecución", 2)
tbl = doc.add_table(rows=1, cols=5); tbl.style = "Light Grid Accent 1"
for i, c in enumerate(["Año", "PIA (M S/)", "PIM (M S/)", "Devengado (M S/)", "Ejec. %"]):
    tbl.rows[0].cells[i].text = c
for r in serie:
    row = tbl.add_row().cells
    row[0].text = r["anio"]
    row[1].text = f"{r['pia']/1e6:.1f}"
    row[2].text = f"{r['pim']/1e6:.1f}"
    row[3].text = f"{r['devengado']/1e6:.1f}"
    row[4].text = f"{r['ejecucion_pct']:.1f}"
parr("El presupuesto crece de forma sostenida y la ejecución es alta (96–99%): la subejecución no es el problema. "
     "Fuente: MEF Datos Abiertos, pliego 039.", size=9, italic=True)

h("2.2 Impacto (contexto multisectorial)", 2)
femi = [r for r in leer("feminicidios_serie_*.csv") if r.get("feminicidios", "").isdigit()]
viol = [r for r in leer("violaciones_serie_*.csv") if r.get("denuncias_violacion", "").isdigit()]
if femi:
    parr(f"Feminicidios (registro Warmi Ñan): de {femi[0]['feminicidios']} ({femi[0]['anio']}) a "
         f"{femi[-1]['feminicidios']} ({femi[-1]['anio']}); oscilan sin descenso sostenido.")
if viol:
    parr(f"Denuncias por violencia sexual (INEI/PNP): de {viol[0]['denuncias_violacion']} ({viol[0]['anio']}) a "
         f"{viol[-1]['denuncias_violacion']} ({viol[-1]['anio']}), más de la mitad contra menores de edad. "
         "Paradoja de registros: más denuncias puede reflejar más violencia o más disposición a denunciar.")
parr("La prevalencia ENDES cae 13 pp (65%→52%), pero es autorreporte, con ruptura metodológica en 2020 y "
     "estancada desde entonces. No es prueba de que la violencia bajó ni de que sea mérito del MIMP.")

h("2.3 Meta prometida vs. resultado real", 2)
parr("La Política Nacional de Igualdad de Género (DS 008-2019-MIMP) fijó reducir la violencia física/sexual de "
     "pareja (últimos 12 meses) a 4,8% en 2026 y 2,4% en 2030. El dato real de 2024 es 7,5%, por encima de la meta "
     "de ese año (6,0%): el ministerio no va camino a cumplir su propia meta. Este es el hallazgo más difícil de refutar.")

h("2.4 Producción de servicios", 2)
parr("Las atenciones de los CEM se estabilizaron en ~165 000 desde 2021; la red de CEM está congelada en 433 desde "
     "2023 y solo 5 operan 24 horas. La cobertura, no la demanda, es el cuello de botella.")

h("2.5 Personal", 2)
pers = leer("personal_mimp_pte_*.csv")
if pers:
    total = sum(int(r["n_trabajadores"]) for r in pers if r.get("n_trabajadores", "").isdigit())
    parr(f"El sector Mujer emplea ~{total:,} personas, de las cuales el ~99% está en régimen CAS (contrato temporal). "
         "El programa que atiende la violencia (Warmi Ñan) tiene mediana salarial S/ 4 364, frente a S/ 30 000 de los "
         "altos funcionarios (Ley Servir): brecha de ~7 veces. Fuente: Portal de Transparencia (Perú Transparente).")

h("2.6 Territorio y gestión", 2)
parr("El gasto acumulado se concentra en Lima (S/ 4 155 millones); ningún otro departamento supera ~S/ 200 millones. "
     "La conducción es inestable: unas 15 titulares del ministerio en 9 años, con gestiones de pocos días. En paralelo, "
     "el marco normativo es abundante (Ley 30364, DL 1323, PNIG, Estrategia Nacional): mucha norma y gasto, poco resultado.")

# --- Contraste de hipótesis ---
h("3. Contraste de hipótesis (H1–H6)")
hip = [
    ("H1 — La violencia no disminuyó pese al gasto", "Se sostiene",
     "En los hechos verificables no hay reducción; solo una encuesta discutible sugiere mejora."),
    ("H2 — La producción de servicios está estancada", "Se sostiene",
     "Red de CEM congelada en 433, solo 5 en 24h; atenciones planas ~165k."),
    ("H3 — El presupuesto es bajo y/o se subejecuta", "El dinero no es la excusa",
     "No subejecuta (96–99%) y creció +134%; el problema no es la plata sino los resultados."),
    ("H4 — Brechas de cobertura territorial", "Se sostiene",
     "Lima concentra S/ 4 155 M; centralización extrema frente a violencia nacional."),
    ("H5 — Problemas de calidad/idoneidad", "Se sostiene",
     "99% CAS (precariedad), brecha salarial de 7x y rotación: calidad sostenida inviable."),
    ("H6 — Predomina la gestión de imagen sobre resultados", "Se sostiene",
     "Norma y gasto abundantes, metas incumplidas y hechos que no mejoran."),
]
for titulo, ver, txt in hip:
    p = doc.add_paragraph()
    p.add_run(titulo + " — ").bold = True
    r = p.add_run(ver + ". "); r.bold = True; r.font.color.rgb = ACCENT
    p.add_run(txt)

# --- Conclusiones y recomendaciones ---
h("4. Conclusiones")
parr("El MIMP gasta más y mejor en términos administrativos, pero no puede demostrar impacto en la violencia de "
     "género medida por hechos, y no cumple sus propias metas. La carga de probar que su acción funciona recae en el "
     "ministerio; hoy sus indicadores no la sostienen. Con las salvaguardas del caso (fenómeno multisectorial, sin "
     "atribución causal a un solo actor), la evaluación es crítica pero no acusatoria: diagnostica y propone.")

h("5. Recomendaciones")
for i, rec in enumerate([
    "Medir la gestión por hechos (feminicidios, denuncias, atenciones) y no principalmente por la encuesta autorreportada.",
    "Ampliar los CEM con atención 24 horas (hoy solo 5 de 433) y garantizar cobertura donde ocurre la violencia.",
    "Descentralizar el gasto según la incidencia territorial, corrigiendo la concentración en Lima.",
    "Estabilizar la conducción y profesionalizar la planta, reduciendo la dependencia del régimen CAS.",
    "Publicar personal, cobertura y ejecución por región en datos abiertos comparables.",
    "Encargar evaluaciones de impacto con contrafactual de los programas, no solo reportes de producción.",
], 1):
    doc.add_paragraph(rec, style="List Number")

# --- Limitaciones ---
h("6. Limitaciones y metodología")
parr("• Los indicadores de violencia son multisectoriales (Ministerio Público, Poder Judicial, Mininter/PNP, salud, "
     "educación): son contexto de contribución, no medida directa de eficacia del MIMP.")
parr("• Los conteos absolutos (feminicidios, denuncias) no están normalizados por población; la normalización por "
     "100 000 es una mejora pendiente. Los cambios penales (Ley 30364, 2015) elevan las denuncias mecánicamente.")
parr("• 2020 (COVID) rompe simultáneamente la serie ENDES, la prestación de servicios y las denuncias: es un factor "
     "de confusión reconocido.")
parr("• Registros administrativos y encuesta poblacional (ENDES) no son comparables entre sí.")
parr("• El dato de personal es un corte del Portal de Transparencia (no una serie anual). La violencia económica y el "
     "VIH en mujeres por departamento no tienen fuente oficial desagregada (marcados como no disponibles).")
parr("Todas las cifras son trazables a su fuente con URL y fecha de descarga (2026-09-08); ver Base_Datos_MIMP.xlsx, "
     "hoja Fuentes. Pipeline reproducible en el repositorio evaluacion-mimp.", size=9, italic=True)

DIR_ENTREGABLES.mkdir(exist_ok=True)
out = DIR_ENTREGABLES / "Informe_Evaluacion_MIMP.docx"
doc.save(out)
print(f"→ {out}")
