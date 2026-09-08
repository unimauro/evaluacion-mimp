# Evaluación de la gestión del MIMP (Perú)

Evaluación de política pública sobre la gestión del **Ministerio de la Mujer y
Poblaciones Vulnerables (MIMP, pliego 039)**, a partir de datos abiertos y oficiales.

Idioma de trabajo y entregables: **español**.

## Objetivo

Evaluar la eficacia de la gestión del MIMP en sus dimensiones propias (servicios,
prevención, articulación y ejecución presupuestal), distinguiendo con rigor lo que
es medida directa de eficacia del MIMP de lo que es **contexto de corresponsabilidad
multisectorial** (feminicidios → MP/PJ; violaciones y desapariciones → Mininter/PNP).

## Periodo

**2019–2025** (serie de 6–7 años).
> `SUPUESTO`: periodo 2019–2025, ajustable. Se confirmará según disponibilidad real
> de series por fuente (ver `00_fuentes/FUENTES.md`).

## Supuestos vigentes

- `SUPUESTO`: periodo de análisis 2019–2025.
- `SUPUESTO`: pliego 039 incluye programas/UE: Programa **Warmi Ñan** (ex-AURORA),
  INABIF, CONADIS, DGNNA, entre otros.
- Nota de vigencia: **AURORA se renombró a "Warmi Ñan"** (DS 003-2025-MIMP, 2025).
  ✅ Verificado en Fase 1 (2026-09-08): **el dominio SÍ cambió** — `*.aurora.gob.pe`
  redirige (301) a `*.warminan.gob.pe` y el TLS de aurora ya no valida. **Usar
  `*.warminan.gob.pe`** en todo el proyecto. Prensa indica que se mantiene la estructura.
- ✅ Corrección Fase 1: el spec confunde **RENADESPPLE** (registro de detenidos del
  Ministerio Público) con desapariciones. El registro real de personas desaparecidas es
  **RENIPED** (PNP). Se usa RENIPED como contexto. Ver `00_fuentes/FUENTES.md`.

## Reglas inviolables (resumen)

1. No inventar nada (cifras, fuentes, URLs, fechas). Dato faltante →
   `[NO DISPONIBLE — requiere descarga manual desde <URL>]`.
2. Cada cifra lleva trazabilidad: **valor + fuente + URL exacta + fecha de descarga**.
3. No atribuir al MIMP resultados multisectoriales.
4. No mezclar registros administrativos con encuesta poblacional (prevalencia ENDES).
5. Normalizar por población (tasa por 100 000 mujeres), documentando el denominador.
6. Marcar todo supuesto como `SUPUESTO: ...`.
7. Advertir vigencia (cambios de dominio, metodología, denominación).
8. No simular resultados de técnicas no dominadas: documentar y dejar para verificación.

Detalle completo en [`INSTRUCCIONES.md`](INSTRUCCIONES.md).

## Estructura del repositorio

```
evaluacion-mimp/
  00_fuentes/FUENTES.md        # estado de cada fuente (accesible/parcial/manual)
  01_data_cruda/               # descargas tal cual (con fecha en el nombre)
  02_data_procesada/           # datasets limpios y unificados
  03_analisis/                 # indicadores, tablas, gráficos
  04_entregables/              # informe .docx, base .xlsx, tablero
  scripts/                     # todo el código, reproducible
  README.md
  INSTRUCCIONES.md             # spec completo del encargo
```

## Dimensiones evaluadas

1. Presupuestal (PIA, PIM, % ejecución, peso en presupuesto nacional, gasto por PP).
2. Cobertura y producción de servicios (CEM, Línea 100/Chat 100, SAU, CAI).
3. Calidad de la atención (tiempos, seguimiento, idoneidad del personal).
4. Prevención (acciones preventivas, personas informadas, estrategia rural).
5. Resultado/impacto como contribución (feminicidios y tentativas, prevalencia ENDES).
6. Gestión institucional (rotación de titulares, ejecución de inversiones, brechas RR.HH.).

## Hipótesis a contrastar (no darlas por ciertas)

- **H1**: los indicadores de violencia no han disminuido pese al gasto.
- **H2**: la producción de servicios está estancada.
- **H3**: el presupuesto es bajo y/o se subejecuta.
- **H4**: hay brechas de cobertura territorial frente a la incidencia.
- **H5**: hay problemas de calidad/idoneidad en la atención.
- **H6**: predomina la gestión de imagen sobre resultados.

## Estado del proyecto

| Fase | Descripción | Estado |
|---|---|---|
| 0 | Setup (estructura + README) | ✅ Hecho |
| 1 | Reconocimiento de fuentes | ✅ Hecho (ver `00_fuentes/`) |
| 2 | Recolección | ⬜ Pendiente |
| 3 | Procesamiento | ⬜ Pendiente |
| 4 | Análisis e indicadores | ⬜ Pendiente |
| 5 | Interpretación con salvaguardas | ⬜ Pendiente |
| 6 | Entregables | ⬜ Pendiente |

## Reproducibilidad

Todo el código vive en `scripts/`. Ver [`scripts/requirements.txt`](scripts/requirements.txt).

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r scripts/requirements.txt
```
