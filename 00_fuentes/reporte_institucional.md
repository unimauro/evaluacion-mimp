# Reporte de fuentes — Gestión institucional (Fase 1)

Verificación: **2026-09-08**. Dimensión 6 (gestión institucional).

> ⚠️ Los indicadores de desapariciones son **CONTEXTO multisectorial (Mininter/PNP)**,
> no eficacia directa del MIMP.

---

## 🔴 HALLAZGO CRÍTICO — corrección al encargo: RENADESPPLE ≠ desapariciones

El spec asocia **RENADESPPLE** a "registro de personas desaparecidas (Mininter/PNP)".
**Es incorrecto.** Verificado:

- **RENADESPPLE** = Registro Nacional de Detenidos y Sentenciados a Pena Privativa de
  Libertad Efectiva → personas **detenidas/sentenciadas**, administrado por el
  **Ministerio Público – Fiscalía de la Nación** (NO Mininter/PNP, NO trata desapariciones).
  - Presentación: https://www.mpfn.gob.pe/renadespple/presentacion/
  - Consulta: https://portal.mpfn.gob.pe/consultarena
- El registro de personas **DESAPARECIDAS** es **RENIPED** (PNP / Mininter):
  - https://desaparecidosenperu.policia.gob.pe/Desaparecidos/reniped
- Adicional relacionado: **RENADE** (Minjus, víctimas de violencia 1980–2000):
  - https://renade.minjus.gob.pe

**Recomendación:** usar **RENIPED** como fuente de contexto de desapariciones. Sigue
siendo CONTEXTO multisectorial (Mininter/PNP), no medida de eficacia del MIMP.

---

## Fuente A — Portal de Transparencia Estándar (PTE) — MIMP

- Estado: **PARCIAL** (tratar como MANUAL para descarga).
- Portal raíz: https://www.transparencia.gob.pe — ACCESIBLE.
- Página entidad MIMP (id_entidad 142), verificada:
  https://www.transparencia.gob.pe/enlaces/pte_transparencia_enlaces.aspx?id_entidad=142
- Secciones disponibles (9): Datos generales · Planeamiento y organización ·
  Presupuesto · Proyectos de inversión e Infobras · Personal · Contratación de bienes
  y servicios · Actividades oficiales · Acceso a la información · Registro de Visitas.
- ¿Automatizable? Probablemente **NO** (ASP.NET/ViewState) → procedimiento MANUAL.
- Procedimiento manual: entrar a la sección → elegir año/trimestre → descargar PDF/XLSX
  → registrar URL exacta + fecha de descarga.
- Nota: para PIM/devengado a detalle usar MEF Consulta Amigable (ver `reporte_presupuesto.md`).

## Fuente B — Rotación de titulares del MIMP 2019–2025

- Estado: **PARCIAL / PISTA** (Wikipedia + prensa). **CONFIRMAR** cada fecha con la
  Resolución Suprema de designación/cese en El Peruano: https://busquedas.elperuano.pe
- Portal oficial de funcionarios (solo titular vigente; devuelve HTTP 418 anti-bot,
  abrir en navegador): https://www.gob.pe/institucion/mimp/funcionarios
- Anexo de referencia: https://es.wikipedia.org/wiki/Anexo:Ministras_de_la_Mujer_de_Per%C3%BA

Lista PISTA (columna `norma_designacion` = `[NO DISPONIBLE]` en todas hasta ubicar la RS):

| # | Titular | Inicio (pista) | Fin (pista) |
|---|---|---|---|
| 1 | Gloria Montenegro Figueroa | 11-mar-2019 | 6-ago-2020 |
| 2 | Rosario Sasieta Morales | 6-ago-2020 | 10-nov-2020 |
| 3 | Patricia Teullet Pipoli | 12-nov-2020 | 17-nov-2020 (5 días) |
| 4 | Silvia Loli Espinoza | 18-nov-2020 | 29-jul-2021 |
| 5 | Anahí Durand Guevara | 29-jul-2021 | 1-feb-2022 |
| 6 | Katy Ugarte Mamani | 1-feb-2022 | 8-feb-2022 (7 días) |
| 7 | Diana Miloslavich Túpac | 8-feb-2022 | 24-ago-2022 |
| 8 | Claudia Dávila Moscoso | 24-ago-2022 | 24-nov-2022 |
| 9 | Heidy Juárez Calle | 24-nov-2022 | 7-dic-2022 (~13 días) |
| 10 | Grecia Rojas Ortiz | 10-dic-2022 | 13-ene-2023 |
| 11 | Nancy Tolentino Gamarra | 13-ene-2023 | 1-abr-2024 |
| 12 | Ángela Hernández Cajo | 1-abr-2024 | 31-ene-2025 |
| 13 | Fanny Montellanos Carbajal | 31-ene-2025 | (continúa en 2025) |

> Lectura PRELIMINAR (a confirmar con RS): ~13 titulares en ~6 años = alta rotación /
> inestabilidad institucional; varias gestiones de días. **NO usar como cifra** hasta
> confirmar fechas con la RS de designación/cese en El Peruano.

## Fuente C — RENIPED (PNP, personas desaparecidas — CONTEXTO)

- Estado: **MANUAL**. https://desaparecidosenperu.policia.gob.pe/Desaparecidos/reniped
- El fetch automatizado **FALLA por certificado SSL no verificable** → abrir en navegador.
- RENADE (Minjus): https://renade.minjus.gob.pe/renade/public/seguimientoPublico/seguimientoPublicoMain.xhtml

---

## Plantillas creadas (vacías, solo encabezados) en `01_data_cruda/`

- `plantilla_titulares_mimp.csv`
- `plantilla_inversiones_mimp.csv`
- `plantilla_rrhh_mimp.csv`

## Resumen de estados

| Fuente | Estado | Automatizable |
|---|---|---|
| PTE Transparencia MIMP (id 142) | PARCIAL | No (manual) |
| Titulares MIMP 2019–2025 | PISTA | Confirmar con RS (El Peruano) |
| RENIPED (desaparecidos, contexto) | MANUAL | No (SSL) |
| ~~RENADESPPLE~~ | Corregido | No aplica (era error del spec) |
