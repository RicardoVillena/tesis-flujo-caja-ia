# Sprint 09 — Verificación

Fecha: 30 de octubre de 2026. Entorno `tesis-fcl` (Python 3.12.15, scikit-learn 1.9.1, numpy 2.5.4, pandas 3.0.6; detalle en [entorno.json](entorno.json)). Rama `sprint-09-variantes-importancia`.

## Ejecución

- **Protocolo:** versionado antes de ejecutar, en el commit `cdf93a1`. `run()` se niega a ejecutar si `protocolo.json` difiere del código.
- **Comando:** `python scripts/reproduce_sprint_09.py`, ejecutado de forma completa: 2 monedas × 5 años externos × 2 modelos × 8 variantes (E0–E4 y 3 con rezago t−1), más las referencias simples y la importancia (520 retiradas individuales y 60 por bloques).
- **Salidas:** escribe en `reports/sprint_09/`; no modifica las carpetas de sprints anteriores. Todos los archivos son deterministas salvo `tiempos_ajuste.csv`.

## Reproducción de resultados anteriores (mismo protocolo)

Detalle en [verificacion_reproduccion.json](verificacion_reproduccion.json):

| Resultado anterior | Diferencia relativa máxima |
|---|---|
| Sprint 08: media histórica, persistencia, Ridge E2 y boosting E2 | ≤ 4,8e-15 |
| Versión inicial del Sprint 09 (`6eeac16`): predicciones E0, E1 y E2 de ambos modelos | 0 |
| Versión inicial del Sprint 09: importancia individual | 2e-16 |

## Pruebas

| Alcance | Comando | Resultado (30 de octubre de 2026) |
|---|---|---|
| Sprint 09 | `python -m unittest tests.test_sprint_09 -v` | 10 de 10 aprobadas |
| Suite completa | `python -m unittest discover -s tests -v` ([registro_pruebas.txt](registro_pruebas.txt)) | 106 pruebas; **103 aprobadas y 3 fallidas** |

**Qué verifican las pruebas del Sprint 09:**
- que el protocolo es el versionado;
- mismas filas y objetivos en los 18 procedimientos de cada moneda y año, sin filas de prueba 2022–2025;
- separación temporal de los pliegues internos y de las búsquedas;
- que la selección E4 no cambia al perturbar años futuros ni la partición de prueba, y sí cambia al perturbar un año interno (control positivo);
- que perturbar la partición de prueba no cambia los resultados de una ejecución reducida;
- la tabla con rezago t−1;
- la reconstrucción de métricas y comparaciones desde las predicciones;
- la reproducción de los resultados anteriores;
- la cobertura y el signo de la importancia;
- la coherencia del historial de E4.

**Fallos de la suite completa:** son los mismos 3 fallos de integridad documentados en [el estado de verificación del Sprint 08](../sprint_08/estado_verificacion.md):
- `test_auditoria_calidad...test_prior_files_intact_against_head_and_pre_edit_reference`;
- `test_clasificacion_sectorial...test_reproducibilidad_fuentes_y_salida_exacta`;
- `test_enriquecimiento_sectorial...test_reproduccion_exacta_catalogos_y_json_sin_red`.

Siguen señalando `notebooks/03_extraccion_macroeconomica.ipynb`, ahora incluido en el commit `ecf7f16`, y los mismos archivos que antes. Además, el control de integridad de la Etapa 1, diseñado para proteger lo previo al Sprint 08, ahora también encuentra los archivos nuevos del Sprint 09: es la detección esperada de trabajo nuevo, no una alteración de datos. No hay fallos nuevos causados por el Sprint 09, y no se regeneraron referencias antiguas.

## Comprobaciones de diseño

- **Selección sin datos externos:** los hiperparámetros y los atributos de E4 se eligen solo con los pliegues internos del entrenamiento externo. El ranking de importancia del Sprint 09 no interviene en E4.
- **Presupuesto comparable:** mismas rejillas (8 configuraciones) y mismos pliegues para todas las variantes.
- **Casos extremos:** no se excluyó ninguna empresa ni se cambió el objetivo. La concentración del error está en [concentracion_error.csv](concentracion_error.csv), y los casos extremos documentados (FOSSAL 2017, CD0009 2016, Cerro Verde y otros) en el Sprint 08.
