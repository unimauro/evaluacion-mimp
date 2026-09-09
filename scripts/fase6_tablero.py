"""Fase 6 — Tablero de indicadores del MIMP (HTML standalone para GitHub Pages).

Lee 03_analisis/presupuesto_dashboard.json (Fase 3) y escribe un HTML autocontenido
(documento completo) con la data inline y Chart.js (cdnjs). Incluye la sección de
contraste de hipótesis H1–H6. No inventa: solo grafica lo procesado y marca lo pendiente.

Uso:  python scripts/fase6_tablero.py
Salida: 04_entregables/tablero_mimp.html  y  docs/index.html (para GitHub Pages).
"""
from __future__ import annotations

import json

from config import DIR_ANALISIS, DIR_ENTREGABLES, RAIZ

data = json.loads((DIR_ANALISIS / "presupuesto_dashboard.json").read_text(encoding="utf-8"))

HTML = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Evaluación del MIMP 2017-2025</title>
<meta name="description" content="Evaluación de la gestión del MIMP (pliego 039), 2017-2025: presupuesto, servicios, impacto e hipótesis, con datos oficiales.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Public+Sans:wght@400;500;600;700&display=swap">
<style>
:root{
  --surface:#fcfcfb; --panel:#ffffff; --ink:#0b0b0b; --ink-2:#52514e; --muted:#8a8880;
  --line:#e7e5df; --line-2:#d9d7cf; --accent:#1c5cab; --ground:#f3f1ec;
  --good:#008300; --warn:#c98500; --crit:#e34948;
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100; --s5:#e87ba4; --s6:#4a3aa7; --s7:#008300; --s8:#e34948;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --surface:#161615; --panel:#1f1f1d; --ink:#f7f6f2; --ink-2:#c3c2b7; --muted:#8f8d84;
  --line:#2e2e2b; --line-2:#3a3a36; --accent:#7fb0ee; --ground:#121211;
  --good:#3faa3f; --warn:#e0a83a; --crit:#e66767;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181; --s6:#9085e9; --s7:#12a012; --s8:#e66767;
}}
:root[data-theme="dark"]{
  --surface:#161615; --panel:#1f1f1d; --ink:#f7f6f2; --ink-2:#c3c2b7; --muted:#8f8d84;
  --line:#2e2e2b; --line-2:#3a3a36; --accent:#7fb0ee; --ground:#121211;
  --good:#3faa3f; --warn:#e0a83a; --crit:#e66767;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181; --s6:#9085e9; --s7:#12a012; --s8:#e66767;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--surface);color:var(--ink);
  font-family:"Public Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
img{max-width:100%}
.wrap{max-width:1180px;margin:0 auto;padding:32px 24px 72px}
header.top{border-bottom:2px solid var(--ink);padding-bottom:20px;margin-bottom:8px}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:700}
h1{font-family:"Fraunces",Georgia,serif;font-weight:600;font-size:clamp(30px,5vw,48px);
  line-height:1.04;margin:.22em 0 .15em;text-wrap:balance;letter-spacing:-.01em}
.sub{color:var(--ink-2);max-width:72ch;font-size:15.5px}
.src{color:var(--muted);font-size:12.5px;margin-top:10px}
.src code{background:var(--ground);padding:1px 5px;border-radius:4px;font-size:12px}
nav.jump{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 0}
nav.jump a{font-size:12.5px;color:var(--ink-2);text-decoration:none;border:1px solid var(--line-2);
  padding:5px 11px;border-radius:20px}
nav.jump a:hover{border-color:var(--accent);color:var(--accent)}

.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(175px,1fr));gap:14px;margin:26px 0 8px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.kpi .k-label{font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);font-weight:600}
.kpi .k-val{font-family:"Fraunces",Georgia,serif;font-size:29px;font-weight:600;margin-top:6px;
  font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.kpi .k-note{font-size:12.5px;color:var(--ink-2);margin-top:3px}
.k-up{color:var(--good)} .k-flat{color:var(--warn)}

section{margin-top:44px;scroll-margin-top:20px}
h2{font-family:"Fraunces",Georgia,serif;font-weight:600;font-size:23px;margin:0 0 4px;letter-spacing:-.01em}
.lead{color:var(--ink-2);font-size:14px;margin:0 0 18px;max-width:80ch}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:18px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 18px 14px}
.card h3{font-size:14.5px;font-weight:700;margin:0 0 2px}
.card p.cap{font-size:12.5px;color:var(--muted);margin:0 0 12px}
.chart-box{position:relative;height:300px}
.chart-box.tall{height:360px}
.full{grid-column:1/-1}

.hyp{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px}
.hcard{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 17px;border-left:4px solid var(--muted)}
.hcard.v-no{border-left-color:var(--good)}
.hcard.v-si{border-left-color:var(--crit)}
.hcard.v-parc{border-left-color:var(--warn)}
.hcard.v-pend{border-left-color:var(--line-2)}
.hcard .hid{font-size:12px;font-weight:700;letter-spacing:.08em;color:var(--muted)}
.hcard h4{margin:4px 0 6px;font-size:15px;font-weight:700;line-height:1.3}
.verdict{display:inline-block;font-size:11.5px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;
  padding:3px 9px;border-radius:20px;margin-bottom:8px}
.verdict.v-no{background:rgba(0,131,0,.13);color:var(--good)}
.verdict.v-si{background:rgba(227,73,72,.14);color:var(--crit)}
.verdict.v-parc{background:rgba(201,133,0,.15);color:var(--warn)}
.verdict.v-pend{background:var(--ground);color:var(--muted)}
.hcard p{margin:0;font-size:13.2px;color:var(--ink-2)}

.note{background:var(--ground);border:1px solid var(--line);border-left:3px solid var(--warn);
  border-radius:10px;padding:14px 16px;font-size:13.5px;color:var(--ink-2)}
.note b{color:var(--ink)}
footer{margin-top:52px;border-top:1px solid var(--line);padding-top:18px;color:var(--muted);font-size:12.5px}
.toggle{position:fixed;top:14px;right:14px;background:var(--panel);border:1px solid var(--line-2);
  color:var(--ink-2);border-radius:20px;padding:6px 13px;font-size:12.5px;cursor:pointer;font-family:inherit;z-index:5}
@media (max-width:640px){.wrap{padding:22px 16px 56px}}
</style>
</head>
<body>
<button class="toggle" id="tgl" aria-label="Cambiar tema">Tema</button>
<div class="wrap">
  <header class="top">
    <div class="eyebrow">Evaluación de la gestión pública · Pliego 039</div>
    <h1>¿El MIMP redujo la violencia, o solo gastó?</h1>
    <p class="sub">Evaluación de la gestión del Ministerio de la Mujer y Poblaciones Vulnerables,
      2017&ndash;2025, con datos abiertos oficiales. Distingue la <b>eficacia presupuestal propia</b>
      del MIMP de su <b>contribución</b> a un problema multisectorial. Vista previa: la dimensión
      presupuestal está completa; servicios, impacto, personal y normativa están en recolección.</p>
    <p class="src">Fuentes: MEF Datos Abiertos (presupuesto, pliego <code>039</code>, descarga <code>2026-09-08</code>);
      INEI&ndash;ENDES, Portal Warmi Ñan, Observatorio y PTE (en proceso). Soles corrientes.</p>
    <nav class="jump">
      <a href="#presupuesto">Presupuesto</a><a href="#gasto">Composición del gasto</a>
      <a href="#territorio">Territorio</a><a href="#hipotesis">Hipótesis H1&ndash;H6</a>
    </nav>
  </header>

  <div class="kpis" id="kpis"></div>

  <section id="presupuesto">
    <h2>Presupuesto y ejecución</h2>
    <p class="lead">PIA (inicial), PIM (modificado) y devengado por año, con el % de ejecución (devengado/PIM)
      y el monto no ejecutado. Nota: el presupuesto salta de S/ 444 M (2018) a S/ 733 M (2019).</p>
    <div class="grid">
      <div class="card full"><h3>PIA · PIM · Devengado por año</h3>
        <p class="cap">Millones de soles corrientes</p><div class="chart-box tall"><canvas id="c_serie"></canvas></div></div>
      <div class="card"><h3>Ejecución presupuestal</h3>
        <p class="cap">Devengado / PIM (%)</p><div class="chart-box"><canvas id="c_ejec"></canvas></div></div>
      <div class="card"><h3>Presupuesto no ejecutado</h3>
        <p class="cap">PIM − Devengado (millones S/)</p><div class="chart-box"><canvas id="c_noejec"></canvas></div></div>
    </div>
  </section>

  <section id="gasto">
    <h2>¿En qué se ejecuta el gasto?</h2>
    <p class="lead">Devengado por unidad ejecutora, programa presupuestal, genérica de gasto,
      fuente de financiamiento y categoría económica.</p>
    <div class="grid">
      <div class="card"><h3>Por unidad ejecutora</h3><p class="cap">Devengado, millones S/</p><div class="chart-box tall"><canvas id="c_ue"></canvas></div></div>
      <div class="card"><h3>Por programa presupuestal</h3><p class="cap">Devengado, millones S/ (top)</p><div class="chart-box tall"><canvas id="c_prog"></canvas></div></div>
      <div class="card"><h3>Por genérica de gasto</h3><p class="cap">Devengado, millones S/</p><div class="chart-box tall"><canvas id="c_gen"></canvas></div></div>
      <div class="card"><h3>Por fuente de financiamiento</h3><p class="cap">Devengado, millones S/</p><div class="chart-box tall"><canvas id="c_ff"></canvas></div></div>
      <div class="card"><h3>Corriente vs. capital</h3><p class="cap">Devengado, millones S/</p><div class="chart-box"><canvas id="c_cat"></canvas></div></div>
      <div class="card"><h3>Estacionalidad del devengado</h3><p class="cap">Devengado mensual, millones S/</p><div class="chart-box"><canvas id="c_mens"></canvas></div></div>
    </div>
  </section>

  <section id="territorio">
    <h2>Distribución territorial del gasto</h2>
    <p class="lead">Devengado acumulado 2017&ndash;2025 por departamento (departamento de la meta).
      Insumo para brechas de cobertura frente a la incidencia (H4).</p>
    <div class="grid"><div class="card full"><h3>Devengado por departamento</h3>
      <p class="cap">Acumulado del periodo, millones S/ (top 15)</p>
      <div class="chart-box" style="height:440px"><canvas id="c_dept"></canvas></div></div></div>
  </section>

  <section id="hipotesis">
    <h2>Contraste de hipótesis H1&ndash;H6</h2>
    <p class="lead">Veredicto preliminar por hipótesis. Verde = no se sostiene; rojo = se sostiene;
      ámbar = parcial; gris = datos en recolección. Solo H3 tiene ya evidencia dura (presupuesto).</p>
    <div class="hyp">
      <div class="hcard v-parc"><div class="hid">H3 · Presupuesto</div><h4>El presupuesto es bajo y/o se subejecuta</h4>
        <span class="verdict v-parc">Se sostiene parcialmente</span>
        <p>La <b>subejecución NO se sostiene</b>: la ejecución fue 96,4%&ndash;99,0% en todo el periodo.
        El PIA <b>creció +134%</b> nominal (2017&rarr;2025). Lo &laquo;bajo&raquo; solo se sostiene como
        <b>peso en el presupuesto nacional</b> (~0,4%), pendiente de calcular el denominador.</p></div>
      <div class="hcard v-pend"><div class="hid">H1 · Impacto</div><h4>La violencia no disminuyó pese al gasto</h4>
        <span class="verdict v-pend">Datos en recolección</span>
        <p>Requiere la serie de prevalencia INEI&ndash;ENDES por tipo (psicológica, física, sexual) y
        feminicidios de contexto. Recolección en curso. <b>Salvaguarda:</b> contribución, no atribución.</p></div>
      <div class="hcard v-pend"><div class="hid">H2 · Servicios</div><h4>La producción de servicios está estancada</h4>
        <span class="verdict v-pend">Datos en recolección</span>
        <p>Requiere la serie de atenciones CEM por tipo de violencia y Línea 100 (Portal Warmi Ñan).
        Recolección en curso.</p></div>
      <div class="hcard v-pend"><div class="hid">H4 · Cobertura</div><h4>Brechas de cobertura territorial vs. incidencia</h4>
        <span class="verdict v-pend">Parcial</span>
        <p>Ya hay gasto por departamento (abajo); falta cruzar con N.º de CEM e incidencia por región.</p></div>
      <div class="hcard v-pend"><div class="hid">H5 · Calidad</div><h4>Problemas de calidad/idoneidad en la atención</h4>
        <span class="verdict v-pend">Datos en recolección</span>
        <p>Requiere personal por régimen (PTE) e informes de supervisión de CEM (Defensoría N.º 255/179).</p></div>
      <div class="hcard v-pend"><div class="hid">H6 · Gestión</div><h4>Predomina la gestión de imagen sobre resultados</h4>
        <span class="verdict v-pend">Datos en recolección</span>
        <p>Insumos: rotación de titulares (~13 en ~6 años, a confirmar con RS) y marco normativo impulsado
        (Ley 30364 y modif.). Recolección en curso.</p></div>
    </div>
    <div class="note" style="margin-top:16px">
      <b>Contribución, no atribución.</b> Los feminicidios, violaciones y desapariciones son contexto
      multisectorial (investiga el Ministerio Público, sanciona el Poder Judicial, conduce Mininter/PNP);
      no se atribuyen al MIMP. Los registros administrativos (atenciones) no son comparables con la
      prevalencia poblacional (INEI&ndash;ENDES). Cifras en soles corrientes.
    </div>
  </section>

  <footer>
    Repositorio <b>evaluacion-mimp</b> · vista previa desplegada en GitHub Pages. Toda cifra es trazable a su
    fuente oficial con fecha de descarga. Regla del proyecto: ninguna cifra sin fuente + URL + fecha.
    Dimensión presupuestal: MEF Datos Abiertos, pliego 039, 2017&ndash;2025.
  </footer>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
const DASH = /*__DATA__*/;
const css = v => getComputedStyle(document.body).getPropertyValue(v).trim();
const SER = ['--s1','--s2','--s3','--s4','--s5','--s6','--s7','--s8'];
const M = x => x/1e6;
const fmtM = x => 'S/ ' + (Math.round(x/1e5)/10).toLocaleString('es-PE') + ' M';
const anios = DASH.meta.periodo;
let charts = [];
function baseOpts(extra){
  const ink=css('--ink'), ink2=css('--ink-2'), line=css('--line');
  return Object.assign({responsive:true,maintainAspectRatio:false,
    interaction:{mode:'index',intersect:false},
    plugins:{legend:{labels:{color:ink2,boxWidth:12,boxHeight:12,usePointStyle:true,font:{family:'Public Sans',size:12}}},
      tooltip:{backgroundColor:css('--panel'),titleColor:ink,bodyColor:ink2,borderColor:line,borderWidth:1,padding:10,usePointStyle:true,
        callbacks:{label:c=>` ${c.dataset.label}: ${fmtM((c.parsed.y!=null?c.parsed.y:c.parsed.x)*1e6)}`}}},
    scales:{x:{grid:{display:false},ticks:{color:ink2,font:{size:12}}},
      y:{grid:{color:line},ticks:{color:ink2,font:{size:12},callback:v=>v.toLocaleString('es-PE')},
         title:{display:true,text:'Millones S/',color:css('--muted'),font:{size:11}}}}}, extra||{});
}
const sc = i => css(SER[i%8]);
function build(){
  charts.forEach(c=>c.destroy()); charts=[];
  const S=DASH.serie_anual, pN=S[S.length-1], p0=S[0];
  const crecPIA=(pN.pia/p0.pia-1)*100, ejecProm=S.reduce((a,b)=>a+b.ejecucion_pct,0)/S.length;
  document.getElementById('kpis').innerHTML=[
    ['PIA '+pN.anio,fmtM(pN.pia),'inicial de apertura'],
    ['PIM '+pN.anio,fmtM(pN.pim),'presupuesto modificado'],
    ['Ejecución '+pN.anio,pN.ejecucion_pct.toFixed(1)+'%','<span class="k-up">devengado/PIM</span>'],
    ['Crecim. PIA '+p0.anio.slice(2)+'→'+pN.anio.slice(2),'<span class="k-up">+'+crecPIA.toFixed(0)+'%</span>','nominal, soles corrientes'],
    ['Ejecución promedio',ejecProm.toFixed(1)+'%','<span class="k-flat">alta y estable</span>'],
  ].map(k=>`<div class="kpi"><div class="k-label">${k[0]}</div><div class="k-val">${k[1]}</div><div class="k-note">${k[2]}</div></div>`).join('');

  charts.push(new Chart(c_serie,{type:'bar',data:{labels:anios,datasets:[
    {label:'PIA',data:S.map(r=>M(r.pia)),backgroundColor:sc(0),borderRadius:3},
    {label:'PIM',data:S.map(r=>M(r.pim)),backgroundColor:sc(1),borderRadius:3},
    {label:'Devengado',data:S.map(r=>M(r.devengado)),backgroundColor:sc(2),borderRadius:3}]},options:baseOpts()}));

  charts.push(new Chart(c_ejec,{type:'line',data:{labels:anios,datasets:[
    {label:'Ejecución %',data:S.map(r=>r.ejecucion_pct),borderColor:sc(2),borderWidth:2,pointRadius:4,pointBackgroundColor:sc(2),tension:.25}]},
    options:(()=>{const o=baseOpts();o.plugins.legend.display=false;o.plugins.tooltip.callbacks.label=c=>` Ejecución: ${c.parsed.y.toFixed(1)}%`;
    o.scales.y.title.text='%';o.scales.y.suggestedMin=90;o.scales.y.suggestedMax=100;o.scales.y.ticks.callback=v=>v+'%';return o;})()}));

  charts.push(new Chart(c_noejec,{type:'bar',data:{labels:anios,datasets:[
    {label:'No ejecutado',data:S.map(r=>M(r.no_ejecutado)),backgroundColor:sc(7),borderRadius:3}]},
    options:(()=>{const o=baseOpts();o.plugins.legend.display=false;return o;})()}));

  function stacked(canvas,obj){
    const ds=obj.labels.map((lab,i)=>({label:lab,data:anios.map(a=>M((obj.por_anio[a]||{})[lab]||0)),
      backgroundColor:sc(i),borderRadius:2,borderWidth:1,borderColor:css('--panel')}));
    const o=baseOpts({scales:{x:{stacked:true,grid:{display:false},ticks:{color:css('--ink-2')}},
      y:{stacked:true,grid:{color:css('--line')},ticks:{color:css('--ink-2'),callback:v=>v.toLocaleString('es-PE')},
         title:{display:true,text:'Millones S/',color:css('--muted'),font:{size:11}}}}});
    o.plugins.legend.labels.font.size=11;
    return new Chart(canvas,{type:'bar',data:{labels:anios,datasets:ds},options:o});
  }
  charts.push(stacked(c_ue,DASH.por_ue));
  charts.push(stacked(c_prog,DASH.por_programa));
  charts.push(stacked(c_gen,DASH.por_generica));
  charts.push(stacked(c_ff,DASH.por_fuente));
  charts.push(stacked(c_cat,DASH.por_categoria));

  charts.push(new Chart(c_mens,{type:'line',data:{labels:DASH.meses,datasets:anios.map((a,i)=>({
    label:a,data:DASH.mensual[a].map(M),borderColor:sc(i),borderWidth:a===anios[anios.length-1]?2.4:1.2,
    pointRadius:0,tension:.35}))},options:(()=>{const o=baseOpts();o.plugins.legend.labels.font.size=10;o.interaction.mode='nearest';return o;})()}));

  const dep=DASH.por_departamento, acc=dep.labels.map(l=>anios.reduce((s,a)=>s+((dep.por_anio[a]||{})[l]||0),0));
  charts.push(new Chart(c_dept,{type:'bar',data:{labels:dep.labels,datasets:[
    {label:'Devengado 2017–2025',data:acc.map(M),backgroundColor:sc(0),borderRadius:3}]},
    options:(()=>{const o=baseOpts({indexAxis:'y'});o.plugins.legend.display=false;
      o.scales.x={grid:{color:css('--line')},ticks:{color:css('--ink-2'),callback:v=>v.toLocaleString('es-PE')},title:{display:true,text:'Millones S/',color:css('--muted'),font:{size:11}}};
      o.scales.y={grid:{display:false},ticks:{color:css('--ink-2'),font:{size:11}}};
      o.plugins.tooltip.callbacks.label=c=>` ${fmtM(c.parsed.x*1e6)}`;return o;})()}));
}
build();
const root=document.documentElement;
document.getElementById('tgl').onclick=()=>{
  const cur=root.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
  root.setAttribute('data-theme',cur==='dark'?'light':'dark');setTimeout(build,30);};
matchMedia('(prefers-color-scheme:dark)').addEventListener('change',()=>{if(!root.getAttribute('data-theme'))build();});
</script>
</body>
</html>
"""

salida = HTML.replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False))
(DIR_ENTREGABLES / "tablero_mimp.html").write_text(salida, encoding="utf-8")
docs = RAIZ / "docs"
docs.mkdir(exist_ok=True)
(docs / "index.html").write_text(salida, encoding="utf-8")
print("→ 04_entregables/tablero_mimp.html")
print("→ docs/index.html (GitHub Pages)")
