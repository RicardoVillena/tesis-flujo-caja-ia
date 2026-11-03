# Índice de notebooks

- `08_mejoras_baseline.ipynb`: experimento original de Sprint 06; no modificado.
- `sprint_07/10_clasificacion_sectorial.ipynb`: ruta canónica de la clasificación sectorial (Fase 3).
- `08_clasificacion_sectorial.ipynb`: enlace simbólico de compatibilidad para scripts anteriores; no es otro notebook ni otro experimento.

Para inventariar notebooks, resolver rutas y excluir enlaces simbólicos del conteo físico. El conteo histórico por glob del notebook 09 no reconoce alias; no volver a interpretar ese conteo como número de experimentos. La numeración canónica evita dos notebooks con número 08.

Reproducción sin entrenamiento: `python scripts/reproduce_enriquecimiento_sectorial.py`. El notebook busca la raíz del repositorio ascendiendo directorios, por lo que ambas rutas son compatibles.

## Sprint 08 (`notebooks/sprint_08/`)

Orden de lectura y función. Los tres notebooks se ejecutan con el kernel `tesis-fcl` y buscan la raíz del repositorio ascendiendo directorios. Toda la lógica está en `src/`; cada notebook llama a su `run()`, que **regenera** los resultados de su etapa.

1. `sprint_08/11_auditoria_calidad_atributos.ipynb`: auditoría descriptiva de los 26 atributos de E2 (Etapa 1). Llama a `run()` de `src/auditoria_calidad.py` y escribe en `reports/sprint_08/` (CSV, `resumen_auditoria.md`, `integridad.json`, `especificacion_e2.json`). No entrena modelos.
2. `sprint_08/12_ablacion_variables.ipynb`: ablación individual y primera validación anidada (antecedente). Llama a `run()` de `src/ablacion_variables.py` y escribe en `reports/sprint_08/ablacion/`. La revisión final de esa etapa no tiene notebook propio: se reproduce con `scripts/reproduce_ablacion_variables.py --revision` (`reports/sprint_08/ablacion_revision/`).
3. `sprint_08/13_comparacion_modelos.ipynb`: comparación exploratoria de media histórica, persistencia, Ridge, Elastic Net y boosting (resultado final de modelado). Llama a `run()` de `src/comparacion_modelos.py` y escribe en `reports/sprint_08/comparacion_modelos/`.

Los tres notebooks ejecutan además las pruebas de su etapa (excepto la que inspecciona el propio notebook). Punto de entrada de la entrega: `reports/sprint_08/README.md`.

## Sesión IA07 (`notebooks/ia07/`)

`ia07/15_optimizacion_hiperparametros.ipynb`: Random Search y Optuna TPE para Ridge. Presenta los resultados de `scripts/reproduce_optimizacion_hiperparametros.py` sin repetir la búsqueda ni la evaluación en prueba. Usa el kernel `tesis-fcl-ia07` (ver `reports/ia07/README.md`).
