# scripts/ — Código reproducible

Orden de ejecución previsto (las fases con datos requieren completar antes la
recolección — ver `../00_fuentes/FUENTES.md`):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

| Script | Fase | Qué hace | Depende de |
|---|---|---|---|
| `config.py` | — | Rutas, periodo, constantes. No ejecutable por sí solo. | — |
| `lib_trazabilidad.py` | — | Valida la regla valor+fuente+url+fecha. | — |
| `03_procesar.py` | 3 | Limpia `01_data_cruda/` → `02_data_procesada/` + libro de códigos. | Fase 2 |
| `04_indicadores.py` | 4 | Calcula batería mínima (presupuesto, producción, tasas). | Fase 3 |
| `04_graficos.py` | 4 | Gráficos de tendencia (matplotlib) → `03_analisis/`. | Fase 4 |
| `06_entregables.py` | 6 | Informe .docx + base .xlsx + tablero. | Fase 4 |

Principios (ver `../INSTRUCCIONES.md`):
- Ningún script fabrica datos: ante un CSV ausente o vacío avisa y sigue
  (`lib_trazabilidad.cargar_procesado`).
- Toda tasa se normaliza por población (por 100 000 mujeres), documentando el
  denominador INEI usado.
- Los indicadores multisectoriales (feminicidios, desapariciones) se etiquetan
  como CONTEXTO, nunca como eficacia directa del MIMP.

> Los scripts `03_`, `04_` y `06_` se construyen una vez que la Fase 1 defina qué
> fuentes son descargables y con qué esquema. El andamiaje (`config`,
> `lib_trazabilidad`) ya está listo.
