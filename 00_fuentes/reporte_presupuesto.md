# Reporte de fuentes — Dimensión PRESUPUESTAL (Fase 1)

Evaluación MIMP · Pliego 039 · periodo 2019–2025. Fecha de verificación de todas las fichas: 2026-09-08.
Regla: ningún dato entra sin valor + fuente + URL exacta + fecha de descarga. Leyenda: ACCESIBLE (descarga automatizable) / PARCIAL (solo consulta interactiva) / MANUAL (descarga/confirmación manual).

## Resumen
- Fuente 1 — MEF Datos Abiertos «Presupuesto y Ejecución de Gasto – Devengado Mensual»: PIA/PIM/devengado por pliego/U.E./programa/año. Estado ACCESIBLE, automatizable (CSV anual por URL directa).
- Fuente 2 — MEF Consulta Amigable web: verificación/cruce del pliego 039. Estado PARCIAL, no automatizable (ASP.NET/ViewState + Incapsula).
- Fuente 3 — MEF Ley de Presupuesto (PIA nacional, denominador): Estado MANUAL (PDF por año; N.º de ley por confirmar). Ruta alterna recomendada: sumar MONTO_PIA de todos los pliegos del CSV de la fuente 1.

## Ficha 1 — MEF · Datos Abiertos «Devengado Mensual» (ACCESIBLE)
- Rol: PIA, PIM y devengado por PLIEGO (039=MIMP), EJECUTORA, PROGRAMA_PPTO, año.
- Portal (metadatos, CKAN): https://www.datosabiertos.gob.pe/dataset/presupuesto-y-ejecuci%C3%B3n-de-gasto-%E2%80%93-devengado-mensual
- Cobertura declarada: 2012–2026, Gob. Nacional/Regional/Local, proveniente de Consulta Amigable (metadata_modified 2026-08-04).
- Verificado 2026-09-08 vía API: https://www.datosabiertos.gob.pe/api/3/action/package_show?id=presupuesto-y-ejecuci%C3%B3n-de-gasto-%E2%80%93-devengado-mensual (HTTP 200). Descarga de cabecera probada (HTTP 206 con Range, y 200).
- URLs de descarga directa (verificadas, tamaño = Content-Length):
  - 2019: https://fs.datosabiertos.mef.gob.pe/datastorefiles/2019-Gasto-Devengado.csv (2 126 168 061 B)
  - 2020: https://fs.datosabiertos.mef.gob.pe/datastorefiles/2020-Gasto-Devengado.csv (2 423 750 562 B)
  - 2021: https://fs.datosabiertos.mef.gob.pe/datastorefiles/2021-Gasto-Devengado.csv (2 437 904 606 B)
  - 2022: https://fs.datosabiertos.mef.gob.pe/datastorefiles/2022-Gasto-Devengado.csv (2 601 021 191 B)
  - 2023: https://fs.datosabiertos.mef.gob.pe/datastorefiles/2023-Gasto-Devengado.csv (2 711 108 717 B)
  - 2024: https://fs.datosabiertos.mef.gob.pe/datastorefiles/2024-Gasto-Devengado.csv (2 767 431 498 B)
  - 2025 (mensual): https://fs.datosabiertos.mef.gob.pe/datastorefiles/2025-Gasto-Devengado-Mensual.csv (2 793 628 275 B)
  - 2025 (diario): https://fs.datosabiertos.mef.gob.pe/datastorefiles/2025-Gasto-Devengado-Diario.csv
  - Diccionario: https://fs.datosabiertos.mef.gob.pe/datastorefiles/Gasto_Devengado_Diccionario.csv
- Riesgo: cada CSV ~2.0–2.6 GB (TODOS los pliegos/niveles del Perú). Filtrar PLIEGO="039" en streaming (duckdb/csvkit/awk), no cargar entero. Soporta Range (curl -C - reanuda).
- Columnas relevantes (confirmadas con el diccionario oficial 2026-09-08): ANO_EJE; PLIEGO, PLIEGO_NOMBRE (MIMP=039); SECTOR(_NOMBRE); EJECUTORA, EJECUTORA_NOMBRE, SEC_EJEC; PROGRAMA_PPTO, PROGRAMA_PPTO_NOMBRE; MONTO_PIA; MONTO_PIM; MONTO_DEVENGADO_ENERO…_DICIEMBRE; MONTO_DEVENGADO_ANUAL (usar como devengado); además MONTO_CERTIFICADO_ANUAL/COMPROMETIDO_ANUAL/GIRADO_ANUAL, función/meta/geografía. CSV con BOM UTF-8, campos entre comillas dobles.
- Procedimiento: por cada año 2019–2025 descargar el CSV → filtrar PLIEGO='039' (ej. DuckDB: SELECT ANO_EJE,PLIEGO,EJECUTORA_NOMBRE,PROGRAMA_PPTO_NOMBRE,SUM(MONTO_PIA),SUM(MONTO_PIM),SUM(MONTO_DEVENGADO_ANUAL) FROM read_csv_auto('AAAA-Gasto-Devengado.csv') WHERE PLIEGO='039' GROUP BY 1,2,3,4) → volcar a plantilla_presupuesto_mimp.csv mapeando anio←ANO_EJE, pliego←PLIEGO, unidad_ejecutora←EJECUTORA_NOMBRE, programa_presupuestal←PROGRAMA_PPTO_NOMBRE, pia←MONTO_PIA, pim←MONTO_PIM, devengado←MONTO_DEVENGADO_ANUAL, fuente="MEF Datos Abiertos – Devengado", url=<URL del año>, fecha_descarga=<real>.
- Vigencia/riesgo: en CKAN figura private:true pero los archivos fs.datosabiertos.mef.gob.pe descargan anónimamente (verificado); si cambia, usar Consulta Amigable web. 2025/2026 tienen versión Mensual y Diaria (usar Mensual para serie anual); 2026 en curso, fuera del periodo. SUPUESTO: confirmar PLIEGO_NOMBRE=MIMP en las filas filtradas.

## Ficha 2 — MEF · Consulta Amigable web (PARCIAL)
- URL: https://apps5.mineco.gob.pe/transparencia/ · ref: https://www.mef.gob.pe/es/seguimiento-de-la-ejecucion-presupuestal-consulta-amigable
- Verificado 2026-09-08 (WebFetch): frameset (Navegar.aspx), ASP.NET/ViewState, Incapsula anti-bot; no expone filtros ni CSV/API a cliente no-navegador. No automatizable.
- Procedimiento manual: 1) abrir portal; 2) entrar a Consulta Amigable; 3) elegir Año (2019…2025); 4) Nivel de Gobierno → E: Gobierno Nacional; 5) Sector del MIMP → Pliego → 039: M. DE LA MUJER Y POBLACIONES VULNERABLES; 6) anotar PIA, PIM, Devengado y % avance; 7) desagregar por Unidad Ejecutora/Programa; 8) repetir por año (botón «Exportar» a Excel dentro de la sesión sirve de respaldo).
- Riesgo: Incapsula puede bloquear scraping; usar solo manualmente. Debe coincidir con Ficha 1 (mismo origen); discrepancia = revisar fecha de corte.

## Ficha 3 — MEF · Ley de Presupuesto del Sector Público (MANUAL) — denominador PIA nacional
- Portal: https://www.mef.gob.pe (Normatividad → Leyes de presupuesto). Verificado 2026-09-08 (WebSearch).
- URLs localizadas (confirmar N.º de ley antes de citar):
  - 2019 Ley N.° 30879: https://www.mef.gob.pe/es/normatividad-sp-9867/por-instrumento/leyes/18641-ley-n-30879-30880-y-30881-1/file
  - 2021 Ley N.° 31084: https://www.mef.gob.pe/es/normatividad-sp-9867/por-instrumento/leyes/24383-ley-n-31084-1/file
  - 2025 (PDF MEF): https://www.mef.gob.pe/contenidos/presu_publ/sectr_publ/proy_2025/PL_Presupuesto_SP_2025.pdf
  - 2020, 2022, 2023, 2024: [NO DISPONIBLE — confirmar N.º de Ley y URL en https://www.mef.gob.pe/es/normatividad-sp-9867/por-instrumento/leyes]
- Cifras de búsqueda NO cargadas al CSV (requieren confirmación en la norma): 2025 ≈ S/ 251 801 millones (Infobae 2024-12-01, [confirmar]); 2021 S/ 183 029 770 158 (texto Ley 31084, [confirmar]); resto [NO DISPONIBLE].
- Nota metodológica RECOMENDADA — SUPUESTO: derivar pia_nacional del MISMO CSV de la Ficha 1 sumando MONTO_PIA sobre todos los pliegos del año (SELECT ANO_EJE, SUM(MONTO_PIA) GROUP BY 1). Denominador plenamente trazable y consistente con el numerador MIMP. Advertencia: puede diferir levemente del monto nominal de la Ley (reserva de contingencia/servicio de deuda). Documentar la definición elegida en 02_data_procesada.

## Pendientes / [NO DISPONIBLE]
1) [NO DISPONIBLE] N.º de Ley y URL del PIA nacional 2020/2022/2023/2024 (alternativa: suma MONTO_PIA del CSV Ficha 1).
2) [NO DISPONIBLE] Confirmación de montos nominales PIA nacional por año en texto oficial.
3) Descarga efectiva de CSV 2019–2025 (pendiente; ~2–2.6 GB c/u, filtrar PLIEGO='039'). Plantillas quedan vacías.
4) SUPUESTO a confirmar: PLIEGO='039' ⇒ PLIEGO_NOMBRE = MIMP.
