# Reporte de fuentes — RESULTADO/IMPACTO (contexto) + POBLACIÓN (Fase 1)
Fecha de verificación: 2026-09-08.
Leyenda: ACCESIBLE = descarga automatizable; PARCIAL = descarga semiautomatizable (URL directa tras selección manual); MANUAL = no automatizable.
Regla: ninguna cifra entra sin valor+fuente+URL+fecha. Este reporte solo documenta ACCESO; no contiene cifras.

## Salvaguardas registradas (aplican a toda esta dimensión)
- **(A) Corresponsabilidad multisectorial:** feminicidios (investiga Ministerio Público, sanciona Poder Judicial), violaciones y desapariciones (conduce Mininter/PNP) son **CONTEXTO**, NO eficacia directa del MIMP.
- **(B) Registro ≠ encuesta:** los registros administrativos (atenciones/denuncias) NO son comparables ni sumables con la prevalencia poblacional de la ENDES (INEI). No presentarlos como una misma serie.
- **(C) Denominador:** para tasas por 100 000 usar la población de mujeres del INEI por año/ámbito. Documentar el denominador en `02_data_procesada/`.

## Vigencia relevante (cruzado con dimensión servicios)
`portalestadistico.aurora.gob.pe` REDIRIGE (301) a `portalestadistico.warminan.gob.pe` → confirma el rename AURORA→Warmi Ñan (DS 003-2025-MIMP). Ver `reporte_servicios.md`.

## Ficha 1 — Observatorio Nacional de la Violencia contra las Mujeres e Integrantes del Grupo Familiar
- URL: https://observatorioviolencia.pe/  (sección datos: /datos/)
- Estado: **MANUAL**. Verificado 2026-09-08.
- La raíz devuelve **HTTP 403 a bots** (WebFetch falla); con User-Agent de navegador responde 200. `/datos/` es WordPress que SOLO publica **PDF/PNG** (boletines, presentaciones), **sin CSV/XLSX/API**. Reenvía al portal estadístico Aurora/Warmi Ñan como motor primario.
- No automatizable. Procedimiento manual: abrir en navegador → sección Datos → descargar PDF/PNG → registrar URL + fecha.

## Ficha 2 — INEI · Estimaciones y proyecciones de población (denominador: mujeres)
- URL producto (gob.pe, HTTP 200): https://www.gob.pe/institucion/inei/informes-publicaciones/6855233-peru-estimaciones-y-proyecciones-de-la-poblacion-por-departamento-1995-2030
- Estado: **PARCIAL** (semiautomatizable). Boletín + anexo XLSX/PDF descargable por click.
- Rol: población de mujeres por año/departamento 1995–2030 → denominador de tasas por 100 000.
- Procedimiento: abrir la página producto → descargar el anexo XLSX → registrar URL + fecha. Una vez obtenida la URL directa del XLSX, la descarga es scriptable.

## Ficha 3 — INEI · ENDES (prevalencia de violencia contra la mujer — ENCUESTA)
- Microdatos (HTTP 200): https://proyectos.inei.gob.pe/microdatos/  — descarga módulos SPSS/CSV/STATA/DBF por selección interactiva.
- Resultados/tablas (HTTP 200): https://proyectos.inei.gob.pe/endes/  — tablas de resultados en PDF.
- Estado: **PARCIAL** (semiautomatizable: la URL directa del ZIP es scriptable, pero la selección de módulo/archivo es manual).
- Rol: prevalencia de violencia (última medición y serie), magnitud del problema. NO comparar/sumar con registros administrativos (salvaguarda B).
- Procedimiento: elegir año de la ENDES y módulo de violencia → descargar ZIP (microdato) o PDF (tabla) → registrar URL + fecha.

## Automatizable vs manual
- Nada es descarga-directa-por-API.
- Observatorio = 100% MANUAL (PDF/PNG).
- INEI población y ENDES = SEMIAUTOMATIZABLE (URL directa scriptable, selección de archivo manual).

## Ítems [NO DISPONIBLE] / pendientes (Fase 2)
- Todas las cifras (feminicidios/tentativas de contexto, prevalencia ENDES, población de mujeres) quedan `[NO DISPONIBLE]` hasta la descarga en Fase 2. Cero cifras inventadas; plantillas solo con encabezados.
- URL directa del anexo XLSX de población INEI (obtener al abrir la página producto).
- URL directa del ZIP/PDF del módulo de violencia de la ENDES (obtener en el portal de microdatos/resultados).

## Plantillas creadas (vacías) en `01_data_cruda/`
- `plantilla_feminicidios_contexto.csv`
- `plantilla_prevalencia_endes.csv`
- `plantilla_poblacion_mujeres.csv`
