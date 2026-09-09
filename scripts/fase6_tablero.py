"""Fase 6 — Portal/tablero de la evaluación del MIMP (HTML standalone, GitHub Pages).

Integra:
  - presupuesto (03_analisis/presupuesto_dashboard.json, Fase 3)
  - prevalencia INEI-ENDES (01_data_cruda/endes_prevalencia_*.csv)
  - rotación de titulares (01_data_cruda/titulares_mimp_confirmado_*.csv)
  - marco normativo (01_data_cruda/normas_mimp_*.csv)
Incluye Google Analytics (gtag), Open Graph, favicon, storytelling inicial y el
contraste H1-H6. No inventa: grafica lo procesado y marca lo pendiente.

Uso:  python scripts/fase6_tablero.py  → 04_entregables/tablero_mimp.html y docs/index.html
"""
from __future__ import annotations

import csv
import glob
import json
from datetime import date

from config import DIR_ANALISIS, DIR_ENTREGABLES, DIR_CRUDA, RAIZ

GA_ID = "G-2CVE1EQ2L2"
# X-Client-Token del gateway ai.tunky.net. Vacío = el chat usa solo el respondedor
# local (datos del tablero). Pega aquí el token de Carlos para activar la IA generativa.
TUNKY_TOKEN = ""
_dash = DIR_ANALISIS / "presupuesto_dashboard.json"
if not _dash.exists():
    raise SystemExit("Falta 03_analisis/presupuesto_dashboard.json. Corre antes: python scripts/fase3_procesar_presupuesto.py")
data = json.loads(_dash.read_text(encoding="utf-8"))


def leer_csv(patron):
    arch = sorted(glob.glob(str(DIR_CRUDA / patron)))
    if not arch:
        return []
    with open(arch[-1], encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# --- ENDES: pivote año x tipo (solo cifras reales) ---
endes_rows = leer_csv("endes_prevalencia_*.csv")
endes = {"anios": [], "series": {}}
if endes_rows:
    tipos, por_anio = [], {}
    for r in endes_rows:
        try:
            val = float(r["prevalencia_pct"])
        except (ValueError, KeyError):
            continue  # [NO DISPONIBLE] u otros
        t = r["tipo_violencia"].strip().lower()
        a = r["anio"].strip()
        por_anio.setdefault(a, {})[t] = val
        if t not in tipos:
            tipos.append(t)
    endes["anios"] = sorted(por_anio)
    orden = [t for t in ["total", "psicologica", "psicológica", "fisica", "física", "sexual"] if t in tipos]
    orden += [t for t in tipos if t not in orden]
    endes["series"] = {t: [por_anio[a].get(t) for a in endes["anios"]] for t in orden}
    endes["fuente"] = endes_rows[0].get("url", "")

# --- Titulares (rotación) ---
tit_rows = leer_csv("titulares_mimp_confirmado_*.csv")
titulares = []
for r in tit_rows:
    ini, fin = r.get("fecha_inicio", "").strip(), r.get("fecha_fin", "").strip()
    titulares.append({"nombre": r.get("nombre", "").strip(), "inicio": ini, "fin": fin})

# --- Feminicidios y tentativas (registro Warmi Ñan; CONTEXTO multisectorial) ---
femi_rows = leer_csv("feminicidios_serie_*.csv")
femi = {"anios": [], "feminicidios": [], "tentativas": []}
for r in femi_rows:
    a = r.get("anio", "").strip()
    if a == "2026":  # preliminar (ene-jul), no comparable
        continue
    try:
        fm = int(r["feminicidios"]); tt = int(r["tentativas"])
    except (ValueError, KeyError):
        continue  # [NO DISPONIBLE]
    femi["anios"].append(a); femi["feminicidios"].append(fm); femi["tentativas"].append(tt)

# --- Violencia sexual: denuncias (INEI/MININTER-PNP; CONTEXTO, paradoja de registros) ---
viol_rows = leer_csv("violaciones_serie_*.csv")
violaciones = {"anios": [], "total": [], "menores": []}
for r in viol_rows:
    try:
        t = int(str(r["denuncias_violacion"]).replace(",", ""))
    except (ValueError, KeyError):
        continue
    violaciones["anios"].append(r["anio"]); violaciones["total"].append(t)
    try:
        violaciones["menores"].append(int(str(r["victimas_menores"]).replace(",", "")))
    except (ValueError, KeyError):
        violaciones["menores"].append(None)

# --- Producción de servicios (H2): atenciones CEM por tipo, Línea 100, N.º CEM ---
def num(x):
    try:
        return int(str(x).replace(",", ""))
    except (ValueError, TypeError):
        return None

cem_rows = leer_csv("cem_atenciones_por_tipo_*.csv")
cem = {"anios": [], "total": [], "psicologica": [], "fisica": [], "sexual": [], "economica": []}
for r in cem_rows:
    if num(r.get("total_atenciones")) is None:
        continue
    cem["anios"].append(r["anio"])
    for k, col in [("total", "total_atenciones"), ("psicologica", "psicologica"),
                   ("fisica", "fisica"), ("sexual", "sexual"), ("economica", "economica")]:
        cem[k].append(num(r.get(col)))

l100_rows = leer_csv("linea100_serie_*.csv")
linea100 = {"anios": [], "consultas": []}
for r in l100_rows:
    v = num(r.get("consultas"))
    if v is not None:
        linea100["anios"].append(r["anio"]); linea100["consultas"].append(v)

cemn_rows = leer_csv("cem_numero_serie_*.csv")
cem_num = {"anios": [], "total": [], "h24": []}
for r in cemn_rows:
    v = num(r.get("n_cem_total"))
    if v is not None:
        cem_num["anios"].append(r["anio"]); cem_num["total"].append(v); cem_num["h24"].append(num(r.get("n_cem_24h")))

# --- Embarazo adolescente (ENDES, solo ámbito Total; ruptura de serie documentada) ---
emb_rows = leer_csv("embarazo_adolescente_*.csv")
embarazo = {"periodos": [], "total": []}
for r in emb_rows:
    if r.get("ambito", "").strip().lower() != "total":
        continue
    try:
        v = float(r["valor_pct"])  # valida ANTES de añadir el periodo (evita desalinear NO DISPONIBLE)
    except (ValueError, KeyError):
        continue
    embarazo["periodos"].append(r["anio"]); embarazo["total"].append(v)

# --- DEMUNA % acreditadas (extraído de la nota; atenciones/conciliaciones no publicadas) ---
import re as _re
dem_rows = leer_csv("demuna_serie_*.csv")
demuna = {"anios": [], "acreditadas_pct": []}
for r in dem_rows:
    blob = " ".join(str(v) for v in r.values())  # CSV desalineado: buscar en toda la fila
    m = _re.search(r"([\d.]+)\s*%\s*de DEMUNA acreditadas", blob)
    if m:
        demuna["anios"].append(r["anio"]); demuna["acreditadas_pct"].append(float(m.group(1)))

# --- Meta PNIG vs real (indicador central de violencia, últimos 12 meses) ---
mv_rows = leer_csv("violencia_12meses_real_*.csv")
metaviol = {"anios": [], "real": [], "meta": []}
for r in mv_rows:
    metaviol["anios"].append(r["anio"])
    try:
        metaviol["real"].append(float(r["valor_pct"]))
    except (ValueError, KeyError):
        metaviol["real"].append(None)
    try:
        metaviol["meta"].append(float(r["meta_pnig"]))
    except (ValueError, KeyError):
        metaviol["meta"].append(None)

# --- Tabla de metas de los planes (solo con meta numérica) ---
meta_rows = leer_csv("metas_planes_*.csv")
metas = []
for r in meta_rows:
    mv = str(r.get("meta_valor", "")).strip()
    if not mv or "DISPONIBLE" in mv:
        continue
    metas.append({"instrumento": r.get("instrumento", ""), "indicador": r.get("indicador", ""),
                  "lb": r.get("linea_base_valor", ""), "lb_anio": r.get("linea_base_anio", ""),
                  "meta": mv, "meta_anio": r.get("meta_anio", ""), "url": r.get("url", ""),
                  "real": "", "estado": "sd"})

# Cruce con nuestras series: real reciente + juicio (solo donde hay dato verificable).
for m in metas:
    ind = m["indicador"].lower()
    if "violencia fisica y/o sexual" in ind or "violencia física y/o sexual" in ind:
        m["real"] = "7.5% (2024)"; m["estado"] = "no"      # real muy por encima de una meta que debe bajar
    elif "embarazo adolescente" in ind:
        m["real"] = "8.4% (2024)"; m["estado"] = "parcial"  # bajó de 13.4 pero sigue sobre la meta 7.2 (ruptura de serie)

# --- Normas ---
norm_rows = leer_csv("normas_mimp_*.csv")
normas = [{"tipo": r.get("tipo", ""), "numero": r.get("numero", ""), "nombre": r.get("nombre", ""),
           "anio": r.get("anio", ""), "url": r.get("url", "")} for r in norm_rows]

# --- Violencia por departamento (para el mapa coroplético) ---
dep_rows = leer_csv("violencia_por_departamento_*.csv")
mapa_dep = {}
for r in dep_rows:
    d = r.get("departamento", "").strip()
    if not d or d == "TOTAL_NACIONAL":
        continue
    def _gi(k):
        try:
            return int(str(r.get(k, "")).replace(",", ""))
        except (ValueError, TypeError):
            return None
    mapa_dep[d] = {"feminicidios": _gi("feminicidios"), "denuncias": _gi("denuncias_violencia_sexual"),
                   "atenciones": _gi("atenciones_cem")}

# --- Personal (Portal de Transparencia vía repo peru-transparente) ---
pers_rows = leer_csv("personal_mimp_pte_*.csv")
_agg = {}
personal = {"unidades": [], "por_regimen": {}, "total": 0, "servir_med": None, "atiende_med": None}
for r in pers_rows:
    try:
        n = int(r["n_trabajadores"]); med = float(r["sueldo_mediana"])
    except (ValueError, KeyError):
        continue
    u = r["unidad"]; reg = r["regimen"]
    a = _agg.setdefault(u, {"n": 0, "med": 0, "maxn": -1, "min": 0, "max": 0})
    a["n"] += n
    if n > a["maxn"]:
        a["maxn"] = n; a["med"] = med
        try:
            a["min"] = float(r.get("sueldo_min", 0)); a["max"] = float(r.get("sueldo_maximo", 0))
        except (ValueError, TypeError):
            pass
    personal["por_regimen"][reg] = personal["por_regimen"].get(reg, 0) + n
    personal["total"] += n
    if "Ley Servir" in reg:
        personal["servir_med"] = med
    if "Warmi" in u:
        personal["atiende_med"] = med
for u, a in _agg.items():
    personal["unidades"].append({"unidad": u, "n": a["n"], "mediana": a["med"],
                                 "min": a.get("min", 0), "max": a.get("max", 0)})
personal["unidades"].sort(key=lambda x: -x["n"])

payload = {"presupuesto": data, "endes": endes, "titulares": titulares, "normas": normas, "personal": personal,
           "mapa_dep": mapa_dep,
           "feminicidios": femi, "cem": cem, "linea100": linea100, "cem_num": cem_num,
           "embarazo": embarazo, "demuna": demuna, "violaciones": violaciones,
           "metaviol": metaviol, "metas": metas, "generado": date.today().isoformat()}

HTML = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://www.googletagmanager.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; img-src 'self' data: https://cdnjs.cloudflare.com https://www.googletagmanager.com https://www.google-analytics.com; font-src 'self' data:; connect-src 'self' https://ai.tunky.net https://www.google-analytics.com https://region1.google-analytics.com https://www.googletagmanager.com; base-uri 'self'; form-action 'self'; object-src 'none'; frame-src 'none'">
<title>¿El MIMP redujo la violencia?</title>
<meta name="description" content="Evaluación de la gestión del MIMP (pliego 039) 2017-2025: triplicó su presupuesto y lo ejecuta al 99%, pero los feminicidios no ceden y las denuncias por violencia sexual casi se duplicaron. ¿Impacto real o solo gasto?">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='20' fill='%236d28d9'/%3E%3Ctext x='50' y='72' font-size='62' text-anchor='middle' fill='white' font-family='Georgia,serif'%3E%E2%99%80%3C/text%3E%3C/svg%3E">
<meta property="og:type" content="website">
<meta property="og:title" content="¿El MIMP redujo la violencia, o solo gastó?">
<meta property="og:description" content="Triplicó su presupuesto (S/ 426M→996M) y lo ejecuta al 99%, pero los feminicidios no ceden (130–170/año) y las denuncias por violencia sexual casi se duplicaron. ¿Impacto real o solo gasto?">
<meta property="og:url" content="https://unimauro.github.io/evaluacion-mimp/">
<meta property="og:image" content="https://unimauro.github.io/evaluacion-mimp/og.png?v=3">
<meta property="og:image:secure_url" content="https://unimauro.github.io/evaluacion-mimp/og.png?v=3">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Evaluación del MIMP 2017-2025: presupuesto, prevalencia y feminicidios">
<meta property="og:site_name" content="Evaluación MIMP">
<meta property="og:locale" content="es_PE">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="¿El MIMP redujo la violencia, o solo gastó?">
<meta name="twitter:description" content="Triplicó su presupuesto y lo ejecuta al 99%, pero los feminicidios no ceden y las denuncias por violencia sexual casi se duplicaron.">
<meta name="twitter:image" content="https://unimauro.github.io/evaluacion-mimp/og.png?v=3">
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=__GA__"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '__GA__');
</script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
<style>
:root{
  --surface:#faf7fc; --panel:#ffffff; --ink:#1a1420; --ink-2:#544b60; --muted:#6b6276;
  --line:#ece5f2; --line-2:#ddd3e6; --accent:#6d28d9; --accent-2:#b31f83; --ground:#f2ecf7;
  --good:#0a7d43; --warn:#b7791a; --crit:#d13b6a;
  --s1:#6d28d9; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100; --s5:#c0248f; --s6:#2a78d6; --s7:#0a7d43; --s8:#d13b3b;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --surface:#15111b; --panel:#201a29; --ink:#f4f0f8; --ink-2:#c6bdd2; --muted:#948aa3;
  --line:#2e2739; --line-2:#3c3448; --accent:#a78bfa; --accent-2:#ec7ac6; --ground:#120e18;
  --good:#42ab68; --warn:#dda63a; --crit:#e56a91;
  --s1:#a78bfa; --s2:#e8814f; --s3:#199e70; --s4:#c98500; --s5:#e267b3; --s6:#5b9bf0; --s7:#42ab68; --s8:#e46464;
}}
:root[data-theme="dark"]{
  --surface:#15111b; --panel:#201a29; --ink:#f4f0f8; --ink-2:#c6bdd2; --muted:#948aa3;
  --line:#2e2739; --line-2:#3c3448; --accent:#a78bfa; --accent-2:#ec7ac6; --ground:#120e18;
  --good:#42ab68; --warn:#dda63a; --crit:#e56a91;
  --s1:#a78bfa; --s2:#e8814f; --s3:#199e70; --s4:#c98500; --s5:#e267b3; --s6:#5b9bf0; --s7:#42ab68; --s8:#e46464;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}
.skip-link{position:absolute;left:-999px;top:8px;background:var(--accent);color:#fff;padding:8px 14px;border-radius:8px;z-index:99}
.skip-link:focus{left:8px}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *,*::before,*::after{animation-duration:.001ms!important;transition-duration:.001ms!important}
  .sem:hover{transform:none}
}
body{margin:0;background:var(--surface);color:var(--ink);
  font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
img{max-width:100%}
.layout{display:grid;grid-template-columns:232px 1fr;min-height:100vh}
aside{position:sticky;top:0;align-self:start;height:100vh;overflow-y:auto;
  background:var(--panel);border-right:1px solid var(--line);padding:22px 18px}
aside .brand{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-weight:700;font-size:19px;line-height:1.1;letter-spacing:-.01em}
aside .brand span{color:var(--accent)}
aside .tag{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin-top:4px}
aside nav{margin-top:22px;display:flex;flex-direction:column;gap:2px}
aside nav a{font-size:13.5px;color:var(--ink-2);text-decoration:none;padding:8px 10px;border-radius:8px}
aside nav a:hover{background:var(--ground);color:var(--ink)}
aside nav a.active{background:var(--ground);color:var(--accent);font-weight:600}
main>section[hidden]{display:none}
aside nav a.sec{margin-top:12px;font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);pointer-events:none;padding-bottom:2px}
aside .foot{margin-top:24px;font-size:11.5px;color:var(--muted);line-height:1.5}
main{min-width:0;padding:34px 40px 80px;max-width:1080px}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:700}
h1{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-weight:700;font-size:clamp(30px,4.6vw,50px);line-height:1.02;margin:.2em 0 .2em;text-wrap:balance;letter-spacing:-.015em}
.dek{color:var(--ink-2);max-width:64ch;font-size:17px;line-height:1.5}
.src{color:var(--muted);font-size:12.5px;margin-top:14px}
.src code{background:var(--ground);padding:1px 5px;border-radius:4px}

.story{display:grid;grid-template-columns:1.05fr .95fr;gap:24px;margin:30px 0 10px;align-items:stretch}
.story .tell{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:22px 24px}
.story .tell h2{margin-top:0}
.story .tell p{color:var(--ink-2);font-size:14.5px}
.story .tell .big{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:19px;color:var(--ink);line-height:1.4;font-weight:600;margin:0 0 12px}
.story .tell .big b.up{color:var(--good)} .story .tell .big b.dn{color:var(--accent-2)}
.story .viz{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px 18px 12px;display:flex;flex-direction:column}
.story .viz h3{margin:0 0 2px;font-size:14px} .story .viz p.cap{margin:0 0 8px;font-size:12px;color:var(--muted)}
.story .viz .chart-box{flex:1;min-height:250px}

.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));gap:13px;margin:8px 0}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:15px 17px}
.kpi .k-label{font-size:11.5px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);font-weight:600}
.kpi .k-val{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:27px;font-weight:600;margin-top:5px;font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.kpi .k-note{font-size:12px;color:var(--ink-2);margin-top:2px}
.k-up{color:var(--good)} .k-dn{color:var(--accent-2)} .k-flat{color:var(--warn)}

section{margin-top:46px;scroll-margin-top:16px}
h2{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-weight:600;font-size:24px;margin:0 0 4px;letter-spacing:-.01em}
.lead{color:var(--ink-2);font-size:14px;margin:0 0 18px;max-width:82ch}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:17px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:17px 18px 13px}
.card h3{font-size:14.5px;font-weight:700;margin:0 0 2px}
.card p.cap{font-size:12.5px;color:var(--muted);margin:0 0 12px}
.chart-box{position:relative;height:300px}
.chart-box.tall{height:360px}
.full{grid-column:1/-1}

.hyp{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
.hcard{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 17px;border-left:4px solid var(--muted)}
.hcard.v-no{border-left-color:var(--good)} .hcard.v-si{border-left-color:var(--crit)}
.hcard.v-parc{border-left-color:var(--warn)} .hcard.v-pend{border-left-color:var(--line-2)}
.hcard .hid{font-size:12px;font-weight:700;letter-spacing:.08em;color:var(--muted)}
.hcard h4{margin:4px 0 6px;font-size:15px;font-weight:700;line-height:1.3}
.verdict{display:inline-block;font-size:11.5px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;padding:3px 9px;border-radius:20px;margin-bottom:8px}
.verdict.v-no{background:rgba(10,125,67,.14);color:var(--good)}
.verdict.v-si{background:rgba(207,59,57,.14);color:var(--crit)}
.verdict.v-parc{background:rgba(183,121,26,.16);color:var(--warn)}
.verdict.v-pend{background:var(--ground);color:var(--muted)}
.hcard p{margin:0;font-size:13.2px;color:var(--ink-2)}
.sem-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-top:8px}
.sem{display:block;text-decoration:none;background:var(--panel);border:1px solid var(--line);border-top:4px solid var(--muted);border-radius:12px;padding:14px 15px;transition:transform .12s}
.sem:hover{transform:translateY(-2px)}
.sem.v-no{border-top-color:var(--good)} .sem.v-si{border-top-color:var(--crit)}
.sem.v-parc{border-top-color:var(--warn)} .sem.v-pend{border-top-color:var(--line-2)}
.sem .dot{display:inline-block;width:11px;height:11px;border-radius:50%;background:var(--muted);vertical-align:middle;margin-right:7px}
.sem.v-no .dot{background:var(--good)} .sem.v-si .dot{background:var(--crit)}
.sem.v-parc .dot{background:var(--warn)} .sem.v-pend .dot{background:var(--line-2)}
.sem b{font-size:13px;color:var(--ink)} .sem i{display:block;font-style:normal;font-weight:700;font-size:15px;margin:5px 0 3px}
.sem.v-no i{color:var(--good)} .sem.v-si i{color:var(--crit)} .sem.v-parc i{color:var(--warn)} .sem.v-pend i{color:var(--muted)}
.sem small{color:var(--ink-2);font-size:12px;line-height:1.35;display:block}
.evol-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(186px,1fr));gap:12px;margin:20px 0 4px}
.evol{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 15px 13px;position:relative;overflow:hidden}
.evol::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--muted)}
.evol.up::before{background:var(--good)} .evol.down::before{background:var(--crit)} .evol.flat::before{background:var(--warn)} .evol.info::before{background:var(--accent)}
.evol .e-lbl{font-size:11.5px;text-transform:uppercase;letter-spacing:.03em;color:var(--muted);font-weight:600;line-height:1.25}
.evol .e-now{font-size:26px;font-weight:700;margin:7px 0 1px;font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.evol .e-chg{font-size:13px;font-weight:700}
.evol.up .e-chg{color:var(--good)} .evol.down .e-chg{color:var(--crit)} .evol.flat .e-chg{color:var(--warn)} .evol.info .e-chg{color:var(--accent)}
.evol .e-from{font-size:12px;color:var(--ink-2);margin-top:3px;font-variant-numeric:tabular-nums}

.faq details{background:var(--panel);border:1px solid var(--line);border-radius:12px;margin-bottom:10px;overflow:hidden}
.faq summary{cursor:pointer;padding:15px 46px 15px 18px;font-weight:700;font-size:14.5px;list-style:none;position:relative}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";position:absolute;right:18px;top:12px;font-size:21px;color:var(--accent);font-weight:400}
.faq details[open] summary::after{content:"−"}
.faq details[open] summary{border-bottom:1px solid var(--line)}
.faq .fa-body{padding:14px 18px;font-size:13.6px;color:var(--ink-2);line-height:1.58}
.faq .fa-body b{color:var(--ink)}
.verdict-card{background:var(--panel);border:1px solid var(--line);border-left:5px solid var(--accent-2);border-radius:14px;margin:20px 0 6px;overflow:hidden;max-width:860px}
.verdict-card>summary{cursor:pointer;list-style:none;padding:17px 48px 17px 20px;font-weight:700;font-size:20px;color:var(--ink);position:relative;letter-spacing:-.01em}
.verdict-card>summary::-webkit-details-marker{display:none}
.verdict-card>summary::after{content:"−";position:absolute;right:20px;top:15px;font-size:22px;color:var(--accent-2)}
.verdict-card:not([open])>summary::after{content:"+"}
.verdict-card .vc-body{padding:2px 24px 20px;color:var(--ink-2);font-size:16px;line-height:1.62}
.verdict-card .vc-body p{margin:0 0 13px}
.verdict-card .vc-body b{color:var(--ink)}
.verdict-card .vc-body .src{font-size:12.5px;color:var(--muted);margin-top:12px}
.verdict-card .vc-body .src code{background:var(--ground);padding:1px 5px;border-radius:4px}
.vs-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.vs-col{border:1px solid var(--line);border-radius:14px;padding:18px 20px;background:var(--panel)}
.vs-soft{border-top:4px solid var(--good)}
.vs-hard{border-top:4px solid var(--crit)}
.vs-tag{font-size:11px;text-transform:uppercase;letter-spacing:.06em;font-weight:700;margin-bottom:6px}
.vs-soft .vs-tag{color:var(--good)} .vs-hard .vs-tag{color:var(--crit)}
.vs-col h3{margin:0 0 12px;font-size:16px}
.vs-col ul{margin:0;padding-left:0;list-style:none}
.vs-col li{position:relative;padding:8px 0 8px 24px;font-size:13.6px;color:var(--ink-2);border-bottom:1px solid var(--line);line-height:1.45}
.vs-col li:last-child{border-bottom:none}
.vs-col li::before{position:absolute;left:0;top:8px;font-weight:700}
.vs-soft li::before{content:"▼";color:var(--good);font-size:11px;top:10px}
.vs-hard li::before{content:"▲";color:var(--crit);font-size:11px;top:10px}
.vs-col li b{color:var(--ink)}
@media (max-width:720px){.vs-grid{grid-template-columns:1fr}}
ol.recos{counter-reset:r;list-style:none;padding:0;margin:14px 0 0;display:grid;gap:11px}
ol.recos li{counter-increment:r;position:relative;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px 14px 52px;font-size:14px;color:var(--ink-2);line-height:1.5}
ol.recos li::before{content:counter(r);position:absolute;left:14px;top:13px;width:26px;height:26px;background:var(--accent);color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px}
ol.recos li b{color:var(--ink)}
.vh-card{border:1px solid var(--line);border-left:5px solid var(--crit);border-radius:14px;padding:18px 22px;background:var(--panel)}
.vh-card.vh-good{border-left-color:var(--good)}
.vh-tag{font-size:11px;text-transform:uppercase;letter-spacing:.08em;font-weight:700;color:var(--crit);margin-bottom:12px}
.vh-card.vh-good .vh-tag{color:var(--good)}
.vh-row{display:flex;align-items:flex-end;gap:22px;flex-wrap:wrap;margin-bottom:14px}
.vh-metric{display:flex;flex-direction:column}
.vh-big{font-size:42px;font-weight:700;line-height:1;font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.vh-sub{font-size:11.5px;color:var(--muted);margin-top:5px;text-transform:uppercase;letter-spacing:.04em}
.vh-vs{font-size:15px;color:var(--muted);align-self:center;font-weight:600;padding-bottom:6px}
.vh-card p{margin:0;font-size:14.5px;color:var(--ink-2);line-height:1.55}
.vh-card p b{color:var(--ink)}
@media (max-width:560px){.vh-big{font-size:34px}.vh-row{gap:16px}}
.note{background:var(--ground);border:1px solid var(--line);border-left:3px solid var(--warn);border-radius:10px;padding:14px 16px;font-size:13.5px;color:var(--ink-2)}
.note b{color:var(--ink)}
table.norm{width:100%;border-collapse:collapse;font-size:13px}
table.norm th,table.norm td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}
table.norm th{color:var(--muted);font-weight:600;font-size:11.5px;text-transform:uppercase;letter-spacing:.04em}
table.norm a{color:var(--accent);text-decoration:none}
.tablewrap{overflow-x:auto}
.badge{font-size:11px;font-weight:700;padding:2px 9px;border-radius:12px;white-space:nowrap;display:inline-block}
.badge.e-no{background:rgba(207,59,57,.16);color:var(--crit)}
.badge.e-parc{background:rgba(183,121,26,.18);color:var(--warn)}
.badge.e-si{background:rgba(10,125,67,.15);color:var(--good)}
.badge.e-sd{background:var(--ground);color:var(--muted)}
.mapa-tabs{display:flex;flex-wrap:wrap;gap:7px;margin:6px 0 12px}
.mapa-tabs button{font-size:12.5px;border:1px solid var(--line-2);background:var(--panel);color:var(--ink-2);border-radius:16px;padding:6px 13px;cursor:pointer;font-family:inherit}
.mapa-tabs button.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.leaflet-container{background:var(--ground)!important;font-family:inherit}
.leaflet-tooltip{background:var(--panel);color:var(--ink);border:1px solid var(--line);box-shadow:0 4px 14px rgba(0,0,0,.2);font-size:12.5px}
.leaflet-tooltip b{color:var(--ink)}
.mapa-leyenda{background:var(--panel);padding:8px 10px;border-radius:8px;border:1px solid var(--line);font-size:11.5px;color:var(--ink-2);line-height:1.7}
.mapa-leyenda i{display:inline-block;width:14px;height:14px;margin-right:6px;border-radius:3px;vertical-align:middle}
footer{margin-top:54px;border-top:1px solid var(--line);padding-top:18px;color:var(--muted);font-size:12.5px}
.toggle{position:fixed;top:12px;right:12px;background:var(--panel);border:1px solid var(--line-2);color:var(--ink-2);border-radius:20px;padding:6px 13px;font-size:12.5px;cursor:pointer;font-family:inherit;z-index:6}
.menu-btn{display:none;background:var(--ground);border:1px solid var(--line-2);border-radius:9px;width:42px;height:38px;font-size:19px;color:var(--ink);cursor:pointer;line-height:1}
.chat-fab{position:fixed;bottom:20px;right:20px;width:56px;height:56px;border-radius:50%;background:var(--accent);border:none;cursor:pointer;box-shadow:0 6px 22px rgba(109,40,217,.42);z-index:20;display:flex;align-items:center;justify-content:center}
.chat-fab.hide{display:none}
.chat-panel{position:fixed;bottom:20px;right:20px;width:min(380px,calc(100vw - 28px));height:min(560px,calc(100vh - 40px));background:var(--panel);border:1px solid var(--line);border-radius:16px;box-shadow:0 14px 44px rgba(30,15,45,.28);z-index:21;display:none;flex-direction:column;overflow:hidden}
.chat-panel:not([hidden]){display:flex}
.chat-top{display:flex;align-items:center;gap:10px;padding:13px 16px;background:var(--accent);color:#fff}
.chat-top b{font-size:13.5px;display:block}.chat-top span{font-size:11px;opacity:.85}
.chat-dot{width:8px;height:8px;border-radius:50%;background:#7cfca0;box-shadow:0 0 0 3px rgba(124,252,160,.3)}
.chat-x{margin-left:auto;background:none;border:none;color:#fff;font-size:17px;cursor:pointer;line-height:1}
.chat-log{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:9px}
.msg{max-width:86%;padding:9px 12px;border-radius:13px;font-size:13.4px;line-height:1.45;white-space:pre-wrap}
.msg.me{align-self:flex-end;background:var(--accent);color:#fff;border-bottom-right-radius:3px}
.msg.bot{align-self:flex-start;background:var(--ground);color:var(--ink);border-bottom-left-radius:3px}
.chat-suggest{display:flex;flex-wrap:wrap;gap:6px}
.chat-suggest button{font-size:12px;border:1px solid var(--line-2);background:var(--panel);color:var(--ink-2);border-radius:16px;padding:5px 10px;cursor:pointer;font-family:inherit}
.chat-form{display:flex;gap:8px;padding:11px;border-top:1px solid var(--line)}
.chat-form input{flex:1;border:1px solid var(--line-2);border-radius:20px;padding:9px 14px;font-family:inherit;font-size:13.4px;background:var(--surface);color:var(--ink)}
.chat-form button{background:var(--accent);border:none;border-radius:50%;width:38px;height:38px;color:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.typing i{display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--muted);margin:0 1px;animation:blink 1.2s infinite}
.typing i:nth-child(2){animation-delay:.2s}.typing i:nth-child(3){animation-delay:.4s}
@keyframes blink{0%,60%,100%{opacity:.3}30%{opacity:1}}
@media (prefers-reduced-motion:reduce){.typing i{animation:none}}
@media (max-width:860px){
  .layout{grid-template-columns:1fr;min-height:0}
  aside{position:sticky;top:0;z-index:12;height:auto;border-right:none;border-bottom:1px solid var(--line);padding:12px 16px}
  aside:empty{display:none}
  .menu-btn{display:block;position:absolute;top:11px;right:14px}
  aside .brand{font-size:18px}
  aside .tag{display:none}
  aside nav{display:none;margin-top:12px;flex-direction:column;gap:1px}
  aside nav.open{display:flex}
  aside nav a{font-size:14px;padding:11px 12px;border-radius:8px}
  aside nav a.sec{display:block;margin-top:10px;pointer-events:none}
  aside .foot{display:none}
  main{padding:22px 16px 64px}
  .toggle{top:auto;bottom:88px;right:14px}
  h1{font-size:31px}
  .dek{font-size:15.5px}
  .story{grid-template-columns:1fr}
  .story .tell,.story .viz{padding:16px 16px}
  .story .tell .big{font-size:16.5px}
  .kpi .k-val{font-size:24px}
  section{margin-top:34px}
}
</style>
</head>
<body>
<a href="#resumen" class="skip-link">Saltar al contenido</a>
<button class="toggle" id="tgl" aria-label="Cambiar tema (claro/oscuro)" aria-pressed="false">◐ Tema</button>
<div class="layout">
  <aside>
    <button class="menu-btn" id="menuBtn" aria-label="Abrir menú" aria-expanded="false" aria-controls="navMenu">☰</button>
    <div class="brand">Evaluación <span>MIMP</span></div>
    <div class="tag">Pliego 039 · 2017–2025</div>
    <nav id="navMenu" aria-label="Secciones de la evaluación">
      <a href="#resumen">Resumen</a>
      <a class="sec">Dimensiones</a>
      <a href="#impacto">Impacto: ¿bajó la violencia?</a>
      <a href="#metas">Meta vs. resultado</a>
      <a href="#servicios">Producción de servicios</a>
      <a href="#ninez">Niñez y adolescencia</a>
      <a href="#presupuesto">Presupuesto y ejecución</a>
      <a href="#planilla">Personal y planilla</a>
      <a href="#gasto">¿En qué se gasta?</a>
      <a href="#territorio">Territorio</a>
      <a href="#gestion">Gestión y rotación</a>
      <a href="#normas">Marco normativo</a>
      <a class="sec">Conclusión</a>
      <a href="#contraste">Encuesta vs. hechos</a>
      <a href="#hipotesis">Hipótesis H1–H6</a>
      <a href="#conclusion">Conclusión y recomendaciones</a>
      <a href="#faq">Preguntas frecuentes</a>
    </nav>
    <div class="foot">Datos oficiales: MEF, INEI–ENDES, Portal Warmi Ñan, El Peruano.<br>Descarga 2026-09-08. Reproducible.</div>
  </aside>

  <main id="inicio">
    <section id="resumen">
    <div class="eyebrow">Evaluación de la gestión pública</div>
    <h1>¿El MIMP redujo la violencia, o solo gastó?</h1>
    <details class="verdict-card" open>
      <summary>La evaluación en corto: no hay mayores mejoras</summary>
      <div class="vc-body">
        <p>Entre 2017 y 2025 el Ministerio de la Mujer <b>casi triplicó su presupuesto</b> y lo ejecuta casi al 100%.
          Pero los <b>hechos registrados no acompañan</b>: los feminicidios siguen en 130–170 al año y las denuncias
          por violencia sexual <b>casi se duplicaron</b>.</p>
        <p>La única "mejora" —la encuesta ENDES— es <b>metodológicamente discutible</b> y se estancó desde 2020.
          La pregunta no es si gastó bien, sino <b>cuánto cumplió de lo que sus propios planes prometieron</b>.</p>
        <p class="src">Fuentes: MEF Datos Abiertos (pliego <code>039</code>), INEI–ENDES, Portal Warmi Ñan,
          El Peruano · descarga <code>2026-09-08</code> · soles corrientes.</p>
      </div>
    </details>

    <div style="margin-top:26px"><span class="eyebrow" style="color:var(--accent-2)">De hace una década a hoy</span></div>
    <div class="evol-grid" id="evol"></div>

    <div class="story">
      <div class="tell">
        <h2>La historia en tres cifras</h2>
        <p class="big">1 · El presupuesto <b class="up">creció +134%</b> (S/ 426 M → 996 M) y la ejecución fue
          <b class="up">96–99%</b> todos los años: el MIMP <b>no subejecuta</b>.</p>
        <p class="big">2 · La prevalencia bajó de 65% a 52% (ENDES), pero <b class="dn">el grueso fue en 2017–2019</b>;
          desde 2020 se <b class="dn">estancó</b> (~52–55%) y los <b class="dn">feminicidios no ceden</b> (130–170/año).</p>
        <p class="big">3 · Pero hubo <b class="dn">~15 ministras/os en 9 años</b>: la conducción es
          <b>inestable</b> pese a un marco normativo sólido.</p>
        <p style="margin-bottom:0"><b>Salvaguarda:</b> la caída de la violencia es multisectorial (contribución, no
          atribución); los registros administrativos no se comparan con la prevalencia poblacional.</p>
      </div>
      <div class="viz">
        <h3>Gasto que se triplica, feminicidios que no ceden</h3>
        <p class="cap">Devengado del MIMP (millones S/) vs. feminicidios registrados (casos). Dos escalas.</p>
        <div class="chart-box"><canvas id="c_story"></canvas></div>
      </div>
    </div>

    <div class="kpis" id="kpis"></div>

    <div style="margin-top:34px">
      <div class="eyebrow" style="color:var(--accent-2)">Veredicto de impacto</div>
      <h2 style="font-size:26px;margin:6px 0 4px">¿El accionar del MIMP tiene impacto real?</h2>
      <p class="lead" style="max-width:74ch">Lectura rápida de las seis hipótesis (H1–H6). La evidencia es contundente:
        <b>cinco de las seis se sostienen</b>. El gasto se triplicó y se ejecuta al 99%, pero los hechos que importan
        no mejoran y el ministerio no cumple sus propias metas. <b>El dinero no es el problema; los resultados sí.</b>
        Toca un recuadro para ver el detalle.</p>
      <div class="sem-grid">
        <a class="sem v-si" href="#impacto"><span class="dot"></span><b>H1 · Impacto</b><i>Se sostiene</i><small>Feminicidios estancados, denuncias sexuales +90%, meta incumplida</small></a>
        <a class="sem v-si" href="#servicios"><span class="dot"></span><b>H2 · Servicios</b><i>Se sostiene</i><small>Red de CEM congelada en 433, solo 5 en 24h; atenciones planas ~165k</small></a>
        <a class="sem v-parc" href="#presupuesto"><span class="dot"></span><b>H3 · Presupuesto</b><i>No es la excusa</i><small>Ejecuta 96–99% y PIA +134%: el dinero se gasta, sin resultados</small></a>
        <a class="sem v-si" href="#territorio"><span class="dot"></span><b>H4 · Cobertura</b><i>Se sostiene</i><small>Lima acapara S/ 4 155 M; ningún otro pasa de ~S/ 200 M</small></a>
        <a class="sem v-si" href="#planilla"><span class="dot"></span><b>H5 · Calidad</b><i>Se sostiene</i><small>99% CAS (precario) y brecha salarial de 7× frente a la cúpula</small></a>
        <a class="sem v-si" href="#gestion"><span class="dot"></span><b>H6 · Gestión</b><i>Se sostiene</i><small>~15 titulares en 9 años, metas incumplidas: forma sobre fondo</small></a>
      </div>
    </div>
    </section>

  <section id="impacto" hidden>
    <h2>Impacto: ¿bajó la violencia de género?</h2>
    <p class="lead">Depende de qué se mire, y por eso <b>no basta con el ENDES</b>. La <b>encuesta</b> (autorreporte)
      sugiere una caída del total, pero es discutible y se estancó desde 2020. Los <b>hechos registrados</b> dicen otra
      cosa: los <b>feminicidios no ceden</b> y las <b>denuncias por violencia sexual casi se duplicaron</b>. Aquí, las
      tres miradas juntas —para no quedarse con el dato más cómodo.</p>

    <div class="grid"><div class="card full"><h3>1 · Prevalencia por tipo de violencia (ENDES)</h3><p class="cap">% de mujeres · <b>autorreporte</b> de "alguna vez" · ⚠ ruptura metodológica en 2020 (INEI cambió de promedios bienales a años simples)</p><div class="chart-box tall"><canvas id="c_endes"></canvas></div></div></div>
    <div class="note" style="margin-top:12px"><b>Contribución, no atribución.</b> La encuesta cae 13 pp (65%→52%) entre 2017 y 2024,
      pero el grueso fue <b>2017–2019</b> y desde 2020 se estancó (~52–55%). La caída es multisectorial (MP, PJ, Mininter, salud,
      educación, sociedad civil), no atribuible solo al MIMP. La violencia <b>económica</b> no la mide la ENDES (corresponde a
      ENARES); <b>pero sí se registra en las atenciones de los CEM</b>: unos <b>620–735 casos al año</b> (ver <i>Producción de
      servicios</i>) — el cruce muestra que existe, aunque poco captada. Fuente: INEI–ENDES, Series Anuales 1986–2024, Cuadro 11.1.</div>

    <div class="grid" style="margin-top:18px"><div class="card full"><h3>2 · Feminicidios y tentativas (contexto)</h3><p class="cap">Casos registrados por año · registro Warmi Ñan · <b>contexto multisectorial</b></p><div class="chart-box"><canvas id="c_femi"></canvas></div></div></div>
    <div class="note" style="margin-top:12px"><b>El dato que incomoda:</b> mientras la prevalencia poblacional bajó, los <b>feminicidios no descienden</b>
      (oscilan 130–170 al año). La magnitud del problema cede en la encuesta, pero su expresión más extrema se mantiene. Feminicidios =
      contexto (investiga el Ministerio Público, sanciona el Poder Judicial), no eficacia directa del MIMP.</div>

    <div class="grid" style="margin-top:18px"><div class="card full"><h3>3 · Denuncias por violencia sexual (contexto)</h3><p class="cap">Registro PNP/MININTER (INEI) · total y víctimas menores de edad</p><div class="chart-box"><canvas id="c_viol"></canvas></div></div></div>
    <div class="note" style="margin-top:12px"><b>La otra cara del registro:</b> las denuncias por violencia sexual <b>casi se duplicaron</b>
      (5,7k en 2016 → 10,8k en 2024), y más de la mitad son contra <b>menores de edad</b>. <b>Paradoja de registros:</b> más denuncias
      puede reflejar más violencia <i>o</i> más disposición a denunciar (mayor visibilización) — no se puede concluir una sola cosa.
      Es contexto (PNP/MP), no eficacia directa del MIMP.</div>
  </section>

  <section id="metas">
    <h2>Meta prometida vs. resultado real</h2>
    <p class="lead">El propio MIMP fijó metas en su Política Nacional de Igualdad de Género (DS 008-2019-MIMP).
      El indicador central —violencia física/sexual de pareja en los <b>últimos 12 meses</b> (mejor que el
      "alguna vez")— debía caer a <b>4,8% en 2026</b> y <b>2,4% en 2030</b>. El dato real va muy por encima.</p>
    <div class="grid">
      <div class="card full"><h3>Violencia de pareja (últimos 12 meses): meta vs. real</h3>
        <p class="cap">% mujeres 15+ · meta oficial PNIG vs. ejecución real (ENDES–PPR)</p>
        <div class="chart-box tall"><canvas id="c_metaviol"></canvas></div></div>
    </div>
    <div class="vh-card" style="margin-top:16px">
      <div class="vh-tag">El veredicto más duro · gestión que no cumple lo suyo</div>
      <div class="vh-row">
        <div class="vh-metric"><span class="vh-big" style="color:var(--crit)">7,5%</span><span class="vh-sub">Real 2024</span></div>
        <div class="vh-vs">vs.</div>
        <div class="vh-metric"><span class="vh-big" style="color:var(--good)">6,0%</span><span class="vh-sub">Meta 2024</span></div>
        <div class="vh-metric"><span class="vh-big" style="color:var(--good)">4,8%</span><span class="vh-sub">Meta 2026</span></div>
        <div class="vh-metric"><span class="vh-big" style="color:var(--accent)">+134%</span><span class="vh-sub">Presupuesto 17→25</span></div>
      </div>
      <p>Salvo 2021, el resultado quedó <b>siempre por encima</b> de la meta y la brecha se amplía. Con el
      presupuesto triplicado, <b>el MIMP no va camino a cumplir la meta que él mismo se fijó</b>.</p>
    </div>
    <div class="card full" style="margin-top:16px"><h3>Otras metas al 2030 de los planes del MIMP</h3>
      <p class="cap">Línea base → meta · Política Nacional de Igualdad de Género y PEI 2025–2030</p>
      <div class="tablewrap"><table class="norm" id="t_metas"><thead><tr><th>Instrumento</th><th>Indicador</th><th>Línea base</th><th>Meta</th><th>Real reciente</th><th>Estado</th></tr></thead><tbody></tbody></table></div></div>
  </section>

  <section id="servicios">
    <h2>Producción de servicios (CEM y Línea 100)</h2>
    <p class="lead">Atenciones de los Centros Emergencia Mujer por tipo de violencia, número de CEM y consultas
      de la Línea 100. Registro administrativo (demanda atendida), no comparable con la prevalencia ENDES.</p>
    <div class="grid">
      <div class="card full"><h3>Atenciones CEM por tipo de violencia</h3><p class="cap">Casos atendidos, apilado por tipo</p><div class="chart-box tall"><canvas id="c_cem"></canvas></div></div>
      <div class="card"><h3>N.º de Centros Emergencia Mujer</h3><p class="cap">Acumulado nacional · solo 5 operan 7×24</p><div class="chart-box"><canvas id="c_cemn"></canvas></div></div>
      <div class="card"><h3>Consultas de la Línea 100</h3><p class="cap">Por año · ver caveat de comparabilidad</p><div class="chart-box"><canvas id="c_l100"></canvas></div></div>
    </div>
    <div class="note" style="margin-top:14px"><b>Dos señales:</b> la violencia <b>sexual atendida se duplicó</b>
      (12,8k en 2018 → 32,2k en 2025), mientras el total se estabiliza en ~165k desde 2021. La red de CEM se
      estancó en <b>433</b> desde 2023 y <b>solo 5 operan 24 horas</b>. En Línea 100 el rótulo cambia entre años y
      2024–2025 son cifras de prensa: no comparar linealmente.</div>
  </section>

  <section id="ninez">
    <h2>Niñez y adolescencia</h2>
    <p class="lead">Embarazo adolescente (ENDES) y cobertura de las DEMUNA (rectoría DGNNA-MIMP).
      Contexto multisectorial (Salud, Educación, MIMP).</p>
    <div class="grid">
      <div class="card"><h3>Embarazo adolescente (15–19 años)</h3><p class="cap">% alguna vez embarazadas · ⚠ ruptura de serie</p><div class="chart-box"><canvas id="c_emb"></canvas></div></div>
      <div class="card"><h3>DEMUNA acreditadas</h3><p class="cap">% del total · registro MIMP (cobertura, no atenciones)</p><div class="chart-box"><canvas id="c_dem"></canvas></div></div>
    </div>
    <div class="note" style="margin-top:14px"><b>Vacíos de información:</b> no existe serie nacional pública de
      <b>atenciones ni conciliaciones DEMUNA</b>, ni de <b>infanticidio</b> (requieren solicitud Ley 27806).
      <b>Aborto</b>: sin estadística oficial de incidencia (ilegal salvo terapéutico). En embarazo adolescente,
      hasta 2017-18 son promedios bienales y desde 2020 años simples → la caída no es comparación interanual limpia.</div>
  </section>

  <section id="presupuesto">
    <h2>Presupuesto y ejecución</h2>
    <p class="lead">PIA (inicial), PIM (modificado) y devengado por año, con el % de ejecución y el monto no ejecutado.
      El presupuesto salta de S/ 444 M (2018) a S/ 733 M (2019).</p>
    <div class="grid">
      <div class="card full"><h3>PIA · PIM · Devengado por año</h3><p class="cap">Millones S/ corrientes</p><div class="chart-box tall"><canvas id="c_serie"></canvas></div></div>
      <div class="card"><h3>Ejecución presupuestal</h3><p class="cap">Devengado / PIM (%)</p><div class="chart-box"><canvas id="c_ejec"></canvas></div></div>
      <div class="card"><h3>Presupuesto no ejecutado</h3><p class="cap">PIM − Devengado (millones S/)</p><div class="chart-box"><canvas id="c_noejec"></canvas></div></div>
    </div>
  </section>

  <section id="planilla">
    <h2>Personal y planilla</h2>
    <p class="lead">Cuánta gente trabaja en el sector Mujer, con qué contrato y con qué sueldo (Portal de
      Transparencia), más el costo de la planilla mes a mes (MEF). Dos hallazgos: <b>casi todo el personal es CAS</b>
      (contrato temporal) y hay una <b>fuerte brecha salarial</b> entre la cúpula y quienes atienden la violencia.</p>
    <div class="grid">
      <div class="card"><h3>Trabajadores por unidad</h3><p class="cap">N.º de personas · Portal de Transparencia (snapshot 2026)</p><div class="chart-box tall"><canvas id="c_personal"></canvas></div></div>
      <div class="card"><h3>Rango salarial por unidad</h3><p class="cap">Soles/mes · de más bajo (p25) a más alto · marca = mediana</p><div class="chart-box tall"><canvas id="c_sueldos"></canvas></div></div>
      <div class="card full"><h3>Gasto de planilla mes a mes</h3><p class="cap">Devengado en personal + CAS, millones S/ · línea gruesa = último año</p><div class="chart-box tall"><canvas id="c_planilla"></canvas></div></div>
    </div>
    <div class="note" style="margin-top:14px"><b>Precariedad y brecha:</b> el <b>~99% del personal es CAS</b> (contrato
      temporal, sin estabilidad), incluido el programa que atiende la violencia (Warmi Ñan, ~5 500 personas con mediana
      S/ 4 364). En paralelo, <b>7 altos funcionarios</b> (Ley Servir) tienen mediana <b>S/ 30 000</b> —unas 7 veces más—
      y los máximos llegan a <b>S/ 57 400</b> frente a mínimos de <b>~S/ 1 764</b> (INABIF). Fuente: Portal de Transparencia
      Estándar, vía <a href="https://unimauro.github.io/peru-transparente/" target="_blank" rel="noopener" style="color:var(--accent)">Perú Transparente ↗</a>.</div>
  </section>

  <section id="gasto">
    <h2>¿En qué se gasta?</h2>
    <p class="lead">Devengado por genérica, por rubro de detalle (aquí aparece el CAS y las contrataciones de
      servicios), por unidad ejecutora, programa y fuente.</p>
    <div class="grid">
      <div class="card"><h3>En qué se gasta (detalle)</h3><p class="cap">Devengado por rubro, millones S/ (top)</p><div class="chart-box tall"><canvas id="c_detalle"></canvas></div></div>
      <div class="card"><h3>Por genérica de gasto</h3><p class="cap">Millones S/</p><div class="chart-box tall"><canvas id="c_gen"></canvas></div></div>
      <div class="card"><h3>Por unidad ejecutora</h3><p class="cap">Millones S/</p><div class="chart-box tall"><canvas id="c_ue"></canvas></div></div>
      <div class="card"><h3>Por programa presupuestal</h3><p class="cap">Millones S/ (top)</p><div class="chart-box tall"><canvas id="c_prog"></canvas></div></div>
      <div class="card"><h3>Por fuente de financiamiento</h3><p class="cap">Millones S/</p><div class="chart-box tall"><canvas id="c_ff"></canvas></div></div>
      <div class="card"><h3>Corriente vs. capital</h3><p class="cap">Millones S/</p><div class="chart-box"><canvas id="c_cat"></canvas></div></div>
    </div>
  </section>

  <section id="territorio">
    <h2>Distribución territorial del gasto</h2>
    <p class="lead">Devengado acumulado 2017–2025 por departamento (departamento de la meta). Insumo para brechas
      de cobertura frente a la incidencia (H4).</p>
    <div class="card full" style="margin-bottom:18px">
      <h3>Mapa: gasto vs. violencia por departamento</h3>
      <p class="cap">Elige la capa. El gasto se concentra en Lima; la violencia ocurre en todo el país.</p>
      <div class="mapa-tabs" id="mapaTabs">
        <button data-capa="gasto" class="active">Gasto acumulado</button>
        <button data-capa="feminicidios">Feminicidios 2025</button>
        <button data-capa="denuncias">Denuncias sexuales 2024</button>
        <button data-capa="atenciones">Atenciones CEM 2025</button>
      </div>
      <div id="mapa" style="height:520px;border-radius:12px;overflow:hidden;background:var(--ground)"></div>
      <p class="cap" style="margin-top:8px">Coropletas por departamento. <b>Nota:</b> mezcla de años (denuncias 2024; feminicidios y CEM 2025) y "Lima" combina Lima Metropolitana + Región Lima. Contexto multisectorial, no eficacia directa del MIMP.</p>
    </div>
    <div class="grid"><div class="card full"><h3>Devengado por departamento</h3><p class="cap">Acumulado, millones S/ (top 15)</p><div class="chart-box" style="height:440px"><canvas id="c_dept"></canvas></div></div></div>
  </section>


  <section id="gestion">
    <h2>Gestión y rotación de titulares</h2>
    <p class="lead">Duración de cada gestión ministerial. Barras rojas: gestiones de menos de 90 días. La rotación
      extrema erosiona la continuidad de política (H6).</p>
    <div class="grid"><div class="card full"><h3>Días en el cargo por titular</h3><p class="cap">Ministras/os del MIMP, 2016–2025</p><div class="chart-box" style="height:460px"><canvas id="c_titulares"></canvas></div></div></div>
  </section>

  <section id="normas">
    <h2>Marco normativo impulsado</h2>
    <p class="lead">Leyes y políticas clave donde el MIMP es rector o proponente. El marco existe y es sostenido;
      el contraste está entre esta continuidad normativa y la inestabilidad de gestión.</p>
    <div class="card full"><div class="tablewrap"><table class="norm" id="t_normas"><thead><tr><th>Tipo</th><th>Número</th><th>Nombre</th><th>Año</th><th>Fuente</th></tr></thead><tbody></tbody></table></div></div>
  </section>

  <section id="hipotesis">
    <h2>Contraste de hipótesis H1–H6</h2>
    <p class="lead">Verde = no se sostiene · rojo = se sostiene · ámbar = parcial · gris = datos en recolección.</p>
    <div class="hyp">
      <div class="hcard v-si"><div class="hid">H1 · Impacto</div><h4>La violencia no disminuyó pese al gasto</h4>
        <span class="verdict v-si">Se sostiene</span>
        <p>En los <b>hechos</b>, no disminuyó: <b>feminicidios estancados</b> (130–170/año), <b>denuncias por violencia
        sexual +90%</b> y el MIMP <b>no cumple su propia meta</b> (7,5% real vs 4,8%). La única señal contraria es una
        encuesta autorreportada, discutible y estancada. Triplicó el gasto y el problema no cede.</p></div>
      <div class="hcard v-si"><div class="hid">H2 · Servicios</div><h4>La producción de servicios está estancada</h4>
        <span class="verdict v-si">Se sostiene</span>
        <p>La <b>red de CEM está congelada en 433</b> desde 2023 y <b>solo 5 operan 24h</b> en todo el país; las
        atenciones llevan <b>estancadas ~165k</b> desde 2021. La cobertura no crece al ritmo de la demanda: el sistema
        toca techo mientras el presupuesto sube.</p></div>
      <div class="hcard v-parc"><div class="hid">H3 · Presupuesto</div><h4>El presupuesto es bajo y/o se subejecuta</h4>
        <span class="verdict v-parc">El dinero no es la excusa</span>
        <p>NO subejecuta: ejecuta <b>96–99%</b> y el PIA creció <b>+134%</b>. El problema <b>no es la plata</b> —se
        gasta casi toda— sino que ese gasto no se traduce en resultados. "Bajo" solo cabe como peso del presupuesto
        nacional (~0,4%).</p></div>
      <div class="hcard v-si"><div class="hid">H4 · Cobertura</div><h4>Brechas de cobertura territorial vs. incidencia</h4>
        <span class="verdict v-si">Se sostiene</span>
        <p><b>Lima concentra S/ 4 155 M</b> del gasto acumulado; ningún otro departamento pasa de ~S/ 200 M. Una
        <b>centralización extrema</b> frente a una violencia que ocurre en todo el país (ver el mapa territorial).</p></div>
      <div class="hcard v-si"><div class="hid">H5 · Calidad</div><h4>Problemas de calidad/idoneidad en la atención</h4>
        <span class="verdict v-si">Se sostiene</span>
        <p><b>99% del personal es CAS</b> (temporal, alta rotación), incluido quien atiende la violencia; con
        <b>brecha salarial de 7×</b> frente a la cúpula (S/ 4 364 vs S/ 30 000). Planta precaria y ministros que
        cambian cada pocos meses: la atención de calidad sostenida es estructuralmente inviable.</p></div>
      <div class="hcard v-si"><div class="hid">H6 · Gestión</div><h4>Predomina la gestión de imagen sobre resultados</h4>
        <span class="verdict v-si">Se sostiene</span>
        <p>Marco normativo abundante (Ley 30364, PNIG, Estrategia) y ejecución del 99%, pero <b>~15 titulares en 9 años</b>,
        metas incumplidas y hechos que no mejoran. <b>Mucha norma y gasto, poco resultado</b>: la forma por delante del fondo.</p></div>
    </div>
  </section>

  <section id="contraste">
    <h2>Cómo se evalúa el ministerio vs. lo que muestran los hechos</h2>
    <p class="lead">El MIMP y su sector destacan la caída de una <b>encuesta de autorreporte</b> (ENDES). Pero las cifras de
      <b>hechos registrados</b> —lo que su propia Ley 30364 define como violencia contra la mujer: física, psicológica,
      sexual y económica— no acompañan. La foto favorable la da la encuesta; los registros cuentan otra historia.</p>
    <div class="vs-grid">
      <div class="vs-col vs-soft">
        <div class="vs-tag">Cómo se autoevalúa · encuesta</div>
        <h3>La foto favorable (ENDES)</h3>
        <ul>
          <li>Prevalencia "alguna vez": <b>65% → 52%</b> (−13 pp)</li>
          <li>Es <b>autorreporte</b> en una encuesta, no hechos registrados</li>
          <li><b>Ruptura metodológica</b> en 2020; estancada desde entonces (~52–55%)</li>
          <li>La <b>meta oficial</b> se define sobre este mismo tipo de encuesta</li>
        </ul>
      </div>
      <div class="vs-col vs-hard">
        <div class="vs-tag">Los hechos · registros</div>
        <h3>La foto real (registros)</h3>
        <ul>
          <li><b>Feminicidios</b>: 130–170 al año, <b>sin descenso</b></li>
          <li><b>Denuncias por violencia sexual</b>: <b>+90%</b> (5,7k → 10,8k)</li>
          <li><b>Atenciones CEM</b>: estables ~165k; la sexual atendida <b>se duplicó</b></li>
          <li>Meta de violencia reciente (12 meses): real <b>7,5%</b> (2024) vs. meta <b>6,0%</b> — <b>no cumple</b></li>
        </ul>
      </div>
    </div>
    <div class="note" style="margin-top:16px;border-left-color:var(--crit)">
      <b>La interpretación:</b> el único indicador que "mejora" es una encuesta autorreportada, débil y estancada. La
      ENDES la produce el <b>INEI</b> (encuesta independiente, estándar internacional): el problema no es el número, sino
      que <b>el sector destaque el indicador que le favorece</b> y no los hechos. En los hechos que sus
      leyes definen como violencia de género, <b>no hay evidencia de mejora</b> pese a triplicar el presupuesto. Con las
      salvaguardas del caso (la violencia es multisectorial y no se puede atribuir causalidad a un solo actor), lo honesto
      es decir que <b>no está demostrado que el MIMP haya reducido la violencia de género</b>: ni cumple sus propias metas
      de hechos, ni los registros retroceden.
    </div>
  </section>

  <section id="conclusion">
    <h2>Conclusión y recomendaciones</h2>
    <p class="lead">Qué dice la evidencia reunida y qué debería cambiar. Una evaluación no acusa: diagnostica y propone.</p>
    <div class="verdict-card" style="max-width:none;border-left-color:var(--crit)">
      <div class="vc-body" style="max-width:80ch">
        <p><b>Diagnóstico.</b> Entre 2017 y 2025 el MIMP casi triplicó su presupuesto y lo ejecuta al 99%, pero
          <b>no hay evidencia consistente</b> de que la violencia de género esté cediendo en los hechos: feminicidios
          estancados, denuncias sexuales al alza y una <b>meta propia incumplida</b>. La gestión es diligente en el gasto,
          no en resultados: planta precaria (99% CAS), cobertura centralizada en Lima y conducción inestable (~15 titulares
          en 9 años).</p>
        <p><b>Matiz honesto.</b> La violencia es multisectorial: no puede atribuirse causalmente el resultado a un solo
          actor, y sin el MIMP el panorama podría ser peor. Pero la carga de probar que su acción funciona recae en el
          ministerio —y hoy sus propios indicadores no la sostienen.</p>
      </div>
    </div>
    <h3 style="margin:24px 0 0">Seis recomendaciones</h3>
    <ol class="recos">
      <li><b>Medir por hechos, no por encuesta.</b> Anclar las metas de gestión a feminicidios, denuncias y atenciones —indicadores verificables— y no principalmente a la prevalencia autorreportada de la ENDES.</li>
      <li><b>Cerrar la brecha de cobertura 24h.</b> Solo 5 de 433 CEM operan las 24 horas; ampliarlos y garantizar atención permanente donde ocurre la violencia.</li>
      <li><b>Descentralizar el gasto.</b> Corregir la concentración en Lima y asignar presupuesto según la incidencia territorial (ver el mapa).</li>
      <li><b>Estabilizar y profesionalizar la planta.</b> Reducir la dependencia del régimen CAS (99% hoy) y la rotación de titulares, que erosionan la continuidad y la calidad.</li>
      <li><b>Transparencia comparable.</b> Publicar personal, cobertura y ejecución por región en datos abiertos, con definiciones y fechas de corte, para permitir la evaluación externa.</li>
      <li><b>Evaluación de impacto real.</b> Encargar evaluaciones con contrafactual de sus programas, no solo reportes de producción de servicios.</li>
    </ol>
  </section>

  <section id="faq" class="faq">
    <h2>Preguntas frecuentes (metodología crítica)</h2>
    <p class="lead">Por qué algunos datos deben leerse con cuidado — y por qué la "caída" de la violencia no es lo que parece.</p>

    <details open><summary>Entonces, ¿el MIMP realmente reduce la violencia de género?</summary>
      <div class="fa-body"><b>No está demostrado.</b> El presupuesto se triplicó, pero los indicadores de <b>hechos</b>
      —feminicidios (estancados), denuncias por violencia sexual (+90%), atenciones CEM (sin bajar)— no mejoran. La única
      "mejora" es una encuesta de autorreporte (ENDES) que además es metodológicamente débil y se estancó desde 2020. Y en
      la <b>meta de hechos que el propio MIMP se fijó</b> (violencia de pareja en 12 meses: 4,8% al 2026), el resultado real
      va por encima (7,5% en 2024). Con las salvaguardas del caso (es un problema multisectorial), lo honesto es que <b>no
      hay evidencia de que su acción esté reduciendo la violencia de género</b>.</div></details>

    <details><summary>¿El ministerio se evalúa con el dato más cómodo?</summary>
      <div class="fa-body">Es una lectura razonable. El sector destaca la caída de la prevalencia ENDES —una encuesta de
      autorreporte que da la foto más favorable— mientras los <b>registros de hechos</b> (los que sus propias leyes definen
      como violencia: física, psicológica, sexual, económica) no acompañan. La ENDES la produce el INEI de forma
      independiente; la crítica no es a la encuesta sino a que <b>el sector se apoye en el indicador que le favorece</b> en
      vez de en los hechos y en el cumplimiento de sus propias metas.</div></details>

    <details><summary>¿Por qué no confiar en que la violencia "cayó 13 puntos"?</summary>
      <div class="fa-body">Ese número viene de <b>un solo indicador</b>: la prevalencia total de la encuesta INEI–ENDES
      (65,4% en 2017 → 52,0% en 2024). Tiene tres problemas: (1) es <b>autorreporte</b> en una encuesta, no hechos
      registrados; (2) mide violencia sufrida <b>"alguna vez" en la vida</b>, muy sensible a la composición de la muestra;
      y (3) en <b>2020 el INEI cambió la metodología</b> (de promedios bienales a años simples), creando una ruptura de
      serie. Además, casi todo el descenso ocurrió en 2017–2019 y desde 2020 <b>se estancó</b> (~52–55%). Por eso es un
      indicador <b>metodológicamente discutible</b>: sirve como contexto, no como prueba de que la violencia bajó —y menos
      de que bajó por acción del MIMP.</div></details>

    <details><summary>¿Qué mide exactamente "violencia de pareja" en la ENDES?</summary>
      <div class="fa-body">El % de mujeres de <b>15 a 49 años alguna vez unidas</b> que declaran haber sufrido violencia
      psicológica/verbal, física o sexual ejercida <b>alguna vez por su esposo o compañero</b>. No incluye a mujeres no
      unidas, no cubre otras formas de violencia de género (acoso, trata, violencia institucional) y depende de que la
      mujer <b>reconozca y reporte</b> la violencia en la entrevista. Base: Cuadro 11.1, Series Anuales INEI 1986–2024.</div></details>

    <details><summary>Entonces, ¿qué datos son mejores para evaluar el problema?</summary>
      <div class="fa-body">Los <b>registros de hechos</b>, que no dependen de autorreporte y no muestran mejora:
      <b>feminicidios</b> estancados en 130–170/año (registro Warmi Ñan), <b>denuncias por violencia sexual</b> que
      casi se duplicaron (5,7k→10,8k, INEI/PNP) y <b>atenciones CEM</b> estables en ~165k. Cada uno tiene su límite
      (subregistro, cambios de definición), pero en conjunto pintan un panorama <b>más crudo</b> que la encuesta.</div></details>

    <details><summary>¿Se pueden sumar feminicidios + denuncias + atenciones en un solo número?</summary>
      <div class="fa-body"><b>No.</b> Son unidades distintas: los feminicidios son <b>muertes</b>, las denuncias son
      <b>denuncias</b> y las atenciones son <b>casos atendidos</b> (una misma persona puede tener varias). Sumarlos
      produciría una cifra sin sentido. Por eso se muestran <b>juntos como panel de señales</b>, no como un total.</div></details>

    <details><summary>Más denuncias, ¿es más violencia o más gente denunciando?</summary>
      <div class="fa-body">No se puede concluir una sola cosa: es la <b>paradoja de los registros</b>. Un alza de denuncias
      puede reflejar <b>más violencia</b>, <b>más disposición a denunciar</b> (mayor confianza/visibilización), o
      <b>más oferta de servicios</b> que capta casos antes invisibles. Por eso las denuncias y atenciones se presentan
      como <b>demanda registrada</b>, no como medida directa de la magnitud del problema.</div></details>

    <details><summary>¿Por qué feminicidios y violaciones son "contexto" y no responsabilidad del MIMP?</summary>
      <div class="fa-body">Porque son <b>multisectoriales</b>: la investigación la conduce el <b>Ministerio Público</b>, la
      sanción el <b>Poder Judicial</b>, y las denuncias las registra la <b>PNP/Mininter</b>. El MIMP previene, atiende y
      articula, pero no controla el resultado penal. Se leen como <b>contribución, no atribución</b>: sirven de contexto,
      no como nota directa de la eficacia del ministerio.</div></details>

    <details><summary>¿No es injusto medir con conteos absolutos en vez de tasas?</summary>
      <div class="fa-body">Es una crítica válida y la reconocemos. Los conteos (feminicidios, denuncias) no ajustan por
      crecimiento poblacional ni por el hecho de que la <b>Ley 30364 (2015)</b> y nuevos tipos penales <b>elevan las denuncias
      mecánicamente</b>. Por eso el argumento no descansa en "subieron X%", sino en que <b>ni siquiera con más registro</b> los
      feminicidios (el indicador menos sensible al subregistro) descienden, y en que el MIMP <b>no cumple su propia meta</b> —que
      sí está definida como tasa. La normalización por 100 000 es una mejora pendiente y declarada.</div></details>

    <details><summary>¿Cuánto de esto es efecto de la pandemia (2020)?</summary>
      <div class="fa-body">Parte. 2020 rompió a la vez la serie ENDES, la prestación de servicios (CEM con aforo reducido)
      y las denuncias (subregistro y luego rebote). Por eso <b>no atribuimos el estancamiento solo a la gestión</b>: es un factor
      de confusión real. Aun así, el estancamiento persiste en 2022–2024, ya sin restricciones, y la meta se incumple en el
      último dato disponible.</div></details>

    <details><summary>¿No aplican doble vara: escépticos con lo bueno, crédulos con lo malo?</summary>
      <div class="fa-body">Es el riesgo que más cuidamos. Los indicadores "malos" también tienen caveats: las <b>denuncias</b>
      pueden subir por mayor visibilización (no solo más violencia); los <b>feminicidios</b> del registro del programa pueden diferir
      de los del Ministerio Público; y todos son <b>contexto multisectorial</b>, no eficacia directa del MIMP. El punto no es que un
      indicador baje o suba, sino que <b>ninguno de los verificables mejora</b> y que el ministerio <b>incumple su propia meta</b>.</div></details>

    <details><summary>¿Qué haría cambiar este veredicto? (falsabilidad)</summary>
      <div class="fa-body">Lo cambiaría: que los <b>feminicidios</b> muestren una tendencia descendente sostenida; que el MIMP
      <b>alcance la trayectoria de su meta</b> PNIG de violencia de pareja; que la cobertura 24h y la descentralización del gasto
      mejoren de forma verificable; o una <b>evaluación de impacto con contrafactual</b> que atribuya reducción a sus programas.
      Nada de eso está hoy en los datos públicos.</div></details>

    <details><summary>¿Quién hizo esto y con qué método?</summary>
      <div class="fa-body">Evaluación independiente a partir de <b>datos abiertos oficiales</b>: MEF (presupuesto), INEI–ENDES
      (prevalencia), Portal Warmi Ñan/MIMP (servicios y feminicidios), INEI/PNP (denuncias), Portal de Transparencia (personal),
      El Peruano (normas). Toda cifra lleva fuente + URL + fecha de descarga (2026-09-08), y el pipeline es reproducible desde el
      repositorio público <code>evaluacion-mimp</code>. No representa a ninguna entidad ni al propio MIMP.</div></details>

    <details><summary>¿El presupuesto del MIMP es alto o bajo?</summary>
      <div class="fa-body">En términos absolutos <b>creció mucho</b> (PIA S/ 426 M en 2017 → S/ 996 M en 2025, +134%) y se
      <b>ejecuta casi al 100%</b>. Pero como parte del presupuesto nacional pesa apenas <b>~0,4%</b>. Ambas cosas son
      ciertas: el MIMP no subejecuta, pero su escala frente al problema es pequeña.</div></details>
  </section>

  <footer>
    Repositorio <b>evaluacion-mimp</b> · desplegado en GitHub Pages. Toda cifra es trazable a su fuente oficial con
    fecha de descarga 2026-09-08. Ninguna cifra sin fuente + URL + fecha. Analítica: Google Analytics.
  </footer>
</main></div>

<button class="chat-fab" id="chatFab" aria-label="Abrir asistente de datos">
  <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-8.5 8.4 8.7 8.7 0 0 1-4-.9L3 20l1.1-4.9a8.4 8.4 0 0 1-1-4 8.4 8.4 0 0 1 8.5-8.4 8.4 8.4 0 0 1 8.4 8.3z"/></svg>
</button>
<div class="chat-panel" id="chatPanel" role="dialog" aria-modal="true" aria-label="Asistente de la evaluación" hidden>
  <div class="chat-top"><span class="chat-dot"></span>
    <div><b>Asistente de la evaluación</b><span>IA · pregunta por las cifras</span></div>
    <button class="chat-x" id="chatClose" aria-label="Cerrar">✕</button></div>
  <div class="chat-log" id="chatLog"></div>
  <form class="chat-form" id="chatForm">
    <input id="chatInput" type="text" autocomplete="off" placeholder="Ej.: ¿Cuánto ejecutó el MIMP en 2024?" maxlength="500">
    <button type="submit" aria-label="Enviar"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg></button>
  </form>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
const P = /*__DATA__*/;
const D = P.presupuesto, EN = P.endes, TIT = P.titulares, NOR = P.normas;
const css = v => getComputedStyle(document.body).getPropertyValue(v).trim();
const SER=['--s1','--s2','--s3','--s4','--s5','--s6','--s7','--s8'], sc=i=>css(SER[i%8]);
// Plugin: etiquetas de valor sobre los puntos (para líneas de una serie)
const valueLabels={id:'valueLabels',afterDatasetsDraw(chart,a,opts){
  if(!opts||!opts.on)return;const{ctx}=chart;ctx.save();
  ctx.font='700 11px "Helvetica Neue",Arial';ctx.textAlign='center';ctx.fillStyle=opts.color||css('--ink');
  chart.data.datasets.forEach((ds,di)=>{const meta=chart.getDatasetMeta(di);if(meta.hidden)return;
    meta.data.forEach((pt,i)=>{const v=ds.data[i];if(v==null)return;ctx.fillText(opts.fmt?opts.fmt(v):v,pt.x,pt.y-9);});});
  ctx.restore();}};
if(window.Chart)Chart.register(valueLabels);
const M=x=>x/1e6, fmtM=x=>'S/ '+(Math.round(x/1e5)/10).toLocaleString('es-PE')+' M';
const anios=D.meta.periodo;
let charts=[];
function base(extra){const ink=css('--ink'),ink2=css('--ink-2'),line=css('--line');
  return Object.assign({responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},
    plugins:{legend:{labels:{color:ink2,boxWidth:12,boxHeight:12,usePointStyle:true,font:{family:'Helvetica Neue',size:11}}},
      tooltip:{backgroundColor:css('--panel'),titleColor:ink,bodyColor:ink2,borderColor:line,borderWidth:1,padding:10,usePointStyle:true,
        callbacks:{label:c=>` ${c.dataset.label}: ${fmtM((c.parsed.y!=null?c.parsed.y:c.parsed.x)*1e6)}`}}},
    scales:{x:{grid:{display:false},ticks:{color:ink2,font:{size:12}}},
      y:{grid:{color:line},ticks:{color:ink2,font:{size:12},callback:v=>v.toLocaleString('es-PE')},title:{display:true,text:'Millones S/',color:css('--muted'),font:{size:11}}}}},extra||{});
}
function stacked(cv,obj){const ds=obj.labels.map((lab,i)=>({label:lab,data:anios.map(a=>M((obj.por_anio[a]||{})[lab]||0)),
  backgroundColor:sc(i),borderRadius:2,borderWidth:1,borderColor:css('--panel')}));
  const o=base({scales:{x:{stacked:true,grid:{display:false},ticks:{color:css('--ink-2')}},
    y:{stacked:true,grid:{color:css('--line')},ticks:{color:css('--ink-2'),callback:v=>v.toLocaleString('es-PE')},title:{display:true,text:'Millones S/',color:css('--muted'),font:{size:11}}}}});
  o.plugins.legend.labels.font.size=10;
  return new Chart(cv,{type:'bar',data:{labels:anios,datasets:ds},options:o});}
function diasEntre(a,b){if(!a)return null;const d1=new Date(a);if(isNaN(d1))return null;
  let d2=b?new Date(b):null;if(!d2||isNaN(d2))d2=new Date('2025-08-31');  // fin vacío o placeholder = en ejercicio
  return Math.max(1,Math.round((d2-d1)/86400000));}

function build(){
  charts.forEach(c=>c.destroy());charts=[];
  const S=D.serie_anual,pN=S[S.length-1],p0=S[0];
  const crec=(pN.pia/p0.pia-1)*100,ejecProm=S.reduce((a,b)=>a+b.ejecucion_pct,0)/S.length;
  const enTot=EN.series&&(EN.series['total']||EN.series['Total']);
  const enOk=enTot&&enTot[0]!=null&&enTot[enTot.length-1]!=null;
  const cae = enOk? (enTot[0]-enTot[enTot.length-1]).toFixed(1):null;
  const nTit=TIT.filter(t=>!/DISPONIBLE|^\[/i.test(t.nombre)).length;
  document.getElementById('kpis').innerHTML=[
    ['PIA '+pN.anio,fmtM(pN.pia),'inicial de apertura'],
    ['Ejecución '+pN.anio,pN.ejecucion_pct.toFixed(1)+'%','<span class="k-up">no subejecuta</span>'],
    ['Crecim. PIA '+p0.anio.slice(2)+'→'+pN.anio.slice(2),'<span class="k-up">+'+crec.toFixed(0)+'%</span>','nominal'],
    enOk?['Prevalencia ENDES','<span class="k-dn">−'+cae+' pp</span>',enTot[0]+'% → '+enTot[enTot.length-1]+'%']:['Prevalencia ENDES','—','en proceso'],
    ['Titulares 2016–25','<span class="k-dn">'+nTit+'</span>','rotación alta'],
  ].map(k=>`<div class="kpi"><div class="k-label">${k[0]}</div><div class="k-val">${k[1]}</div><div class="k-note">${k[2]}</div></div>`).join('');

  // Tarjetas de evolución "antes → ahora" (datos reales)
  const nf=x=>x.toLocaleString('es-PE');
  const cards=[];
  const card=(kl,lbl,now,chg,from)=>cards.push(`<div class="evol ${kl}"><div class="e-lbl">${lbl}</div><div class="e-now">${now}</div><div class="e-chg">${chg}</div><div class="e-from">${from}</div></div>`);
  const EMBc=P.embarazo;
  if(EMBc&&EMBc.total.length){const v0=EMBc.total[0],vN=EMBc.total[EMBc.total.length-1];
    card('up','Embarazo adolescente (15–19)',vN+'%','▼ '+(v0-vN).toFixed(1)+' pp*',EMBc.periodos[0]+': '+v0+'%');}
  const FE2=P.feminicidios;
  if(FE2&&FE2.feminicidios.length){const v0=FE2.feminicidios[0],vN=FE2.feminicidios[FE2.feminicidios.length-1];
    card('flat','Feminicidios (contexto)',nf(vN),'≈ sin descenso',FE2.anios[0]+': '+nf(v0));}
  const CE2=P.cem;
  if(CE2&&CE2.total.length){const v0=CE2.total[0],vN=CE2.total[CE2.total.length-1];
    card('info','Atenciones CEM / año',nf(vN),'▲ +'+((vN/v0-1)*100).toFixed(0)+'%',CE2.anios[0]+': '+nf(v0));}
  card('info','Presupuesto PIA',fmtM(pN.pia),'▲ +'+crec.toFixed(0)+'%',p0.anio+': '+fmtM(p0.pia));
  const VI2=P.violaciones;
  if(VI2&&VI2.total.length){const v0=VI2.total[0],vN=VI2.total[VI2.total.length-1];
    card('down','Denuncias violencia sexual',nf(vN),'▲ +'+((vN/v0-1)*100).toFixed(0)+'%',VI2.anios[0]+': '+nf(v0));}
  document.getElementById('evol').innerHTML=cards.join('');

  // Story: gasto (barras) vs feminicidios registrados (línea) — dos escalas
  const FEs=P.feminicidios;
  if(FEs&&FEs.anios&&FEs.anios.length){
    const o=base();o.plugins.legend.display=true;o.interaction.mode='index';
    o.scales.y.title.text='Devengado (M S/)';
    o.scales.y1={position:'right',grid:{drawOnChartArea:false},ticks:{color:css('--accent-2')},
      title:{display:true,text:'Feminicidios (casos)',color:css('--accent-2'),font:{size:11}},beginAtZero:true,suggestedMax:200};
    o.plugins.tooltip.callbacks.label=c=>c.dataset.yAxisID==='y1'?` ${c.dataset.label}: ${c.parsed.y} casos`:` ${c.dataset.label}: ${fmtM(c.parsed.y*1e6)}`;
    charts.push(new Chart(c_story,{data:{labels:anios,datasets:[
      {type:'bar',label:'Devengado',data:S.map(r=>M(r.devengado)),backgroundColor:sc(0),borderRadius:3,order:2},
      {type:'line',label:'Feminicidios',yAxisID:'y1',data:anios.map(a=>{const i=FEs.anios.indexOf(a);return i>=0?FEs.feminicidios[i]:null;}),
        borderColor:css('--accent-2'),backgroundColor:'transparent',borderWidth:2.6,pointRadius:3,tension:.2,spanGaps:true,order:1}]},options:o}));
  }

  charts.push(new Chart(c_serie,{type:'bar',data:{labels:anios,datasets:[
    {label:'PIA',data:S.map(r=>M(r.pia)),backgroundColor:sc(0),borderRadius:3},
    {label:'PIM',data:S.map(r=>M(r.pim)),backgroundColor:sc(1),borderRadius:3},
    {label:'Devengado',data:S.map(r=>M(r.devengado)),backgroundColor:sc(2),borderRadius:3}]},options:base()}));
  charts.push(new Chart(c_ejec,{type:'line',data:{labels:anios,datasets:[{label:'Ejecución %',data:S.map(r=>r.ejecucion_pct),borderColor:sc(2),borderWidth:2,pointRadius:4,pointBackgroundColor:sc(2),tension:.25}]},
    options:(()=>{const o=base();o.plugins.legend.display=false;o.plugins.tooltip.callbacks.label=c=>` Ejecución: ${c.parsed.y.toFixed(1)}%`;o.scales.y.title.text='%';o.scales.y.suggestedMin=90;o.scales.y.suggestedMax=100;o.scales.y.ticks.callback=v=>v+'%';return o;})()}));
  charts.push(new Chart(c_noejec,{type:'bar',data:{labels:anios,datasets:[{label:'No ejecutado',data:S.map(r=>M(r.no_ejecutado)),backgroundColor:sc(7),borderRadius:3}]},
    options:(()=>{const o=base();o.plugins.legend.display=false;return o;})()}));

  // Planilla mensual
  charts.push(new Chart(c_planilla,{type:'line',data:{labels:D.meses,datasets:anios.map((a,i)=>({label:a,data:(D.planilla_mensual[a]||[]).map(M),
    borderColor:sc(i),borderWidth:a===anios[anios.length-1]?2.6:1.2,pointRadius:0,tension:.3}))},
    options:(()=>{const o=base();o.plugins.legend.labels.font.size=10;o.interaction.mode='nearest';o.scales.y.title.text='Millones S/ / mes';return o;})()}));

  // Personal (Portal de Transparencia)
  const PR=P.personal;
  if(PR&&PR.unidades&&PR.unidades.length){
    const nombresU=PR.unidades.map(u=>u.unidad.replace(/\s*\(.*\)/,'').replace('Programa ','').trim());
    const oP=base({indexAxis:'y'});oP.plugins.legend.display=false;
    oP.scales.x={grid:{color:css('--line')},ticks:{color:css('--ink-2')},title:{display:true,text:'N.º de trabajadores',color:css('--muted'),font:{size:11}}};
    oP.scales.y={grid:{display:false},ticks:{color:css('--ink-2'),font:{size:11}}};
    oP.plugins.tooltip.callbacks.label=c=>` ${c.parsed.x.toLocaleString('es-PE')} trabajadores`;
    charts.push(new Chart(c_personal,{type:'bar',data:{labels:nombresU,datasets:[{data:PR.unidades.map(u=>u.n),backgroundColor:sc(0),borderRadius:3}]},options:oP}));
    const oS=base({indexAxis:'y'});oS.plugins.legend.display=false;
    oS.scales.x={grid:{color:css('--line')},ticks:{color:css('--ink-2'),callback:v=>'S/ '+(v/1000)+'k'},title:{display:true,text:'Sueldo mín → máx (S/)',color:css('--muted'),font:{size:11}},beginAtZero:true};
    oS.scales.y={grid:{display:false},ticks:{color:css('--ink-2'),font:{size:11}}};
    oS.plugins.tooltip.callbacks.label=c=>{const u=PR.unidades[c.dataIndex];return ` mín S/ ${u.min.toLocaleString('es-PE')} · mediana S/ ${u.mediana.toLocaleString('es-PE')} · máx S/ ${u.max.toLocaleString('es-PE')}`;};
    charts.push(new Chart(c_sueldos,{data:{labels:nombresU,datasets:[
      {type:'bar',label:'Rango (p25–máx)',data:PR.unidades.map(u=>[u.min,u.max]),backgroundColor:'rgba(120,80,220,.30)',borderColor:sc(0),borderWidth:1,borderRadius:3,borderSkipped:false},
      {type:'scatter',label:'Mediana',data:PR.unidades.map((u,i)=>({x:u.mediana,y:i})),backgroundColor:sc(4),pointRadius:5,pointStyle:'rectRot'}]},options:oS}));
  }
  charts.push(stacked(c_detalle,D.por_detalle_gasto));
  charts.push(stacked(c_gen,D.por_generica));
  charts.push(stacked(c_ue,D.por_ue));
  charts.push(stacked(c_prog,D.por_programa));
  charts.push(stacked(c_ff,D.por_fuente));
  charts.push(stacked(c_cat,D.por_categoria));

  const dep=D.por_departamento,acc=dep.labels.map(l=>anios.reduce((s,a)=>s+((dep.por_anio[a]||{})[l]||0),0));
  charts.push(new Chart(c_dept,{type:'bar',data:{labels:dep.labels,datasets:[{label:'Devengado 2017–2025',data:acc.map(M),backgroundColor:sc(0),borderRadius:3}]},
    options:(()=>{const o=base({indexAxis:'y'});o.plugins.legend.display=false;
      o.scales.x={grid:{color:css('--line')},ticks:{color:css('--ink-2'),callback:v=>v.toLocaleString('es-PE')},title:{display:true,text:'Millones S/',color:css('--muted'),font:{size:11}}};
      o.scales.y={grid:{display:false},ticks:{color:css('--ink-2'),font:{size:11}}};o.plugins.tooltip.callbacks.label=c=>` ${fmtM(c.parsed.x*1e6)}`;return o;})()}));

  // ENDES por tipo
  if(EN.anios&&EN.anios.length){
    const nombres={total:'Total',psicologica:'Psicológica','psicológica':'Psicológica',fisica:'Física','física':'Física',sexual:'Sexual'};
    const ds=Object.keys(EN.series).map((t,i)=>({label:nombres[t]||t,data:EN.series[t],borderColor:sc(i),backgroundColor:'transparent',
      borderWidth:t==='total'?2.6:1.8,pointRadius:3,tension:.25,spanGaps:true}));
    const o=base();o.scales.y.title.text='% de mujeres';o.scales.y.suggestedMin=0;o.scales.y.ticks.callback=v=>v+'%';
    o.plugins.tooltip.callbacks.label=c=>` ${c.dataset.label}: ${c.parsed.y}%`;
    charts.push(new Chart(c_endes,{type:'line',data:{labels:EN.anios,datasets:ds},options:o}));
  }

  // Feminicidios y tentativas (contexto)
  const FE=P.feminicidios;
  if(FE&&FE.anios&&FE.anios.length){
    const o=base();o.scales.y.title.text='Casos';o.scales.y.ticks.callback=v=>v;o.scales.y.beginAtZero=true;
    o.plugins.tooltip.callbacks.label=c=>` ${c.dataset.label}: ${c.parsed.y} casos`;
    charts.push(new Chart(c_femi,{data:{labels:FE.anios,datasets:[
      {type:'bar',label:'Feminicidios',data:FE.feminicidios,backgroundColor:sc(7),borderRadius:3,order:2},
      {type:'line',label:'Tentativas',data:FE.tentativas,borderColor:sc(4),backgroundColor:'transparent',borderWidth:2.4,pointRadius:3,tension:.25,order:1}]},options:o}));
  }
  // Denuncias por violencia sexual (contexto)
  const VI=P.violaciones;
  if(VI&&VI.anios&&VI.anios.length){
    const o=base();o.scales.y.title.text='Denuncias';o.scales.y.ticks.callback=v=>v.toLocaleString('es-PE');o.scales.y.beginAtZero=true;
    o.plugins.tooltip.callbacks.label=c=>` ${c.dataset.label}: ${c.parsed.y.toLocaleString('es-PE')}`;
    charts.push(new Chart(c_viol,{type:'line',data:{labels:VI.anios,datasets:[
      {label:'Total denuncias',data:VI.total,borderColor:sc(7),backgroundColor:'transparent',borderWidth:2.6,pointRadius:3,tension:.2},
      {label:'Víctimas menores',data:VI.menores,borderColor:sc(4),backgroundColor:'transparent',borderWidth:2,pointRadius:3,tension:.2,spanGaps:true}]},options:o}));
  }

  // Producción de servicios (H2)
  const CE=P.cem;
  if(CE&&CE.anios&&CE.anios.length){
    const tipos=[['psicologica','Psicológica'],['fisica','Física'],['sexual','Sexual'],['economica','Económica']];
    const o=base({scales:{x:{stacked:true,grid:{display:false},ticks:{color:css('--ink-2')}},
      y:{stacked:true,grid:{color:css('--line')},ticks:{color:css('--ink-2'),callback:v=>v.toLocaleString('es-PE')},title:{display:true,text:'Atenciones',color:css('--muted'),font:{size:11}}}}});
    o.plugins.tooltip.callbacks.label=c=>` ${c.dataset.label}: ${c.parsed.y.toLocaleString('es-PE')}`;
    charts.push(new Chart(c_cem,{type:'bar',data:{labels:CE.anios,datasets:tipos.map(([k,lb],i)=>({
      label:lb,data:CE[k],backgroundColor:sc(i),borderRadius:2,borderWidth:1,borderColor:css('--panel')}))},options:o}));
  }
  const CN=P.cem_num;
  if(CN&&CN.anios&&CN.anios.length){
    const o=base();o.plugins.legend.display=false;o.scales.y.title.text='N.º de CEM';o.scales.y.ticks.callback=v=>v;o.scales.y.beginAtZero=true;o.scales.y.suggestedMax=500;
    o.plugins.tooltip.callbacks.label=c=>` ${c.parsed.y} CEM`;o.plugins.valueLabels={on:true,color:sc(0),fmt:v=>v};o.layout={padding:{top:20}};
    charts.push(new Chart(c_cemn,{type:'line',data:{labels:CN.anios,datasets:[{label:'CEM',data:CN.total,borderColor:sc(0),backgroundColor:'rgba(120,80,220,.14)',fill:true,borderWidth:2.6,pointRadius:3,pointBackgroundColor:sc(0),tension:.2}]},options:o}));
  }
  const L1=P.linea100;
  if(L1&&L1.anios&&L1.anios.length){
    const o=base();o.plugins.legend.display=false;o.scales.y.title.text='Consultas';o.scales.y.ticks.callback=v=>v.toLocaleString('es-PE');o.scales.y.beginAtZero=true;
    o.plugins.tooltip.callbacks.label=c=>` ${c.parsed.y.toLocaleString('es-PE')} consultas`;
    charts.push(new Chart(c_l100,{type:'bar',data:{labels:L1.anios,datasets:[{label:'Línea 100',data:L1.consultas,backgroundColor:sc(5),borderRadius:3}]},options:o}));
  }
  // Niñez
  const EMB=P.embarazo;
  if(EMB&&EMB.periodos&&EMB.periodos.length){
    const o=base();o.plugins.legend.display=false;o.scales.y.title.text='% adolescentes';o.scales.y.ticks.callback=v=>v+'%';o.scales.y.beginAtZero=true;o.scales.y.suggestedMax=15;
    o.plugins.tooltip.callbacks.label=c=>` ${c.parsed.y}%`;o.plugins.valueLabels={on:true,color:sc(1),fmt:v=>v+'%'};o.layout={padding:{top:20}};
    charts.push(new Chart(c_emb,{type:'line',data:{labels:EMB.periodos,datasets:[{label:'Embarazo adolescente',data:EMB.total,borderColor:sc(1),backgroundColor:'rgba(235,104,52,.14)',fill:true,borderWidth:2.6,pointRadius:4,pointBackgroundColor:sc(1),tension:.25,spanGaps:true,segment:{borderDash:c=>c.p0DataIndex===1?[5,4]:undefined}}]},options:o}));
  }
  const DM=P.demuna;
  if(DM&&DM.anios&&DM.anios.length){
    const o=base();o.plugins.legend.display=false;o.scales.y.title.text='% acreditadas';o.scales.y.ticks.callback=v=>v+'%';o.scales.y.beginAtZero=true;
    o.plugins.tooltip.callbacks.label=c=>` ${c.parsed.y}% acreditadas`;
    charts.push(new Chart(c_dem,{type:'bar',data:{labels:DM.anios,datasets:[{label:'DEMUNA acreditadas',data:DM.acreditadas_pct,backgroundColor:sc(2),borderRadius:3}]},options:o}));
  }

  // Titulares: días en el cargo
  if(TIT.length){
    const rows=TIT.filter(t=>!/DISPONIBLE|^\[/i.test(t.nombre)).map(t=>({n:t.nombre.split(' ').slice(0,2).join(' '),d:diasEntre(t.inicio,t.fin)})).filter(r=>r.d);
    const o=base({indexAxis:'y'});o.plugins.legend.display=false;
    o.scales.x={grid:{color:css('--line')},ticks:{color:css('--ink-2')},title:{display:true,text:'Días en el cargo',color:css('--muted'),font:{size:11}}};
    o.scales.y={grid:{display:false},ticks:{color:css('--ink-2'),font:{size:10.5}}};
    o.plugins.tooltip.callbacks.label=c=>` ${c.parsed.x} días`;
    charts.push(new Chart(c_titulares,{type:'bar',data:{labels:rows.map(r=>r.n),datasets:[{data:rows.map(r=>r.d),
      backgroundColor:rows.map(r=>r.d<90?css('--crit'):sc(0)),borderRadius:3}]},options:o}));
  }

  // Normas tabla
  const tb=document.querySelector('#t_normas tbody');
  tb.innerHTML=NOR.map(n=>{const u=(n.url||'').startsWith('http');
    return `<tr><td>${n.tipo}</td><td>${n.numero}</td><td>${n.nombre}</td><td>${n.anio}</td><td>${u?`<a href="${n.url}" target="_blank" rel="noopener">El Peruano ↗</a>`:'<span style="color:var(--muted)">pendiente</span>'}</td></tr>`;}).join('');

  // Meta PNIG vs real
  const MV=P.metaviol;
  if(MV&&MV.anios&&MV.anios.length){
    const o=base();o.scales.y.title.text='% mujeres 15+';o.scales.y.ticks.callback=v=>v+'%';o.scales.y.beginAtZero=true;
    o.plugins.tooltip.callbacks.label=c=>c.parsed.y==null?null:` ${c.dataset.label}: ${c.parsed.y}%`;
    charts.push(new Chart(c_metaviol,{data:{labels:MV.anios,datasets:[
      {type:'line',label:'Meta PNIG (lo prometido)',data:MV.meta,borderColor:css('--good'),borderDash:[6,4],backgroundColor:'transparent',borderWidth:2,pointRadius:2,tension:.1,spanGaps:true},
      {type:'line',label:'Real (ENDES 12 meses)',data:MV.real,borderColor:css('--crit'),backgroundColor:'transparent',borderWidth:2.8,pointRadius:4,tension:.2,spanGaps:true}]},options:o}));
  }
  const tm=document.querySelector('#t_metas tbody');
  const eTxt={si:'Cumple',parcial:'En camino',no:'No cumple',sd:'s/d'},eCls={si:'e-si',parcial:'e-parc',no:'e-no',sd:'e-sd'};
  if(tm)tm.innerHTML=P.metas.map(m=>`<tr><td>${m.instrumento}</td><td>${m.indicador}</td><td>${m.lb!==''?m.lb+' ('+m.lb_anio+')':'—'}</td><td><b>${m.meta}</b> (${m.meta_anio})</td><td>${m.real||'—'}</td><td><span class="badge ${eCls[m.estado]||'e-sd'}">${eTxt[m.estado]||'s/d'}</span></td></tr>`).join('');
}
try{build();}catch(e){console.error('build() falló:',e);}
const root=document.documentElement;
// Restaurar tema guardado
try{const th=localStorage.getItem('mimp-tema');if(th)root.setAttribute('data-theme',th);}catch(e){}
function temaActual(){return root.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');}
document.getElementById('tgl').setAttribute('aria-pressed',String(temaActual()==='dark'));
document.getElementById('tgl').onclick=()=>{const nuevo=temaActual()==='dark'?'light':'dark';
  root.setAttribute('data-theme',nuevo);document.getElementById('tgl').setAttribute('aria-pressed',String(nuevo==='dark'));
  try{localStorage.setItem('mimp-tema',nuevo);}catch(e){}setTimeout(()=>{try{build();}catch(e){}},30);};
// A11y: alternativa textual para cada gráfico
try{document.querySelectorAll('canvas').forEach(c=>{const card=c.closest('.card');const h=card&&card.querySelector('h3');
  c.setAttribute('role','img');c.setAttribute('aria-label','Gráfico'+(h?': '+h.textContent.trim():'')+'. Las cifras están en el texto y las notas de la sección.');});}catch(e){}
matchMedia('(prefers-color-scheme:dark)').addEventListener('change',()=>{if(!root.getAttribute('data-theme'))build();});

/* ===== Menú hamburguesa (móvil) ===== */
function cerrarMenu(){const nv=document.querySelector('aside nav');const mb=document.getElementById('menuBtn');
  if(nv)nv.classList.remove('open');if(mb){mb.textContent='☰';mb.setAttribute('aria-expanded','false');}}
(function(){const mb=document.getElementById('menuBtn');if(!mb)return;
  const nv=document.querySelector('aside nav');
  mb.addEventListener('click',()=>{const o=nv.classList.toggle('open');mb.setAttribute('aria-expanded',o);mb.textContent=o?'✕':'☰';});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nv.classList.contains('open'))cerrarMenu();});
  document.addEventListener('click',e=>{if(nv.classList.contains('open')&&!e.target.closest('aside'))cerrarMenu();});})();

/* ===== Navegación por secciones (cada sección = una página) ===== */
(function(){
  const mainEl=document.querySelector('main');
  const secciones=[...mainEl.querySelectorAll(':scope > section')];
  const navLinks=[...document.querySelectorAll('aside nav a[href^="#"]')];
  function show(id){
    if(!secciones.some(s=>s.id===id)) id='resumen';
    secciones.forEach(s=>s.hidden=(s.id!==id));
    navLinks.forEach(a=>{const on=a.getAttribute('href')==='#'+id;a.classList.toggle('active',on);
      if(on)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
    try{history.replaceState(null,'','#'+id);}catch(e){}
    window.scrollTo(0,0);
    const sec=document.getElementById(id);if(sec){sec.setAttribute('tabindex','-1');try{sec.focus({preventScroll:true});}catch(e){}}
    requestAnimationFrame(()=>charts.forEach(c=>{try{c.resize();}catch(e){}}));
  }
  document.querySelectorAll('a[href^="#"]').forEach(a=>{
    const id=a.getAttribute('href').slice(1);
    if(secciones.some(s=>s.id===id))
      a.addEventListener('click',e=>{e.preventDefault();show(id);cerrarMenu();});
  });
  window.__show=show;
  show((location.hash||'#resumen').slice(1));
})();

/* ===== Mapa coroplético (Leaflet) ===== */
let __mapa=null, __capaLayer=null, __capaSel='gasto';
const normDep=s=>s.toUpperCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace('PROVINCIA CONSTITUCIONAL DEL ','').replace(' METROPOLITANA','').trim();
function valorCapa(nombre){
  const n=normDep(nombre), md=P.mapa_dep||{}, dep=D.por_departamento;
  if(__capaSel==='gasto'){
    const lbl=(dep.labels||[]).find(l=>normDep(l)===n);
    return lbl?anios.reduce((s,a)=>s+((dep.por_anio[a]||{})[lbl]||0),0)/1e6:0;
  }
  const k=Object.keys(md).find(x=>normDep(x)===n);
  return k&&md[k][__capaSel]!=null?md[k][__capaSel]:0;
}
function pintarMapa(gj){
  if(__capaLayer)__mapa.removeLayer(__capaLayer);
  const vals=gj.features.map(f=>valorCapa(f.properties.NOMBDEP)).filter(v=>v>0);
  const max=Math.max(1,...vals);
  const ac=css('--accent');
  const col=v=>{if(!v)return 'var(--line)'.trim()||'#eee';const t=Math.sqrt(v/max);
    return `rgba(109,40,217,${(0.12+t*0.8).toFixed(2)})`;};
  const fmt=v=>__capaSel==='gasto'?('S/ '+Math.round(v).toLocaleString('es-PE')+' M'):(v.toLocaleString('es-PE'));
  const lblCapa={gasto:'Devengado acumulado',feminicidios:'Feminicidios 2025',denuncias:'Denuncias sexuales 2024',atenciones:'Atenciones CEM 2025'};
  __capaLayer=L.geoJSON(gj,{style:f=>({fillColor:col(valorCapa(f.properties.NOMBDEP)),weight:1,color:css('--line'),fillOpacity:.9}),
    onEachFeature:(f,layer)=>{const nm=f.properties.NOMBDEP,v=valorCapa(nm);
      layer.bindTooltip('<b>'+nm+'</b><br>'+lblCapa[__capaSel]+': '+fmt(v),{sticky:true});
      layer.on('mouseover',()=>layer.setStyle({weight:2.5,color:ac}));
      layer.on('mouseout',()=>__capaLayer.resetStyle(layer));}}).addTo(__mapa);
}
let __gj=null;
function initMapa(){
  if(!window.L||__mapa)return;
  __mapa=L.map('mapa',{zoomControl:true,attributionControl:false,scrollWheelZoom:false}).setView([-9.8,-74.5],4.6);
  fetch('peru-departamentos.geojson').then(r=>r.json()).then(gj=>{__gj=gj;pintarMapa(gj);
    try{__mapa.fitBounds(__capaLayer.getBounds(),{padding:[8,8]});}catch(e){}}).catch(()=>{});
  document.querySelectorAll('#mapaTabs button').forEach(b=>b.addEventListener('click',()=>{
    document.querySelectorAll('#mapaTabs button').forEach(x=>x.classList.remove('active'));
    b.classList.add('active');__capaSel=b.dataset.capa;if(__gj)pintarMapa(__gj);}));
}
// Inicializar/refrescar el mapa al entrar a Territorio
const __origShow=window.__show;
if(__origShow){window.__show=function(id){__origShow(id);if(id==='territorio'){initMapa();setTimeout(()=>{try{__mapa&&__mapa.invalidateSize();}catch(e){}},60);}};}
document.querySelectorAll('a[href="#territorio"]').forEach(a=>a.addEventListener('click',()=>{setTimeout(()=>{initMapa();try{__mapa&&__mapa.invalidateSize();}catch(e){}},80);}));
if(location.hash==='#territorio'){initMapa();}

/* ===== Asistente de datos: gateway ai.tunky.net + respondedor local ===== */
const CHAT={
  endpoint:"https://ai.tunky.net/v1/chat",
  token:"__TUNKY__",   // X-Client-Token de ai.tunky.net (vacío = solo respondedor local)
  system:"Eres el asistente de una evaluación CRITICA de la gestion del MIMP (Ministerio de la Mujer del Peru, pliego 039), 2017-2025. Respondes en espanol, breve y con cifras. TESIS CENTRAL: el presupuesto se triplico (+134%) y se ejecuta al 99%, pero NO hay evidencia de impacto real: los feminicidios siguen en 130-170/año, las denuncias por violencia sexual casi se duplicaron (+90%) y el MIMP no cumple su propia meta (violencia de pareja 12 meses: real 7.5% en 2024 vs meta 4.8% a 2026). La UNICA 'mejora' es la encuesta ENDES (autorreporte 'alguna vez'), metodologicamente discutible, con ruptura de serie en 2020 y estancada desde entonces: es casi autoevaluacion complaciente, NO prueba de que la violencia bajo. Salvaguardas: la violencia es MULTISECTORIAL (no atribuir causalidad a un solo actor); distingue registro administrativo de encuesta. No inventes cifras."
};
const H=[]; let cOpen=false, cBusy=false, cGreet=false;
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[<>&]/g,c=>({"<":"&lt;",">":"&gt;","&":"&amp;"}[c]));
const cadd=(role,txt)=>{const l=$("chatLog");const d=document.createElement("div");d.className="msg "+role;d.textContent=txt;l.appendChild(d);l.scrollTop=l.scrollHeight;};
function cTyping(){const l=$("chatLog");const m=document.createElement("div");m.className="msg bot";m.innerHTML='<span class="typing"><i></i><i></i><i></i></span>';l.appendChild(m);l.scrollTop=l.scrollHeight;return m;}
function cSug(){const w=document.createElement("div");w.className="chat-suggest";
  ["¿Bajó la violencia?","¿Cumplió sus metas?","¿Cuánto ejecutó en 2024?","¿Cuántas ministras hubo?"].forEach(q=>{const b=document.createElement("button");b.textContent=q;b.onclick=()=>{w.remove();cHandle(q);};w.appendChild(b);});
  $("chatLog").appendChild(w);}
function cGreetFn(){if(cGreet)return;cGreet=true;
  cadd("bot","¡Hola! 👋 Soy el asistente de esta evaluación CRÍTICA del MIMP. Pregúntame si la violencia bajó de verdad, por el presupuesto y su ejecución, por las metas incumplidas o la rotación de ministras.");cSug();}

function localAnswer(q){
  const n=q.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"");
  const S=D.serie_anual, pN=S[S.length-1], p0=S[0];
  const m=n.match(/20(1[7-9]|2[0-5])/);
  const enTot=EN.series&&EN.series['total'];
  if(/ejecu|devenga|gast[oó]|presupuesto|pia|pim/.test(n)){
    if(m){const r=S.find(x=>x.anio===m[0]);if(r)return `En ${r.anio} el MIMP tuvo un PIM de S/ ${(r.pim/1e6).toFixed(1)} M y devengó S/ ${(r.devengado/1e6).toFixed(1)} M: ${r.ejecucion_pct.toFixed(1)}% de ejecución. Fuente: MEF Datos Abiertos, pliego 039.`;}
    return `El presupuesto del MIMP creció de S/ ${(p0.pia/1e6).toFixed(0)} M (${p0.anio}) a S/ ${(pN.pia/1e6).toFixed(0)} M (${pN.anio}), +${((pN.pia/p0.pia-1)*100).toFixed(0)}%. La ejecución fue alta todo el periodo (96–99%): el MIMP NO subejecuta. Fuente: MEF Datos Abiertos.`;
  }
  if(/meta|plan|promet|cumpl|estrateg|pnig/.test(n)){
    return "El MIMP no va camino a cumplir su propia meta. Su Política Nacional de Igualdad de Género (2019) fijó bajar la violencia física/sexual de pareja (últimos 12 meses) a 4,8% en 2026 y 2,4% en 2030. Pero el dato real de 2024 es 7,5%, por encima de la meta de ese año (6,0%) y lejos de la de 2026. Ver la sección 'Meta vs. resultado'.";
  }
  if(/violen|prevalen|endes|feminic|redujo|bajo|disminu|impacto|sirve|necesari/.test(n)){
    return "No hay evidencia consistente. La encuesta ENDES (autorreporte, la produce el INEI) bajó de 65% a 52%, pero es un indicador discutible, con ruptura de serie en 2020 y estancado desde entonces. Los HECHOS no acompañan: los feminicidios siguen en 130–170/año y las denuncias por violencia sexual casi se duplicaron (+90%). Y el MIMP no cumple su propia meta. Con las salvaguardas del caso (es multisectorial), no hay evidencia de que su acción esté reduciendo la violencia de género.";
  }
  if(/denuncia|sexual|violacion|violación/.test(n))
    return "Las denuncias por violencia sexual (registro PNP/MININTER, INEI) casi se duplicaron: de 5 683 (2016) a 10 819 (2024), y más de la mitad son contra menores de edad. Paradoja de registros: más denuncias puede ser más violencia o más disposición a denunciar. Es contexto multisectorial, no eficacia directa del MIMP.";
  if(/ministr|titular|rotac|cargo/.test(n))
    return `Hubo ~${TIT.length} titulares del MIMP entre 2016 y 2025 (con periodos de pocos días). Solo Nancy Tolentino tuvo una gestión larga (~15 meses). Alta rotación = conducción inestable pese a un marco normativo sólido.`;
  if(/en que|detalle|planilla|personal|cas|contrat/.test(n)){
    const d=D.por_detalle_gasto.labels.slice(0,3).join(", ");
    return `Los principales rubros de gasto son: ${d}. El CAS (Contrato Administrativo de Servicios) es el mayor rubro de contratación de personal. Ver secciones "Personal y planilla" y "¿En qué se gasta?".`;
  }
  if(/norma|ley|30364|politica/.test(n))
    return `El MIMP es rector de la Ley 30364 (2015) e impulsó la Política Nacional de Igualdad de Género (2019) y la Estrategia "Mujeres libres de violencia" (2021). Ver la tabla de marco normativo.`;
  if(/hola|ayuda|puedes|que sabes/.test(n))
    return "Puedo responderte sobre: presupuesto y ejecución, prevalencia ENDES, rotación de ministras, en qué se gasta y el marco normativo. ¿Qué te interesa?";
  return "Puedo contarte sobre el presupuesto (96–99% de ejecución), la prevalencia de violencia (ENDES, −13 pp), la rotación de ministras o en qué se gasta. Prueba una de esas.";
}
function cPick(d){if(!d)return null;if(typeof d==="string")return d;
  return d.reply||d.message||d.answer||d.response||d.text||d.content||(d.choices&&d.choices[0]&&((d.choices[0].message&&d.choices[0].message.content)||d.choices[0].text))||null;}
async function cGateway(text){
  const res=await fetch(CHAT.endpoint,{method:"POST",headers:{"Content-Type":"application/json","X-Client-Token":CHAT.token},
    body:JSON.stringify({message:text,messages:H.slice(-12),system:CHAT.system})});
  const raw=await res.text();let data;try{data=JSON.parse(raw);}catch(e){data=raw;}
  if(!res.ok)throw new Error((data&&data.error)||"HTTP "+res.status);
  return cPick(data)||"…";}
async function cHandle(text){
  text=(text||"").trim().slice(0,500);if(!text||cBusy)return;
  cadd("me",text);H.push({role:"user",content:text});cBusy=true;
  const sb=document.querySelector('#chatForm button[type=submit]');if(sb)sb.disabled=true;
  const t=cTyping();let reply;
  try{ if(CHAT.token&&CHAT.token.indexOf("__")!==0){ try{reply=await cGateway(text);}catch(e){reply=localAnswer(text);} } else reply=localAnswer(text); }
  catch(e){reply=localAnswer(text);}
  t.remove();cadd("bot",reply);H.push({role:"assistant",content:reply});cBusy=false;
  if(sb)sb.disabled=false;$("chatInput").focus();}
function cToggle(v){cOpen=v==null?!cOpen:v;$("chatPanel").hidden=!cOpen;$("chatFab").classList.toggle("hide",cOpen);
  if(cOpen){cGreetFn();setTimeout(()=>{try{$("chatInput").focus();}catch(e){}},40);}else{try{$("chatFab").focus();}catch(e){}}}
$("chatFab").onclick=()=>cToggle(true);
$("chatClose").onclick=()=>cToggle(false);
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&cOpen)cToggle(false);});
$("chatForm").onsubmit=e=>{e.preventDefault();const v=$("chatInput").value;$("chatInput").value="";cHandle(v);};
</script>
</body>
</html>
"""

_json_payload = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")  # evita cerrar el <script>
salida = (HTML.replace("/*__DATA__*/", _json_payload)
          .replace("__GA__", GA_ID).replace("__TUNKY__", TUNKY_TOKEN))
# Cada sección arranca oculta salvo "resumen" (navegación por pestañas, sin flash inicial).
import re as _hre
salida = _hre.sub(r'<section id="(?!resumen\b)([a-z0-9]+)"(?! hidden)', r'<section id="\1" hidden', salida)
(DIR_ENTREGABLES / "tablero_mimp.html").write_text(salida, encoding="utf-8")
docs = RAIZ / "docs"
docs.mkdir(exist_ok=True)
(docs / "index.html").write_text(salida, encoding="utf-8")

# Banner OG (SVG) para redes
og = '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
<rect width="1200" height="630" fill="#6d28d9"/>
<rect y="470" width="1200" height="160" fill="#4c1d95"/>
<text x="70" y="150" font-family="Georgia,serif" font-size="34" fill="#d8c8f5">EVALUACIÓN DE LA GESTIÓN · MIMP · PLIEGO 039</text>
<text x="70" y="270" font-family="Georgia,serif" font-size="80" font-weight="700" fill="#ffffff">¿Redujo la violencia,</text>
<text x="70" y="360" font-family="Georgia,serif" font-size="80" font-weight="700" fill="#ffffff">o solo gastó?</text>
<text x="70" y="440" font-family="Arial,sans-serif" font-size="30" fill="#e4d5f7">Presupuesto +134% · Ejecución 99% · Prevalencia −13 pp · 2017–2025</text>
<text x="70" y="560" font-family="Arial,sans-serif" font-size="26" fill="#b79ae6">Datos oficiales MEF · INEI–ENDES · unimauro.github.io/evaluacion-mimp</text>
</svg>'''
(docs / "og.svg").write_text(og, encoding="utf-8")
print("→ 04_entregables/tablero_mimp.html")
print("→ docs/index.html + docs/og.svg (GitHub Pages)")
print(f"ENDES años: {endes['anios']} | titulares: {len(titulares)} | normas: {len(normas)}")
