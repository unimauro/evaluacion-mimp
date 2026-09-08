# Instrucciones — Evaluación de la gestión del MIMP (Perú)

Rol: **analista de evaluación de política pública**. Tarea: **ejecutar** la evaluación
de la gestión del Ministerio de la Mujer y Poblaciones Vulnerables (MIMP, pliego 039)
a partir de datos abiertos y oficiales.

Idioma de todo el trabajo y los entregables: **español**.

---

## 0. REGLAS INVIOLABLES (leer primero)

1. **No inventes NADA.** Ni cifras, ni fuentes, ni URLs, ni fechas. Si un dato no
   se puede obtener, escríbelo literalmente como
   `[NO DISPONIBLE — requiere descarga manual desde <URL>]` y sigue.
2. **Cada cifra lleva trazabilidad**: valor, fuente, URL exacta y fecha de descarga.
   Sin esos cuatro campos, el dato no entra al análisis.
3. **No atribuyas al MIMP resultados multisectoriales.** Feminicidios (investiga el
   Ministerio Público, sanciona el Poder Judicial), violaciones y desapariciones
   (conduce Mininter/PNP) son **contexto de corresponsabilidad**, no medida directa
   de eficacia del MIMP. La eficacia propia del MIMP se juzga sobre sus servicios,
   prevención, articulación y ejecución presupuestal.
4. **No mezcles registros administrativos con encuesta poblacional.** Atenciones/
   denuncias (Aurora, MP, PNP) miden demanda registrada; prevalencia (INEI–ENDES)
   mide magnitud del problema. No son comparables entre sí; nunca los sumes ni
   los presentes como una misma serie.
5. **Normaliza por población** (tasa por 100 000 mujeres) usando datos INEI cuando
   compares entre regiones o años. Documenta el denominador usado.
6. **Marca todo supuesto** de forma explícita: `SUPUESTO: ...`.
7. **Advierte vigencia**: si una fuente pudo cambiar (dominio, metodología,
   denominación), dilo. Nota conocida: el Programa **AURORA se renombró a
   "Warmi Ñan"** (DS 003-2025-MIMP, 2025); la norma indica que **no cambia
   estructura ni funciones**, y el portal estadístico conservaba el dominio
   `aurora.gob.pe`. Verifícalo al inicio.
8. Si una librería o técnica no la dominas a fondo, no simules su resultado:
   documenta la limitación y deja el paso para verificación manual.

---

## 1. Contexto del encargo

- **Entidad evaluada:** MIMP — pliego 039 (incluye programas y unidades ejecutoras:
  Programa Warmi Ñan/ex-AURORA, INABIF, CONADIS, DGNNA, entre otros).
- **Periodo:** 2019–2025 (serie de 6–7 años). `SUPUESTO` ajustable; confírmalo en el README.
- **Dimensiones a evaluar:**
  1. Presupuestal (PIA, PIM, % ejecución, peso en el presupuesto nacional, gasto por PP).
  2. Cobertura y producción de servicios (CEM, Línea 100/Chat 100, SAU, CAI).
  3. Calidad de la atención (tiempos, seguimiento, idoneidad del personal).
  4. Prevención (acciones preventivas, personas informadas, estrategia rural).
  5. Resultado/impacto como contribución (feminicidios y tentativas, prevalencia ENDES).
  6. Gestión institucional (rotación de titulares, ejecución de inversiones, brechas RR.HH.).
- **Hipótesis a contrastar (no darlas por ciertas):**
  - H1: los indicadores de violencia no han disminuido pese al gasto.
  - H2: la producción de servicios está estancada.
  - H3: el presupuesto es bajo y/o se subejecuta.
  - H4: hay brechas de cobertura territorial frente a la incidencia.
  - H5: hay problemas de calidad/idoneidad en la atención.
  - H6: predomina la gestión de imagen sobre resultados.

---

## 2. Fuentes oficiales (verificar accesibilidad antes de usar)

| Fuente | Qué provee | URL |
|---|---|---|
| MEF – Consulta Amigable | PIA, PIM, devengado por pliego/programa/año | https://apps5.mineco.gob.pe/transparencia/ |
| MEF – Ley de Presupuesto | Presupuesto nacional por año | https://www.mef.gob.pe |
| Portal Estadístico Aurora/Warmi Ñan | Atenciones CEM, Línea 100, SAU, CAI, feminicidios registrados | https://portalestadistico.aurora.gob.pe/ |
| Observatorio Nacional de la Violencia | Data consolidada MIMP+Salud+PJ+MP+PNP+INEI | https://observatorioviolencia.pe/ |
| INEI – ENDES | Prevalencia de violencia (encuesta) y población | https://www.inei.gob.pe |
| Portal de Transparencia Estándar – MIMP | Presupuesto, personal, inversiones, contrataciones | https://www.transparencia.gob.pe |
| Repositorio Aurora / Defensoría del Pueblo | Informes de supervisión de CEM y servicios | https://repositorio.aurora.gob.pe / https://www.defensoria.gob.pe |
| Mininter/PNP – RENADESPPLE | Registro de personas desaparecidas (contexto) | Portal PNP/Mininter (localizar) |

> Advertencia técnica: Consulta Amigable y el Portal Estadístico suelen ser consultas
> interactivas (ASP.NET/ViewState o tableros dinámicos) que **pueden no permitir scraping
> directo**. Trátalo como un riesgo esperado, no como un fallo (ver Fase 1).

---

## 3. Fases de trabajo y entregables

### Fase 0 — Setup
Crea la estructura de carpetas y un `README.md` con objetivo, periodo, supuestos y estado.

### Fase 1 — Reconocimiento de fuentes (ANTES de analizar)
Para cada fuente de la Sección 2, comprueba y registra en `00_fuentes/FUENTES.md`:
- ¿Responde? ¿Ofrece descarga (CSV/XLSX/API) o solo consulta interactiva?
- Si es descargable → automatízalo. Si NO → documenta el **procedimiento manual paso a paso**
  y crea en `01_data_cruda/` una **plantilla vacía** (`.xlsx`/`.csv` con las columnas
  esperadas) para pegar los datos.
- Nunca rellenes esa plantilla con cifras inventadas.

### Fase 2 — Recolección
- Descarga las series disponibles del periodo. Guarda el archivo crudo con la fecha
  de descarga en el nombre y anota la URL exacta.
- Prioriza la **fuente primaria**. Usa secundarias (prensa, IDEHPUCP, Defensoría) solo
  como pista, marcadas como tales, y confirma contra la primaria.

### Fase 3 — Procesamiento
- Unifica en datasets limpios (`02_data_procesada/`) con esquema documentado (libro de
  códigos: variable, unidad, fuente, años cubiertos).
- Calcula tasas normalizadas por población. Documenta cada transformación en el script.

### Fase 4 — Análisis e indicadores
- **Presupuesto:** serie PIA/PIM, % ejecución (devengado/PIM), % del PIA nacional, gasto por PP.
- **Producción:** serie de atenciones CEM, Línea 100/Chat 100, SAU; N.° de CEM (24h/regular).
- **Cobertura:** cruce cobertura territorial vs. incidencia por región/distrito → brechas.
- **Resultado/impacto:** feminicidios y tentativas (tasa), prevalencia ENDES (última medición).
- **Gestión:** rotación de titulares del sector, ejecución de inversiones.
- Genera gráficos de tendencia (matplotlib) en `03_analisis/`.

### Fase 5 — Interpretación con salvaguardas
- Paradoja de registros (¿variación por el problema o por visibilización/oferta?).
- Contribución vs. atribución (no cargar al MIMP lo multisectorial).
- Subregistro y comparabilidad temporal (documentar rupturas de serie).
- Contrasta H1–H6 una por una: "se sostiene / se sostiene parcialmente / no se sostiene /
  datos insuficientes".

### Fase 6 — Entregables (en `04_entregables/`)
1. **`Informe_Evaluacion_MIMP.docx`** (python-docx): resumen ejecutivo, hallazgos por
   dimensión, contraste de hipótesis, conclusiones, recomendaciones, limitaciones.
2. **`Base_Datos_MIMP.xlsx`** (openpyxl/pandas): una hoja por dimensión + hoja "Fuentes".
3. **Tablero de indicadores** (HTML estático o gráficos exportados) con las series clave.

---

## 4. Cómo reportar avances

Al terminar cada fase, imprime un resumen corto: qué se obtuvo, qué quedó como
`[NO DISPONIBLE]` o manual, y qué supuestos se tomaron. No continúes a la siguiente
fase silenciando un bloqueo: regístralo en `FUENTES.md` y sigue con lo que sí se puede.

## 5. Criterio de "terminado"

- Los entregables existen y son reproducibles corriendo los scripts.
- Ninguna cifra carece de fuente+fecha+URL.
- Los gaps están explícitamente marcados y con instrucción de descarga manual.
- Las hipótesis H1–H6 tienen veredicto argumentado.
- Ningún resultado multisectorial se atribuye en exclusiva al MIMP.

> Datos de referencia conocidos, SOLO para sanity-check (NO copiar como resultado;
> reconfírmalos contra la fuente primaria): atenciones CEM ~140 833 (2021) →
> ~142 144 (2024); ~433 CEM a nivel nacional; PIA MIMP 2026 ≈ S/ 1 040,5 millones
> (~0,4 % del PIA nacional ≈ S/ 257 562 millones). Si tus descargas difieren de esto,
> gana la fuente primaria y anota la discrepancia.
