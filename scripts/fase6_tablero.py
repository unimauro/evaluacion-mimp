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
data = json.loads((DIR_ANALISIS / "presupuesto_dashboard.json").read_text(encoding="utf-8"))


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

# --- Normas ---
norm_rows = leer_csv("normas_mimp_*.csv")
normas = [{"tipo": r.get("tipo", ""), "numero": r.get("numero", ""), "nombre": r.get("nombre", ""),
           "anio": r.get("anio", ""), "url": r.get("url", "")} for r in norm_rows]

payload = {"presupuesto": data, "endes": endes, "titulares": titulares, "normas": normas,
           "feminicidios": femi, "generado": date.today().isoformat()}

HTML = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>¿El MIMP redujo la violencia?</title>
<meta name="description" content="Evaluación de la gestión del MIMP (pliego 039) 2017-2025: casi triplicó su presupuesto y lo ejecuta al 99%; la prevalencia de violencia de pareja cayó 13 puntos. ¿Mérito propio o contexto multisectorial?">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='20' fill='%236d28d9'/%3E%3Ctext x='50' y='72' font-size='62' text-anchor='middle' fill='white' font-family='Georgia,serif'%3E%E2%99%80%3C/text%3E%3C/svg%3E">
<meta property="og:type" content="website">
<meta property="og:title" content="¿El MIMP redujo la violencia, o solo gastó?">
<meta property="og:description" content="El MIMP casi triplicó su presupuesto (S/ 426M→996M) y lo ejecuta al 99%. La prevalencia de violencia de pareja cayó de 65% a 52%. Evaluación con datos oficiales, 2017-2025.">
<meta property="og:url" content="https://unimauro.github.io/evaluacion-mimp/">
<meta property="og:image" content="https://unimauro.github.io/evaluacion-mimp/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="¿El MIMP redujo la violencia, o solo gastó?">
<meta name="twitter:description" content="Evaluación con datos oficiales del MIMP 2017-2025: presupuesto, servicios, impacto e hipótesis.">
<meta name="twitter:image" content="https://unimauro.github.io/evaluacion-mimp/og.png">
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=__GA__"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', '__GA__');
</script>
<style>
:root{
  --surface:#faf7fc; --panel:#ffffff; --ink:#1a1420; --ink-2:#5c5364; --muted:#8f869a;
  --line:#ece5f2; --line-2:#ddd3e6; --accent:#6d28d9; --accent-2:#c0248f; --ground:#f2ecf7;
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

.note{background:var(--ground);border:1px solid var(--line);border-left:3px solid var(--warn);border-radius:10px;padding:14px 16px;font-size:13.5px;color:var(--ink-2)}
.note b{color:var(--ink)}
table.norm{width:100%;border-collapse:collapse;font-size:13px}
table.norm th,table.norm td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}
table.norm th{color:var(--muted);font-weight:600;font-size:11.5px;text-transform:uppercase;letter-spacing:.04em}
table.norm a{color:var(--accent);text-decoration:none}
.tablewrap{overflow-x:auto}
footer{margin-top:54px;border-top:1px solid var(--line);padding-top:18px;color:var(--muted);font-size:12.5px}
.toggle{position:fixed;top:12px;right:12px;background:var(--panel);border:1px solid var(--line-2);color:var(--ink-2);border-radius:20px;padding:6px 13px;font-size:12.5px;cursor:pointer;font-family:inherit;z-index:6}
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
@media (max-width:860px){.layout{grid-template-columns:1fr}aside{position:static;height:auto;border-right:none;border-bottom:1px solid var(--line)}
  aside nav{flex-direction:row;flex-wrap:wrap}aside .foot{display:none}main{padding:24px 18px 60px}.story{grid-template-columns:1fr}}
</style>
</head>
<body>
<button class="toggle" id="tgl" aria-label="Cambiar tema">◐ Tema</button>
<div class="layout">
  <aside>
    <div class="brand">Evaluación <span>MIMP</span></div>
    <div class="tag">Pliego 039 · 2017–2025</div>
    <nav>
      <a href="#inicio">Resumen</a>
      <a class="sec">Dimensiones</a>
      <a href="#impacto">Impacto: ¿bajó la violencia?</a>
      <a href="#presupuesto">Presupuesto y ejecución</a>
      <a href="#planilla">Personal y planilla</a>
      <a href="#gasto">¿En qué se gasta?</a>
      <a href="#territorio">Territorio</a>
      <a href="#gestion">Gestión y rotación</a>
      <a href="#normas">Marco normativo</a>
      <a class="sec">Conclusión</a>
      <a href="#hipotesis">Hipótesis H1–H6</a>
    </nav>
    <div class="foot">Datos oficiales: MEF, INEI–ENDES, Portal Warmi Ñan, El Peruano.<br>Descarga 2026-09-08. Reproducible.</div>
  </aside>

  <main id="inicio">
    <div class="eyebrow">Evaluación de la gestión pública</div>
    <h1>¿El MIMP redujo la violencia, o solo gastó?</h1>
    <p class="dek">Entre 2017 y 2025 el Ministerio de la Mujer <b>casi triplicó su presupuesto</b> y lo ejecuta
      casi al 100%. En el mismo periodo, la prevalencia de violencia de pareja <b>cayó 13 puntos</b>. La pregunta
      no es si gastó bien, sino <b>cuánto de esa mejora es mérito propio</b> y cuánto es un problema multisectorial.</p>
    <p class="src">Fuentes: MEF Datos Abiertos (pliego <code>039</code>), INEI–ENDES, Portal Warmi Ñan, El Peruano · descarga <code>2026-09-08</code> · soles corrientes.</p>

    <div class="story">
      <div class="tell">
        <h2>La historia en tres cifras</h2>
        <p class="big">1 · El presupuesto <b class="up">creció +134%</b> (S/ 426 M → 996 M) y la ejecución fue
          <b class="up">96–99%</b> todos los años: el MIMP <b>no subejecuta</b>.</p>
        <p class="big">2 · La prevalencia de violencia de pareja <b class="dn">bajó de 65% a 52%</b> (−13 pp, ENDES),
          pero los <b class="dn">feminicidios no ceden</b> (130–170/año): la magnitud baja, lo extremo resiste.</p>
        <p class="big">3 · Pero hubo <b class="dn">~15 ministras/os en 9 años</b>: la conducción es
          <b>inestable</b> pese a un marco normativo sólido.</p>
        <p style="margin-bottom:0"><b>Salvaguarda:</b> la caída de la violencia es multisectorial (contribución, no
          atribución); los registros administrativos no se comparan con la prevalencia poblacional.</p>
      </div>
      <div class="viz">
        <h3>Gasto que sube, violencia que baja</h3>
        <p class="cap">Devengado del MIMP (millones S/) vs. prevalencia ENDES (%). Dos escalas, dos historias.</p>
        <div class="chart-box"><canvas id="c_story"></canvas></div>
      </div>
    </div>

    <div class="kpis" id="kpis"></div>
  </main>
</div>

<div class="layout"><aside style="visibility:hidden"></aside><main style="padding-top:0">

  <section id="impacto">
    <h2>Impacto: prevalencia de violencia (ENDES)</h2>
    <p class="lead">Prevalencia de violencia contra la mujer ejercida alguna vez por la pareja (INEI–ENDES, mujeres
      15–49 alguna vez unidas). <b>Magnitud del problema</b>, no registro de atenciones. El total cae 13 pp.</p>
    <div class="grid">
      <div class="card full"><h3>Prevalencia por tipo de violencia</h3><p class="cap">% de mujeres, por año</p><div class="chart-box tall"><canvas id="c_endes"></canvas></div></div>
      <div class="card full"><h3>Feminicidios y tentativas (contexto)</h3><p class="cap">Casos registrados por año · registro Warmi Ñan · <b>contexto multisectorial</b></p><div class="chart-box"><canvas id="c_femi"></canvas></div></div>
    </div>
    <div class="note" style="margin-top:14px"><b>El dato que incomoda:</b> mientras la prevalencia poblacional bajó 13 pp, los <b>feminicidios no descienden</b> (oscilan 130–170 al año). La magnitud del problema cede, pero su expresión más extrema se mantiene. Feminicidios = contexto (investiga el Ministerio Público), no eficacia directa del MIMP.</div>
    <div class="note" style="margin-top:14px"><b>Contribución, no atribución.</b> La caída es multisectorial (MP, PJ, Mininter, salud, educación, sociedad civil), no atribuible solo al MIMP. La violencia <b>económica</b> no la mide la ENDES (corresponde a ENARES): <code>[NO DISPONIBLE]</code>.</div>
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
    <p class="lead">Gasto en planilla (personal nombrado + CAS) mes a mes por año. El número de trabajadores por
      régimen (PTE) está en recolección; aquí se muestra el <b>costo</b> de la planilla, que sí es trazable al MEF.</p>
    <div class="grid">
      <div class="card full"><h3>Gasto de planilla mes a mes</h3><p class="cap">Devengado en personal + CAS, millones S/ · línea gruesa = último año</p><div class="chart-box tall"><canvas id="c_planilla"></canvas></div></div>
    </div>
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
      <div class="hcard v-parc"><div class="hid">H1 · Impacto</div><h4>La violencia no disminuyó pese al gasto</h4>
        <span class="verdict v-parc">Se sostiene parcialmente</span>
        <p><b>La violencia sí bajó en magnitud:</b> la prevalencia ENDES cayó 13 pp (65,4%→52,0%),
        sobre todo psicológica y física. <b>Pero los feminicidios no descienden</b> (130–170/año). La
        parte que cede es multisectorial (el MIMP contribuye, no es mérito exclusivo); lo más extremo resiste.</p></div>
      <div class="hcard v-parc"><div class="hid">H3 · Presupuesto</div><h4>El presupuesto es bajo y/o se subejecuta</h4>
        <span class="verdict v-parc">Se sostiene parcialmente</span>
        <p>Subejecución <b>NO</b>: ejecutó 96–99%. PIA <b>+134%</b>. "Bajo" solo como peso del presupuesto
        nacional (~0,4%), pendiente de cerrar el denominador.</p></div>
      <div class="hcard v-parc"><div class="hid">H6 · Gestión</div><h4>Predomina la gestión de imagen sobre resultados</h4>
        <span class="verdict v-parc">Se sostiene parcialmente</span>
        <p>Marco normativo sólido (Ley 30364, PNIG, Estrategia). Pero <b>~15 titulares en 9 años</b>
        (5 en 17 meses bajo un gobierno): inestabilidad de conducción frente a continuidad normativa.</p></div>
      <div class="hcard v-pend"><div class="hid">H2 · Servicios</div><h4>La producción de servicios está estancada</h4>
        <span class="verdict v-pend">Datos en recolección</span>
        <p>Requiere atenciones CEM por tipo y Línea 100 (Portal Warmi Ñan). En curso.</p></div>
      <div class="hcard v-parc"><div class="hid">H4 · Cobertura</div><h4>Brechas de cobertura territorial vs. incidencia</h4>
        <span class="verdict v-parc">Parcial</span>
        <p>Gasto muy concentrado en Lima (ver territorio); falta cruzar con N.º de CEM e incidencia por región.</p></div>
      <div class="hcard v-pend"><div class="hid">H5 · Calidad</div><h4>Problemas de calidad/idoneidad en la atención</h4>
        <span class="verdict v-pend">Datos en recolección</span>
        <p>Requiere personal por régimen (PTE) e informes de supervisión de CEM (Defensoría 255/179). En curso.</p></div>
    </div>
  </section>

  <footer>
    Repositorio <b>evaluacion-mimp</b> · desplegado en GitHub Pages. Toda cifra es trazable a su fuente oficial con
    fecha de descarga 2026-09-08. Ninguna cifra sin fuente + URL + fecha. Analítica: Google Analytics.
  </footer>
</main></div>

<button class="chat-fab" id="chatFab" aria-label="Abrir asistente de datos">
  <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-8.5 8.4 8.7 8.7 0 0 1-4-.9L3 20l1.1-4.9a8.4 8.4 0 0 1-1-4 8.4 8.4 0 0 1 8.5-8.4 8.4 8.4 0 0 1 8.4 8.3z"/></svg>
</button>
<div class="chat-panel" id="chatPanel" hidden>
  <div class="chat-top"><span class="chat-dot"></span>
    <div><b>Asistente de la evaluación</b><span>IA · pregunta por las cifras</span></div>
    <button class="chat-x" id="chatClose" aria-label="Cerrar">✕</button></div>
  <div class="chat-log" id="chatLog"></div>
  <form class="chat-form" id="chatForm">
    <input id="chatInput" type="text" autocomplete="off" placeholder="Ej.: ¿Cuánto ejecutó el MIMP en 2024?" maxlength="500">
    <button type="submit" aria-label="Enviar"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg></button>
  </form>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
const P = /*__DATA__*/;
const D = P.presupuesto, EN = P.endes, TIT = P.titulares, NOR = P.normas;
const css = v => getComputedStyle(document.body).getPropertyValue(v).trim();
const SER=['--s1','--s2','--s3','--s4','--s5','--s6','--s7','--s8'], sc=i=>css(SER[i%8]);
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
function diasEntre(a,b){if(!a)return null;const d1=new Date(a),d2=b?new Date(b):new Date('2025-08-31');
  return Math.max(1,Math.round((d2-d1)/86400000));}

function build(){
  charts.forEach(c=>c.destroy());charts=[];
  const S=D.serie_anual,pN=S[S.length-1],p0=S[0];
  const crec=(pN.pia/p0.pia-1)*100,ejecProm=S.reduce((a,b)=>a+b.ejecucion_pct,0)/S.length;
  const enTot=EN.series&&(EN.series['total']||EN.series['Total']);
  const cae = enTot? (enTot[0]-enTot[enTot.length-1]).toFixed(1):null;
  document.getElementById('kpis').innerHTML=[
    ['PIA '+pN.anio,fmtM(pN.pia),'inicial de apertura'],
    ['Ejecución '+pN.anio,pN.ejecucion_pct.toFixed(1)+'%','<span class="k-up">no subejecuta</span>'],
    ['Crecim. PIA '+p0.anio.slice(2)+'→'+pN.anio.slice(2),'<span class="k-up">+'+crec.toFixed(0)+'%</span>','nominal'],
    enTot?['Prevalencia ENDES','<span class="k-dn">−'+cae+' pp</span>',enTot[0]+'% → '+enTot[enTot.length-1]+'%']:['Prevalencia ENDES','—','en proceso'],
    ['Titulares 2016–25','<span class="k-dn">'+TIT.length+'</span>','rotación alta'],
  ].map(k=>`<div class="kpi"><div class="k-label">${k[0]}</div><div class="k-val">${k[1]}</div><div class="k-note">${k[2]}</div></div>`).join('');

  // Story: dual axis (excepción consciente: dos historias, gasto vs prevalencia)
  if(enTot){
    const o=base();o.plugins.legend.display=true;o.interaction.mode='index';
    o.scales.y.title.text='Devengado (M S/)';
    o.scales.y1={position:'right',grid:{drawOnChartArea:false},ticks:{color:css('--accent-2'),callback:v=>v+'%'},
      title:{display:true,text:'Prevalencia (%)',color:css('--accent-2'),font:{size:11}},suggestedMin:40,suggestedMax:70};
    o.plugins.tooltip.callbacks.label=c=>c.dataset.yAxisID==='y1'?` ${c.dataset.label}: ${c.parsed.y}%`:` ${c.dataset.label}: ${fmtM(c.parsed.y*1e6)}`;
    charts.push(new Chart(c_story,{data:{labels:anios,datasets:[
      {type:'bar',label:'Devengado',data:S.map(r=>M(r.devengado)),backgroundColor:sc(0),borderRadius:3,order:2},
      {type:'line',label:'Prevalencia ENDES',yAxisID:'y1',data:anios.map(a=>{const i=EN.anios.indexOf(a);return i>=0?enTot[i]:null;}),
        borderColor:css('--accent-2'),backgroundColor:'transparent',borderWidth:2.4,pointRadius:3,tension:.25,spanGaps:true,order:1}]},options:o}));
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

  // Titulares: días en el cargo
  if(TIT.length){
    const rows=TIT.map(t=>({n:t.nombre.split(' ').slice(0,2).join(' '),d:diasEntre(t.inicio,t.fin)})).filter(r=>r.d);
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
}
build();
const root=document.documentElement;
document.getElementById('tgl').onclick=()=>{const cur=root.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
  root.setAttribute('data-theme',cur==='dark'?'light':'dark');setTimeout(build,30);};
matchMedia('(prefers-color-scheme:dark)').addEventListener('change',()=>{if(!root.getAttribute('data-theme'))build();});

/* ===== Asistente de datos: gateway ai.tunky.net + respondedor local ===== */
const CHAT={
  endpoint:"https://ai.tunky.net/v1/chat",
  token:"__TUNKY__",   // X-Client-Token de ai.tunky.net (vacío = solo respondedor local)
  system:"Eres el asistente de la evaluación de la gestión del MIMP (Ministerio de la Mujer del Perú, pliego 039), 2017-2025. Respondes en español, breve y con cifras. Regla clave: los feminicidios y la violencia son un problema MULTISECTORIAL; el MIMP contribuye pero no se le atribuye en exclusiva. Distingue registro administrativo de prevalencia poblacional (ENDES)."
};
const H=[]; let cOpen=false, cBusy=false, cGreet=false;
const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[<>&]/g,c=>({"<":"&lt;",">":"&gt;","&":"&amp;"}[c]));
const cadd=(role,txt)=>{const l=$("chatLog");const d=document.createElement("div");d.className="msg "+role;d.textContent=txt;l.appendChild(d);l.scrollTop=l.scrollHeight;};
function cTyping(){const l=$("chatLog");const m=document.createElement("div");m.className="msg bot";m.innerHTML='<span class="typing"><i></i><i></i><i></i></span>';l.appendChild(m);l.scrollTop=l.scrollHeight;return m;}
function cSug(){const w=document.createElement("div");w.className="chat-suggest";
  ["¿Cuánto ejecutó en 2024?","¿Bajó la violencia?","¿Cuántas ministras hubo?","¿En qué se gasta?"].forEach(q=>{const b=document.createElement("button");b.textContent=q;b.onclick=()=>{w.remove();cHandle(q);};w.appendChild(b);});
  $("chatLog").appendChild(w);}
function cGreetFn(){if(cGreet)return;cGreet=true;
  cadd("bot","¡Hola! 👋 Soy el asistente de esta evaluación del MIMP. Pregúntame por el presupuesto, la ejecución, la prevalencia de violencia (ENDES) o la rotación de ministras.");cSug();}

function localAnswer(q){
  const n=q.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"");
  const S=D.serie_anual, pN=S[S.length-1], p0=S[0];
  const m=n.match(/20(1[7-9]|2[0-5])/);
  const enTot=EN.series&&EN.series['total'];
  if(/ejecu|devenga|gast[oó]|presupuesto|pia|pim/.test(n)){
    if(m){const r=S.find(x=>x.anio===m[0]);if(r)return `En ${r.anio} el MIMP tuvo un PIM de S/ ${(r.pim/1e6).toFixed(1)} M y devengó S/ ${(r.devengado/1e6).toFixed(1)} M: ${r.ejecucion_pct.toFixed(1)}% de ejecución. Fuente: MEF Datos Abiertos, pliego 039.`;}
    return `El presupuesto del MIMP creció de S/ ${(p0.pia/1e6).toFixed(0)} M (${p0.anio}) a S/ ${(pN.pia/1e6).toFixed(0)} M (${pN.anio}), +${((pN.pia/p0.pia-1)*100).toFixed(0)}%. La ejecución fue alta todo el periodo (96–99%): el MIMP NO subejecuta. Fuente: MEF Datos Abiertos.`;
  }
  if(/violen|prevalen|endes|feminic|redujo|bajo|disminu/.test(n)){
    if(enTot)return `Según INEI–ENDES, la prevalencia de violencia de pareja (alguna vez) cayó de ${enTot[0]}% (${EN.anios[0]}) a ${enTot[enTot.length-1]}% (${EN.anios[EN.anios.length-1]}), unos ${(enTot[0]-enTot[enTot.length-1]).toFixed(1)} puntos menos. Es magnitud poblacional, no atenciones. Salvaguarda: la mejora es MULTISECTORIAL, no atribuible solo al MIMP.`;
    return "La prevalencia de violencia (ENDES) está en el tablero, sección Impacto.";
  }
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
  text=(text||"").trim();if(!text||cBusy)return;
  cadd("me",text);H.push({role:"user",content:text});cBusy=true;$("chatSend");
  const t=cTyping();let reply;
  try{ if(CHAT.token&&CHAT.token.indexOf("__")!==0){ try{reply=await cGateway(text);}catch(e){reply=localAnswer(text);} } else reply=localAnswer(text); }
  catch(e){reply=localAnswer(text);}
  t.remove();cadd("bot",reply);H.push({role:"assistant",content:reply});cBusy=false;$("chatInput").focus();}
function cToggle(v){cOpen=v==null?!cOpen:v;$("chatPanel").hidden=!cOpen;$("chatFab").classList.toggle("hide",cOpen);if(cOpen)cGreetFn();}
$("chatFab").onclick=()=>cToggle(true);
$("chatClose").onclick=()=>cToggle(false);
$("chatForm").onsubmit=e=>{e.preventDefault();const v=$("chatInput").value;$("chatInput").value="";cHandle(v);};
</script>
</body>
</html>
"""

salida = (HTML.replace("/*__DATA__*/", json.dumps(payload, ensure_ascii=False))
          .replace("__GA__", GA_ID).replace("__TUNKY__", TUNKY_TOKEN))
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
