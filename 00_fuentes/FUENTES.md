# Estado de fuentes (Fase 1 — Reconocimiento) — CONSOLIDADO

Verificación real: **2026-09-08**. Ninguna cifra entra al análisis sin
**valor + fuente + URL exacta + fecha de descarga**.

Leyenda: `ACCESIBLE` (descarga automatizable) · `PARCIAL` (semiautomatizable / índice
o tablero) · `MANUAL` (descarga manual) · `PISTA` (secundaria, confirmar contra primaria).

Fichas detalladas por dimensión:
- [`reporte_presupuesto.md`](reporte_presupuesto.md) — presupuestal (MEF).
- [`reporte_servicios.md`](reporte_servicios.md) — producción de servicios y calidad (Warmi Ñan, Defensoría).
- [`reporte_violencia_poblacion.md`](reporte_violencia_poblacion.md) — impacto/contexto y población (Observatorio, INEI).
- [`reporte_institucional.md`](reporte_institucional.md) — gestión institucional (Transparencia, titulares, RENIPED).

---

## 🔴 Dos correcciones críticas al encargo (verificadas)

1. **El dominio AURORA sí cambió.** La nota del spec ("el portal conservaba el dominio
   `aurora.gob.pe`") quedó **desactualizada**: hoy `*.aurora.gob.pe` redirige **301** a
   `*.warminan.gob.pe` y el TLS de aurora ya no valida. Rebranding oficializado por
   **DS 003-2025-MIMP** (~2-may-2025). → **Usar `*.warminan.gob.pe` en todo el proyecto.**
2. **RENADESPPLE ≠ desapariciones.** RENADESPPLE es el registro de detenidos/sentenciados
   del **Ministerio Público**, no de Mininter/PNP. El registro real de personas
   **desaparecidas** es **RENIPED** (PNP). → **Usar RENIPED** como contexto. (Sigue siendo
   contexto multisectorial, no eficacia del MIMP.)

---

## Tabla de estado por fuente

| Fuente | Dimensión | URL vigente | Estado | ¿Automatizable? |
|---|---|---|---|---|
| MEF Datos Abiertos «Devengado Mensual» | Presupuesto | fs.datosabiertos.mef.gob.pe/datastorefiles/ | **ACCESIBLE** | Sí (CSV anual, filtrar PLIEGO='039') |
| MEF Consulta Amigable web | Presupuesto (verif.) | apps5.mineco.gob.pe/transparencia/ | PARCIAL | No (ASP.NET/Incapsula) → manual |
| MEF Ley de Presupuesto | Denominador nacional | mef.gob.pe | MANUAL | Alternativa: sumar MONTO_PIA del CSV |
| Portal Estadístico **Warmi Ñan** | Servicios | portalestadistico.warminan.gob.pe | PARCIAL | Semi (XLSX vía índice de boletines) |
| Repositorio **Warmi Ñan** | Servicios/docs | repositorio.warminan.gob.pe | MANUAL | No (SPA React) |
| Defensoría del Pueblo | Calidad | defensoria.gob.pe | **ACCESIBLE** | Sí (PDF directo: Inf. 255/2025, 179/2018) |
| Observatorio Nacional de la Violencia | Impacto/contexto | observatorioviolencia.pe | MANUAL | No (403 a bots; solo PDF/PNG) |
| INEI · Proyecciones de población | Denominador (mujeres) | gob.pe/institucion/inei | PARCIAL | Semi (anexo XLSX por click) |
| INEI · ENDES | Prevalencia (encuesta) | proyectos.inei.gob.pe/endes · /microdatos | PARCIAL | Semi (ZIP/PDF por selección) |
| PTE Transparencia — MIMP (id 142) | Institucional | transparencia.gob.pe | PARCIAL | No (ASP.NET) → manual |
| Titulares MIMP 2019–2025 | Institucional | El Peruano (RS) / gob.pe/mimp | PISTA | Confirmar con RS |
| **RENIPED** (ex "RENADESPPLE" del spec) | Contexto (desapar.) | desaparecidosenperu.policia.gob.pe | MANUAL | No (SSL no valida) |

## Verificación de vigencia AURORA → Warmi Ñan

- [x] Confirmado: dominio migrado a `warminan.gob.pe` (301 desde aurora). DS 003-2025-MIMP.
- [x] Estructura/funciones: prensa indica que se mantiene. `SUPUESTO`: serie estadística
  continua/comparable antes y después; confirmar en "Metodología" del portal.
- [ ] `[NO DISPONIBLE]` — texto íntegro del DS 003-2025-MIMP (descargar PDF de la norma).

## Principales `[NO DISPONIBLE]` / pendientes de Fase 2

- **Presupuesto:** descarga efectiva de los CSV MEF 2019–2025 (~2–2.6 GB c/u, filtrar
  PLIEGO='039'); N.º de Ley y monto del PIA nacional 2020/2022/2023/2024 (o derivarlo del CSV).
- **Servicios:** N.º de CEM total/24h/regular por año; mapeo tabla-numerada→indicador en
  boletines históricos; inventario del Repositorio (SPA, navegador).
- **Impacto/población:** cifras de prevalencia ENDES, población de mujeres y feminicidios de
  contexto (todo `[NO DISPONIBLE]` hasta descargar). URLs directas de anexos INEI.
- **Institucional:** Resoluciones Supremas de designación/cese de cada titular; descargas del
  PTE (presupuesto/personal/inversiones); estadísticas de RENIPED (consulta manual).

## Plantillas vacías listas en `01_data_cruda/` (11, solo encabezados)

`plantilla_presupuesto_mimp.csv` · `plantilla_presupuesto_nacional.csv` ·
`plantilla_atenciones_cem.csv` · `plantilla_linea100_sau_cai.csv` ·
`plantilla_cem_infraestructura.csv` · `plantilla_feminicidios_contexto.csv` ·
`plantilla_prevalencia_endes.csv` · `plantilla_poblacion_mujeres.csv` ·
`plantilla_titulares_mimp.csv` · `plantilla_inversiones_mimp.csv` · `plantilla_rrhh_mimp.csv`
