# Alineación con el plan de investigación (Sprint 09, revisión local)

Esta revisión contrasta la implementación con el plan de tesis `notebooks/Trabajo_de_investigacion_final.pdf` (usado como referencia académica, no como instrucciones operativas). Repite el experimento en la población no financiera, evalúa el tamaño empresarial y delimita lo pendiente para una valoración probabilística.

Es exploratoria y está **sin commit**: los cambios quedan en local para revisión.

## Entregables

| Documento | Contenido |
|---|---|
| [informe_alineacion.md](informe_alineacion.md) | Respuestas a las 5 preguntas, resultados y limitaciones |
| [matriz_consistencia.md](matriz_consistencia.md) | Problema, objetivos, hipótesis, variables e indicadores: (A) alcance original del plan, (B) componente implementado y qué es contrastable |
| [matriz_operacionalizacion.md](matriz_operacionalizacion.md) | Definición conceptual y operacional, dimensiones, medición, unidades y fuentes; variables del plan sin datos |
| [antecedentes.md](antecedentes.md) | Ali (2026) y Pham (2026), verificados en el original; Lu y Zhao (2025), solo resumen |
| [viabilidad_pendientes.md](viabilidad_pendientes.md) | LSTM, DCF, tasa de descuento, valor terminal y evaluación probabilística (sin implementar) |
| [protocolo.json](protocolo.json) | Protocolo fijado antes de ejecutar (SHA-256 `99fee593…`, 30 de octubre de 2026, 13:33:30) |

**Datos y resultados:**
- Población: `poblacion_por_anio_sector_moneda.csv`, `poblacion_resumen.csv`, `clasificaciones_dudosas.csv` y `clasificacion_filas.csv`.
- Variables: `auditoria_variables.csv`.
- Modelado:
  - búsquedas internas: `busquedas_internas.csv`;
  - predicciones con identificadores de fila: `predicciones.csv`;
  - métricas: `metricas_por_anio.csv` y `resumen_procedimientos.csv`;
  - comparaciones: `comparaciones_por_anio.csv` y `resumen_comparaciones.csv`;
  - importancia individual y por bloques: archivos `importancia_*.csv`;
  - concentración del error: `concentracion_error.csv`.
- Entorno y verificación: `entorno.json`, `verificacion_reproduccion.json` y [registro_pruebas.txt](registro_pruebas.txt).
- Gráficos: [graficos/](graficos/).

## Reproducción

Desde la raíz del repositorio, en el entorno existente `tesis-fcl` (sin red):

```bash
python scripts/reproduce_alineacion_investigacion.py --protocolo   # solo escribe protocolo.json
python scripts/reproduce_alineacion_investigacion.py               # regenera esta carpeta (salvo los .md); exige el protocolo versionado
python -m unittest tests.test_alineacion_investigacion -v
```

- **Código:** `src/alineacion_investigacion.py` reutiliza `src/variantes_importancia.py`, `src/comparacion_modelos.py` y `src/ablacion_variables.py`.
- **Dependencias de solo lectura:** `data/processed/`, el catálogo sectorial `reports/sprint_07/fase_3/catalogo_empresa_anio.csv` y, para la verificación en dólares, `reports/sprint_09/predicciones.csv`.

## Verificación (30 de octubre de 2026)

- **Pruebas de esta línea** (`tests/test_alineacion_investigacion.py`): 9 de 9 aprobadas. Comprueban:
  - el protocolo versionado;
  - el filtro sectorial y la trazabilidad de exclusiones y dudosas;
  - las mismas filas en todas las variantes de cada población;
  - la separación temporal;
  - que perturbar la partición de prueba o años futuros no cambia los resultados (con control positivo);
  - la reconstrucción de métricas;
  - la coherencia de atributos y transformaciones (tamaño = ln del activo y ningún sustituto del efectivo);
  - la reproducción del Sprint 09 en dólares;
  - la cobertura y el signo de la importancia.
- **Suite completa:** 115 pruebas, **112 aprobadas y 3 fallidas**. Los 3 fallos son los de integridad históricos, documentados en `../verificacion.md` y en `../../sprint_08/estado_verificacion.md`; no hay fallos nuevos.
- **Lectura del PDF:** no hay herramientas de PDF en el entorno y se denegó instalar `pypdf`. El plan y los artículos se leyeron con un extractor mínimo de la biblioteca estándar, ejecutado desde el scratchpad, que no forma parte del repositorio.

## Etapa siguiente

[../experimento_final/](../experimento_final/README.md): formulaciones del objetivo, pérdida absoluta y E0–E3 sobre la población no financiera (regla SMV). En esa etapa, la población conservadora de esta carpeta queda identificada como sensibilidad retrospectiva.
