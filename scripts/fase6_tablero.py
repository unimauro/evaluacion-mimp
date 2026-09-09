"""Fase 6 — Tablero de indicadores presupuestales del MIMP (HTML autocontenido).

Lee 03_analisis/presupuesto_dashboard.json (Fase 3) y escribe un tablero HTML con la
data inline y Chart.js (cdnjs). No inventa nada: solo grafica lo procesado y marca las
demás dimensiones como pendientes de Fase 2.

Uso:  python scripts/fase6_tablero.py
"""
from __future__ import annotations

import json

from config import DIR_ANALISIS, DIR_ENTREGABLES

data = json.loads((DIR_ANALISIS / "presupuesto_dashboard.json").read_text(encoding="utf-8"))

HTML = r"""<title>Presupuesto del MIMP 2019-2025</title>
<meta name="description" content="Tablero de la ejecución presupuestal del pliego 039 (MIMP), 2019-2025, con datos oficiales del MEF.">
<style>
:root{
  --surface:#fcfcfb; --panel:#ffffff; --ink:#0b0b0b; --ink-2:#52514e; --muted:#8a8880;
  --line:#e7e5df; --line-2:#d9d7cf; --accent:#1c5cab; --ground:#f3f1ec;
  --good:#008300; --warn:#eda100; --crit:#e34948;
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100; --s5:#e87ba4; --s6:#4a3aa7; --s7:#008300; --s8:#e34948;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --surface:#161615; --panel:#1f1f1d; --ink:#f7f6f2; --ink-2:#c3c2b7; --muted:#8f8d84;
  --line:#2e2e2b; --line-2:#3a3a36; --accent:#7fb0ee; --ground:#121211;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181; --s6:#9085e9; --s7:#12a012; --s8:#e66767;
}}
:root[data-theme="dark"]{
  --surface:#161615; --panel:#1f1f1d; --ink:#f7f6f2; --ink-2:#c3c2b7; --muted:#8f8d84;
  --line:#2e2e2b; --line-2:#3a3a36; --accent:#7fb0ee; --ground:#121211;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#d55181; --s6:#9085e9; --s7:#12a012; --s8:#e66767;
}
*{box-sizing:border-box}
body{margin:0;background:var(--surface);color:var(--ink);
  font-family:"Public Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:32px 24px 72px}
header.top{border-bottom:2px solid var(--ink);padding-bottom:20px;margin-bottom:8px}
.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);font-weight:700}
h1{font-family:"Fraunces",Georgia,serif;font-weight:600;font-size:clamp(30px,5vw,46px);
  line-height:1.05;margin:.25em 0 .15em;text-wrap:balance;letter-spacing:-.01em}
.sub{color:var(--ink-2);max-width:70ch;font-size:15.5px}
.src{color:var(--muted);font-size:12.5px;margin-top:10px;font-variant-numeric:tabular-nums}
.src code{background:var(--ground);padding:1px 5px;border-radius:4px;font-size:12px}

.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:26px 0 8px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.kpi .k-label{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:600}
.kpi .k-val{font-family:"Fraunces",Georgia,serif;font-size:30px;font-weight:600;margin-top:6px;
  font-variant-numeric:tabular-nums;letter-spacing:-.01em}
.kpi .k-note{font-size:12.5px;color:var(--ink-2);margin-top:3px}
.k-up{color:var(--good)} .k-flat{color:var(--warn)}

section{margin-top:40px}
h2{font-family:"Fraunces",Georgia,serif;font-weight:600;font-size:22px;margin:0 0 4px;letter-spacing:-.01em}
.lead{color:var(--ink-2);font-size:14px;margin:0 0 18px;max-width:78ch}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:18px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 18px 14px}
.card h3{font-size:14.5px;font-weight:700;margin:0 0 2px}
.card p.cap{font-size:12.5px;color:var(--muted);margin:0 0 12px}
.chart-box{position:relative;height:300px}
.chart-box.tall{height:360px}
.full{grid-column:1/-1}

.note{background:var(--ground);border:1px solid var(--line);border-left:3px solid var(--warn);
  border-radius:10px;padding:14px 16px;font-size:13.5px;color:var(--ink-2)}
.note b{color:var(--ink)}
.pending{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:14px}
.pend{border:1px dashed var(--line-2);border-radius:10px;padding:13px 15px;background:var(--panel)}
.pend .st{font-size:11px;text-transform:uppercase;letter-spacing:.08em;font-weight:700;color:var(--muted)}
.pend h4{margin:5px 0 4px;font-size:14px}
.pend p{margin:0;font-size:12.5px;color:var(--ink-2)}
footer{margin-top:52px;border-top:1px solid var(--line);padding-top:18px;color:var(--muted);font-size:12.5px}
.toggle{position:fixed;top:14px;right:14px;background:var(--panel);border:1px solid var(--line-2);
  color:var(--ink-2);border-radius:20px;padding:6px 13px;font-size:12.5px;cursor:pointer;font-family:inherit}
@media (max-width:640px){.wrap{padding:22px 16px 56px}}
</style>

<button class="toggle" id="tgl" aria-label="Cambiar tema">Tema</button>
<div class="wrap">
  <header class="top">
    <div class="eyebrow">Evaluación de la gestión · Pliego 039</div>
    <h1>Presupuesto del MIMP, 2019&ndash;2025</h1>
    <p class="sub">Ejecución presupuestal del Ministerio de la Mujer y Poblaciones Vulnerables
      a partir de datos abiertos oficiales del MEF. Dimensión presupuestal de la evaluación;
      las demás dimensiones se recogen en fases posteriores.</p>
    <p class="src">Fuente: MEF &mdash; Datos Abiertos, &laquo;Presupuesto y Ejecución de Gasto (Devengado)&raquo;,
      CSV anual, pliego <code>039</code>. Descarga: <code>2026-09-08</code>. Soles corrientes.</p>
  </header>

  <div class="kpis" id="kpis"></div>

  <section>
    <h2>Presupuesto y ejecución</h2>
    <p class="lead">PIA (presupuesto inicial), PIM (modificado) y devengado por año, con el porcentaje
      de ejecución (devengado/PIM) y el monto no ejecutado.</p>
    <div class="grid">
      <div class="card full"><h3>PIA · PIM · Devengado por año</h3>
        <p class="cap">Millones de soles corrientes</p><div class="chart-box tall"><canvas id="c_serie"></canvas></div></div>
      <div class="card"><h3>Ejecución presupuestal</h3>
        <p class="cap">Devengado / PIM (%)</p><div class="chart-box"><canvas id="c_ejec"></canvas></div></div>
      <div class="card"><h3>Presupuesto no ejecutado</h3>
        <p class="cap">PIM − Devengado (millones S/)</p><div class="chart-box"><canvas id="c_noejec"></canvas></div></div>
    </div>
  </section>

  <section>
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

  <section>
    <h2>Distribución territorial del gasto</h2>
    <p class="lead">Devengado acumulado 2019&ndash;2025 por departamento (según departamento de la meta).
      Insumo para analizar brechas de cobertura frente a la incidencia (dimensión pendiente).</p>
    <div class="grid"><div class="card full"><h3>Devengado por departamento</h3>
      <p class="cap">Acumulado del periodo, millones S/ (top 15)</p>
      <div class="chart-box" style="height:440px"><canvas id="c_dept"></canvas></div></div></div>
  </section>

  <section>
    <h2>Salvaguardas metodológicas</h2>
    <div class="note">
      <b>Contribución, no atribución.</b> Este tablero mide la <b>eficacia presupuestal propia</b> del MIMP
      (cuánto recibe, cuánto ejecuta y en qué). Los feminicidios, violaciones y desapariciones son
      <b>contexto de corresponsabilidad multisectorial</b> (investiga el Ministerio Público, sanciona el Poder
      Judicial, conduce Mininter/PNP) y <b>no</b> se atribuyen al MIMP. Los registros administrativos (atenciones)
      no son comparables con la prevalencia poblacional (INEI&ndash;ENDES). Cifras en soles corrientes (sin ajuste por inflación).
    </div>
    <div class="pending">
      <div class="pend"><div class="st">Fase 2 · pendiente</div><h4>Producción de servicios</h4><p>Atenciones CEM, Línea 100, SAU/SAM. Portal Warmi Ñan (XLSX vía índice de boletines).</p></div>
      <div class="pend"><div class="st">Fase 2 · pendiente</div><h4>Impacto (contexto)</h4><p>Feminicidios/tentativas y prevalencia ENDES. Observatorio e INEI (descarga semi-manual).</p></div>
      <div class="pend"><div class="st">Fase 2 · pendiente</div><h4>Cobertura territorial</h4><p>N.º de CEM (24h/regular) por región cruzado con incidencia.</p></div>
      <div class="pend"><div class="st">Fase 1 · pista</div><h4>Gestión institucional</h4><p>~13 titulares en ~6 años (rotación); confirmar con Resoluciones Supremas.</p></div>
    </div>
  </section>

  <footer>
    Tablero reproducible del repositorio <b>evaluacion-mimp</b> · dimensión presupuestal (Fases 2&ndash;3&ndash;6).
    Todo dato es trazable a su CSV anual del MEF con fecha de descarga 2026-09-08.
    Regla del proyecto: ninguna cifra sin fuente + URL + fecha.
  </footer>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
const DASH = /*__DATA__*/;
const css = v => getComputedStyle(document.body).getPropertyValue(v).trim();
const SER = ['--s1','--s2','--s3','--s4','--s5','--s6','--s7','--s8'];
const M = x => x/1e6;                       // soles -> millones
const fmtM = x => 'S/ ' + (Math.round(x/1e5)/10).toLocaleString('es-PE') + ' M';
const anios = DASH.meta.periodo;
let charts = [];

function baseOpts(extra){
  const ink=css('--ink'), ink2=css('--ink-2'), line=css('--line');
  return Object.assign({
    responsive:true, maintainAspectRatio:false,
    interaction:{mode:'index',intersect:false},
    plugins:{
      legend:{labels:{color:ink2,boxWidth:12,boxHeight:12,usePointStyle:true,font:{family:'Public Sans',size:12}}},
      tooltip:{backgroundColor:css('--panel'),titleColor:ink,bodyColor:ink2,borderColor:line,borderWidth:1,
        padding:10,usePointStyle:true,
        callbacks:{label:c=>` ${c.dataset.label}: ${fmtM(c.parsed.y!=null?c.parsed.y*1e6:c.parsed.x*1e6)}`}}
    },
    scales:{
      x:{grid:{display:false},ticks:{color:ink2,font:{size:12}}},
      y:{grid:{color:line},ticks:{color:ink2,font:{size:12},callback:v=>v.toLocaleString('es-PE')},
         title:{display:true,text:'Millones S/',color:css('--muted'),font:{size:11}}}
    }
  }, extra||{});
}
function sc(i){return css(SER[i%8]);}

function build(){
  charts.forEach(c=>c.destroy()); charts=[];
  const S=DASH.serie_anual;

  // KPIs
  const p0=S[0], pN=S[S.length-1];
  const crecPIA=(pN.pia/p0.pia-1)*100, ejecProm=S.reduce((a,b)=>a+b.ejecucion_pct,0)/S.length;
  document.getElementById('kpis').innerHTML = [
    ['PIA '+pN.anio, fmtM(pN.pia), 'inicial de apertura'],
    ['PIM '+pN.anio, fmtM(pN.pim), 'presupuesto modificado'],
    ['Ejecución '+pN.anio, pN.ejecucion_pct.toFixed(1)+'%', '<span class="k-up">devengado/PIM</span>'],
    ['Crecim. PIA 19→'+pN.anio.slice(2), '<span class="k-up">+'+crecPIA.toFixed(0)+'%</span>', 'nominal, soles corrientes'],
    ['Ejecución promedio', ejecProm.toFixed(1)+'%', '<span class="k-flat">alta y estable</span>'],
  ].map(k=>`<div class="kpi"><div class="k-label">${k[0]}</div><div class="k-val">${k[1]}</div><div class="k-note">${k[2]}</div></div>`).join('');

  // 1. Serie PIA/PIM/Devengado
  charts.push(new Chart(c_serie,{type:'bar',data:{labels:anios,datasets:[
    {label:'PIA',data:S.map(r=>M(r.pia)),backgroundColor:sc(0),borderRadius:3},
    {label:'PIM',data:S.map(r=>M(r.pim)),backgroundColor:sc(1),borderRadius:3},
    {label:'Devengado',data:S.map(r=>M(r.devengado)),backgroundColor:sc(2),borderRadius:3},
  ]},options:baseOpts()}));

  // 2. Ejecución %
  charts.push(new Chart(c_ejec,{type:'line',data:{labels:anios,datasets:[
    {label:'Ejecución %',data:S.map(r=>r.ejecucion_pct),borderColor:sc(2),backgroundColor:'transparent',
     borderWidth:2,pointRadius:4,pointBackgroundColor:sc(2),tension:.25}
  ]},options:(()=>{const o=baseOpts();o.plugins.tooltip.callbacks.label=c=>` Ejecución: ${c.parsed.y.toFixed(1)}%`;
     o.plugins.legend.display=false;o.scales.y.title.text='%';o.scales.y.suggestedMin=90;o.scales.y.suggestedMax=100;
     o.scales.y.ticks.callback=v=>v+'%';return o;})()}));

  // 3. No ejecutado
  charts.push(new Chart(c_noejec,{type:'bar',data:{labels:anios,datasets:[
    {label:'No ejecutado',data:S.map(r=>M(r.no_ejecutado)),backgroundColor:sc(7),borderRadius:3}
  ]},options:(()=>{const o=baseOpts();o.plugins.legend.display=false;return o;})()}));

  // Helper apiladas por categoría {labels, por_anio}
  function stacked(canvas,obj){
    const ds=obj.labels.map((lab,i)=>({label:lab,
      data:anios.map(a=>M((obj.por_anio[a]||{})[lab]||0)),
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

  // Estacionalidad mensual (una línea por año)
  charts.push(new Chart(c_mens,{type:'line',data:{labels:DASH.meses,datasets:anios.map((a,i)=>({
    label:a,data:DASH.mensual[a].map(M),borderColor:sc(i),backgroundColor:'transparent',
    borderWidth:a===anios[anios.length-1]?2.4:1.4,pointRadius:0,tension:.35}))},
    options:(()=>{const o=baseOpts();o.plugins.legend.labels.font.size=11;o.interaction.mode='nearest';return o;})()}));

  // Territorial (barras horizontales, acumulado)
  const dep=DASH.por_departamento, acc=dep.labels.map(l=>anios.reduce((s,a)=>s+((dep.por_anio[a]||{})[l]||0),0));
  charts.push(new Chart(c_dept,{type:'bar',data:{labels:dep.labels,datasets:[
    {label:'Devengado 2019–2025',data:acc.map(M),backgroundColor:sc(0),borderRadius:3}]},
    options:(()=>{const o=baseOpts({indexAxis:'y'});o.plugins.legend.display=false;
      o.scales.x={grid:{color:css('--line')},ticks:{color:css('--ink-2'),callback:v=>v.toLocaleString('es-PE')},
        title:{display:true,text:'Millones S/',color:css('--muted'),font:{size:11}}};
      o.scales.y={grid:{display:false},ticks:{color:css('--ink-2'),font:{size:11}}};
      o.plugins.tooltip.callbacks.label=c=>` ${fmtM(c.parsed.x*1e6)}`;return o;})()}));
}
build();

// Theme toggle
const root=document.documentElement;
document.getElementById('tgl').onclick=()=>{
  const cur=root.getAttribute('data-theme')
    || (matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
  root.setAttribute('data-theme',cur==='dark'?'light':'dark');
  setTimeout(build,30);
};
matchMedia('(prefers-color-scheme:dark)').addEventListener('change',()=>{if(!root.getAttribute('data-theme'))build();});
</script>
"""

out = DIR_ENTREGABLES / "tablero_mimp.html"
out.write_text(HTML.replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False)), encoding="utf-8")
print(f"→ {out}")
