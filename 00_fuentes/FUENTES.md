# Estado de fuentes (Fase 1 — Reconocimiento)

Registro del estado de cada fuente oficial. **Ninguna cifra entra al análisis sin
valor + fuente + URL exacta + fecha de descarga.**

Leyenda de estado:
- `ACCESIBLE` — responde y ofrece descarga (CSV/XLSX/API) automatizable.
- `PARCIAL` — responde pero solo consulta interactiva / descarga limitada.
- `MANUAL` — requiere descarga manual paso a paso (documentar procedimiento + plantilla vacía).
- `SIN VERIFICAR` — aún no comprobada.

> Estado inicial: todas las fuentes están **SIN VERIFICAR**. Comprobar en la Fase 1
> antes de cualquier análisis.

---

## Verificación previa obligatoria

- [ ] **AURORA → "Warmi Ñan"** (DS 003-2025-MIMP, 2025): confirmar que el portal
  estadístico sigue en `aurora.gob.pe` y que no cambió estructura/metodología.
  → Estado: `[NO DISPONIBLE — verificar]`

---

## Ficha por fuente

### 1. MEF – Consulta Amigable
- URL: https://apps5.mineco.gob.pe/transparencia/
- Provee: PIA, PIM, devengado por pliego/programa/año.
- Estado: `SIN VERIFICAR`
- ¿Descarga automatizable? — `[por verificar]` (riesgo esperado: ASP.NET/ViewState).
- Procedimiento manual: `[pendiente]`
- Fecha de verificación: `[pendiente]`

### 2. MEF – Ley de Presupuesto
- URL: https://www.mef.gob.pe
- Provee: presupuesto nacional por año (denominador % del PIA nacional).
- Estado: `SIN VERIFICAR`
- Fecha de verificación: `[pendiente]`

### 3. Portal Estadístico Aurora / Warmi Ñan
- URL: https://portalestadistico.aurora.gob.pe/
- Provee: atenciones CEM, Línea 100, SAU, CAI, feminicidios registrados.
- Estado: `SIN VERIFICAR`
- ¿Descarga automatizable? — `[por verificar]` (riesgo: tablero dinámico).
- Fecha de verificación: `[pendiente]`

### 4. Observatorio Nacional de la Violencia
- URL: https://observatorioviolencia.pe/
- Provee: data consolidada MIMP + Salud + PJ + MP + PNP + INEI.
- Estado: `SIN VERIFICAR`
- Fecha de verificación: `[pendiente]`

### 5. INEI – ENDES
- URL: https://www.inei.gob.pe
- Provee: prevalencia de violencia (encuesta) y población (denominador de tasas).
- Estado: `SIN VERIFICAR`
- Fecha de verificación: `[pendiente]`

### 6. Portal de Transparencia Estándar – MIMP
- URL: https://www.transparencia.gob.pe
- Provee: presupuesto, personal, inversiones, contrataciones.
- Estado: `SIN VERIFICAR`
- Fecha de verificación: `[pendiente]`

### 7. Repositorio Aurora / Defensoría del Pueblo
- URL: https://repositorio.aurora.gob.pe · https://www.defensoria.gob.pe
- Provee: informes de supervisión de CEM y servicios (calidad).
- Estado: `SIN VERIFICAR`
- Fecha de verificación: `[pendiente]`

### 8. Mininter/PNP – RENADESPPLE
- URL: `[localizar portal PNP/Mininter]`
- Provee: registro de personas desaparecidas (CONTEXTO multisectorial, no eficacia MIMP).
- Estado: `SIN VERIFICAR`
- Fecha de verificación: `[pendiente]`
