"""Fase 6 — Genera la imagen Open Graph (og.png) para compartir en redes.

Construye un SVG 1200x630 con el titular, las cifras clave y un mini-gráfico de
barras de feminicidios (el dato que 'incomoda'), y lo rasteriza a PNG con
rsvg-convert (WhatsApp/Twitter/Facebook no muestran SVG como og:image).

Uso:  python scripts/fase6_og.py   → docs/og.png (+ docs/og.svg)
"""
from __future__ import annotations

import csv
import glob
import subprocess

from config import DIR_CRUDA, RAIZ

# Feminicidios reales (registro Warmi Ñan) para el mini-gráfico.
femi = []
arch = sorted(glob.glob(str(DIR_CRUDA / "feminicidios_serie_*.csv")))
if arch:
    with open(arch[-1], encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["anio"] == "2026":
                continue
            try:
                femi.append((r["anio"], int(r["feminicidios"])))
            except (ValueError, KeyError):
                continue

# Geometría del mini-gráfico (barras) dentro del OG.
gx, gy, gw, gh = 690, 250, 440, 250
vmax = max((v for _, v in femi), default=170)
bars = ""
if femi:
    n = len(femi)
    bw = gw / n * 0.62
    step = gw / n
    for i, (a, v) in enumerate(femi):
        h = gh * v / (vmax * 1.12)
        x = gx + i * step + (step - bw) / 2
        y = gy + gh - h
        color = "#f0abfc" if i == n - 1 else "#a78bfa"
        bars += (f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{h:.0f}" rx="3" fill="{color}"/>'
                 f'<text x="{x+bw/2:.0f}" y="{y-8:.0f}" font-family="Arial" font-size="20" font-weight="700" '
                 f'fill="#ede9fe" text-anchor="middle">{v}</text>'
                 f'<text x="{x+bw/2:.0f}" y="{gy+gh+26:.0f}" font-family="Arial" font-size="17" '
                 f'fill="#c4b5fd" text-anchor="middle">{a}</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#2e1065"/><stop offset="1" stop-color="#4c1d95"/></linearGradient></defs>
<rect width="1200" height="630" fill="url(#bg)"/>
<rect x="0" y="0" width="12" height="630" fill="#f0abfc"/>
<text x="70" y="92" font-family="Georgia,serif" font-size="26" letter-spacing="2" fill="#c4b5fd">EVALUACIÓN DE LA GESTIÓN · MIMP · PLIEGO 039 · 2017–2025</text>
<text x="70" y="188" font-family="Georgia,serif" font-size="66" font-weight="700" fill="#ffffff">¿Redujo la violencia,</text>
<text x="70" y="262" font-family="Georgia,serif" font-size="66" font-weight="700" fill="#ffffff">o solo gastó?</text>
<text x="70" y="360" font-family="Arial" font-size="30" fill="#ede9fe">Presupuesto <tspan font-weight="700" fill="#86efac">+134%</tspan> · Ejecución <tspan font-weight="700" fill="#86efac">99%</tspan></text>
<text x="70" y="404" font-family="Arial" font-size="30" fill="#ede9fe">Prevalencia ENDES <tspan font-weight="700" fill="#f0abfc">−13 pp</tspan></text>
<text x="70" y="470" font-family="Arial" font-size="27" font-weight="700" fill="#fca5a5">Pero los feminicidios no ceden →</text>
<text x="70" y="504" font-family="Arial" font-size="23" fill="#c4b5fd">130–170 casos al año, sin descenso sostenido</text>
<text x="70" y="580" font-family="Arial" font-size="24" fill="#ddd6fe">unimauro.github.io/evaluacion-mimp · Datos oficiales MEF · INEI–ENDES · Warmi Ñan</text>
<text x="{gx}" y="{gy-24:.0f}" font-family="Arial" font-size="22" font-weight="700" fill="#ede9fe">Feminicidios por año (registro Warmi Ñan)</text>
<line x1="{gx}" y1="{gy+gh}" x2="{gx+gw}" y2="{gy+gh}" stroke="#7c5cc4" stroke-width="1.5"/>
{bars}
</svg>'''

docs = RAIZ / "docs"
docs.mkdir(exist_ok=True)
(docs / "og.svg").write_text(svg, encoding="utf-8")
subprocess.run(["rsvg-convert", "-w", "1200", "-h", "630",
                "-o", str(docs / "og.png"), str(docs / "og.svg")], check=True)
print(f"→ docs/og.png ({(docs / 'og.png').stat().st_size // 1024} KB) + docs/og.svg")
print(f"  feminicidios en el gráfico: {femi}")
