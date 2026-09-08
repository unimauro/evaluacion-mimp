# Reporte de fuentes — Dimensión COBERTURA Y PRODUCCIÓN DE SERVICIOS (Fase 1)
Fecha de verificación de todas las fichas: 2026-09-08.
Leyenda: ACCESIBLE = descarga automatizable; PARCIAL = descarga parcial/navegar índice o tablero; MANUAL = descarga manual no automatizable de forma fiable.
Regla: ninguna cifra entra sin valor+fuente+URL+fecha. Este reporte solo documenta ACCESO; no contiene cifras.

## 0. VERIFICACIÓN CRÍTICA DE VIGENCIA — AURORA → "Warmi Ñan"
Resultado: la nota conocida quedó PARCIALMENTE DESACTUALIZADA. El dominio SÍ cambió.
- DS 003-2025-MIMP, publicado ~2 mayo 2025. Programa = "...Warmi Ñan" (quechua "camino de la mujer").
  Fuente prensa oficial: https://www.elperuano.pe/noticia/269616--nueva-identidad-legal-aurora-es-ahora-warmi-nan-lee-el-impacto-del-ds-003-2025-mimp (2026-09-08).
  Confirmación normativa secundaria: https://iuslatin.pe/mimp-programa-aurora-cambia-de-nombre-a-warmi-nan-decreto-supremo-n-o-003-2025-mimp/ (2026-09-08).
  [NO DISPONIBLE — texto íntegro del DS 003-2025-MIMP: requiere descarga manual del PDF de la norma].
- Estructura/funciones: prensa indica "se mantiene la estructura operativa". Sin evidencia de cambio metodológico. SUPUESTO: la serie estadística es continua/comparable antes y después del rebranding; confirmar en sección "Metodología" del portal.
- CAMBIO DE DOMINIO (verificado hoy, contradice la nota previa): aurora.gob.pe YA NO se conserva. Al 2026-09-08:
  https://portalestadistico.aurora.gob.pe/ → 301 → https://portalestadistico.warminan.gob.pe/
  https://repositorio.aurora.gob.pe/ → 301 → https://repositorio.warminan.gob.pe/
  https://www.aurora.gob.pe/ → 301 → https://www.warminan.gob.pe/ (→ gob.pe/warmiñan)
  Verificado con curl -I (Server: nginx/1.22.1, Location a warminan). El TLS de *.aurora.gob.pe ya no valida.
  Implicancia: actualizar TODAS las URLs a *.warminan.gob.pe; las aurora son legadas (riesgo de caída).

## 1. Portal Estadístico Warmi Ñan (ex Portal Estadístico Aurora)
URL vigente: https://portalestadistico.warminan.gob.pe/  · URL legada (redirige): https://portalestadistico.aurora.gob.pe/
Estado: PARCIAL. Provee: casos/atenciones CEM y Familia (región, tipo de violencia, sexo, grupo edad), Línea 100, Chat 100, SAU/SAM, CAI (casos y acciones), SAR (rural), casos con características de feminicidio y de tentativa, acciones preventivas. Últimos datos observados: ene–jul 2026. Verificado 2026-09-08.
Cómo se descarga (probado HTTP 200 + XLSX válido): cada página de indicador (/cem-casos-nacional/, /cem-casos-departamento/, /chat-100-consultas/, /casos-con-caracteristicas-de-feminicidio/, etc.) muestra un tablero Tableau embebido (iframe) NO scrapeable como tabla; los datos se publican como XLSX por URL directa en dos rutas:
1) Mensuales consolidados: .../wp-content/uploads/AAAA/MM/<Nombre>-<mes>.xlsx. Ejemplos verificados 2026-09-08:
   CEM: https://portalestadistico.warminan.gob.pe/wp-content/uploads/2026/08/Casos-del-Centro-Emergencia-Mujer-y-Familia-julio.xlsx (200, 260KB, Excel válido)
   Línea 100: https://portalestadistico.warminan.gob.pe/wp-content/uploads/2026/08/Linea-100-julio.xlsx
   Feminicidio: https://portalestadistico.warminan.gob.pe/wp-content/uploads/2026/08/Feminicidio-julio.xlsx
   Tentativa: https://portalestadistico.warminan.gob.pe/wp-content/uploads/2026/08/Tentativa-julio.xlsx
   SAM (ex SAU): https://portalestadistico.warminan.gob.pe/wp-content/uploads/2026/08/SAM-julio.xlsx
   Acciones preventivas: https://portalestadistico.warminan.gob.pe/wp-content/uploads/2026/08/AP-julio.xlsx
2) Tablas de boletín: .../wp-content/uploads/boletin/<Año>/<Mes>/paginas/<n.n.n>.xlsx. Verificados:
   2026/Julio 4.1.1: https://portalestadistico.warminan.gob.pe/wp-content/uploads/boletin/2026/Julio/paginas/4.1.1.xlsx (200, 24KB)
   2024/Diciembre 4.1.1: https://portalestadistico.warminan.gob.pe/wp-content/uploads/boletin/2024/Diciembre/paginas/4.1.1.xlsx (200, 24KB) — confirma boletines históricos.
Serie histórica 2019–2025: índice en https://portalestadistico.warminan.gob.pe/boletines-estadisticos/ (y /boletines-regionales/, /datos-historicos/, /banco-de-datos/, /compendios-estadisticos/). Años 2019–2025 presentes en el HTML del índice.
ADVERTENCIA automatización: numeración de tablas NO estable entre años/meses (2025/Diciembre usa 1.1, 2.10, 2.13…; 2026/Julio usa 4.1.1). NO adivinar URLs por patrón (verificado: boletin/2021/Diciembre/paginas/4.1.1.xlsx → 404; boletin/2019/... → 404). Scrapear el índice y seguir los href .xlsx.
Automatizable: descargar cada .xlsx una vez conocida su URL (curl/requests). Recolección: GET a boletines-estadisticos/ y cada boletín → extraer href .xlsx → descargar con fecha en el nombre. Manual/verificación: mapear qué tabla numerada = qué indicador abriendo el XLSX (la URL solo trae un código como 4.1.1).
Procedimiento manual: 1) abrir portalestadistico.warminan.gob.pe; 2) Datos → Boletines estadísticos (o Datos históricos/Banco de datos); 3) elegir año (2019…2025) y mes (para serie anual usar Diciembre, que acumula); 4) descargar el .xlsx de cada tabla; 5) guardar en 01_data_cruda/ como warminan_<indicador>_<año>_desc2026-09-08.xlsx + anotar URL; 6) para indicador solo-Tableau usar botón Download→Crosstab/Data del iframe.
Gaps: N.º de CEM total/24h/regular = [NO DISPONIBLE — sin XLSX directo el 2026-09-08; buscar en boletín anual "cobertura de servicios" o directorio institucional]. Feminicidios del portal = registro administrativo del programa, NO cifra oficial MP/PJ → contexto de corresponsabilidad, no eficacia MIMP; no sumar con MP/PNP.

## 2. Repositorio Warmi Ñan (ex Repositorio Aurora)
URL vigente: https://repositorio.warminan.gob.pe/ · legada: https://repositorio.aurora.gob.pe/ (301). Estado: MANUAL. Verificado 2026-09-08.
El HTML es un cascarón SPA React (<div id="root"> + /assets/index-*.js; <title>Repositorio Nacional Warmi Ñan</title>); el listado se carga por JS → curl/WebFetch no ven archivos. Requiere navegador (o descubrir su API JS). Procedimiento: abrir en navegador, usar buscador, filtrar por tipo/año, descargar PDF/XLSX, registrar URL+fecha. [NO DISPONIBLE — inventario de documentos: requiere navegación manual].

## 3. Defensoría del Pueblo — supervisión de CEM (dimensión CALIDAD)
URL base: https://www.defensoria.gob.pe. Estado: ACCESIBLE (PDFs con descarga directa). Verificado 2026-09-08.
- Informe Defensorial N.º 255 (2025): "Informe de seguimiento a las recomendaciones sobre la Estrategia Nacional de Prevención de la Violencia de Género contra las Mujeres 'Mujeres libres de violencia'". Publicado 30-09-2025. Incluye supervisión a CEM + establecimientos de salud en Apurímac, San Martín y Cusco; 100 usuarias. Ficha: https://www.defensoria.gob.pe/informes/informe-defensorial-n-255/  PDF (según ficha): https://www.defensoria.gob.pe/wp-content/uploads/2025/09/Informe-Defensorial-n.°255.pdf [VERIFICAR DESCARGA — URL con caracteres especiales °/ñ; confirmar URL codificada].
- Informe Defensorial N.º 179 (2018): "Centros Emergencia Mujer: supervisión a nivel nacional 2018" (326 CEM, oct–nov 2018). PDF: https://www.defensoria.gob.pe/wp-content/uploads/2018/12/Informe-Defensorial-Nº-179-Centros-Emergencia-Mujer-supervisión-a-nivel-nacional-2018.pdf
Naturaleza: cualitativo/supervisión (horarios, infraestructura, suficiencia de personal, accesibilidad) → insumo dimensión calidad, no conteo de producción. Procedimiento: descargar PDFs directo; para más informes usar buscador https://www.defensoria.gob.pe/documentos/ filtrando "Centros Emergencia Mujer".

## Resumen de accesibilidad
| Fuente | URL vigente | Estado | Descarga | Serie 2019–2025 |
|---|---|---|---|---|
| Portal Estadístico Warmi Ñan | portalestadistico.warminan.gob.pe | PARCIAL | XLSX por tabla (Tableau embebido) | Sí, vía índice boletines-estadisticos (numeración no estable → scrapear índice) |
| Repositorio Warmi Ñan | repositorio.warminan.gob.pe | MANUAL | SPA React (JS) | Requiere navegador |
| Defensoría del Pueblo (CEM) | defensoria.gob.pe | ACCESIBLE | PDF directo | Informes puntuales (2018, 2025) |

## Ítems [NO DISPONIBLE] / pendientes manuales
1. Texto íntegro del DS 003-2025-MIMP (PDF norma).
2. N.º de CEM total/24h/regular por año (sin XLSX directo; boletín anual o directorio institucional).
3. Mapeo tabla-numerada→indicador en boletines históricos.
4. Inventario del Repositorio Warmi Ñan (SPA; navegación manual).
5. URL codificada exacta del PDF del Informe Defensorial N.º 255.
