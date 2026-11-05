# Informe de Auditoría Independiente — Sesión IA07 (Optimización de Hiperparámetros de Ridge: Random Search vs. Optuna TPE)

**Fecha de auditoría:** 4 de noviembre de 2026  
**Proyecto:** `tesis-flujo-caja-ia`  
**Rama evaluada:** `sprint-09-variantes-importancia` (commits `e68d3e2`, `c6bb6df` y cambios locales en árbol de trabajo del 4 de noviembre de 2026)  
**Alcance:**
- Código fuente y reproducción: [`src/optimizacion_hiperparametros.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/optimizacion_hiperparametros.py), [`scripts/reproduce_optimizacion_hiperparametros.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/scripts/reproduce_optimizacion_hiperparametros.py), [`requirements-ia07.txt`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/requirements-ia07.txt).
- Pruebas automatizadas: [`tests/test_optimizacion_hiperparametros.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_optimizacion_hiperparametros.py).
- Notebook y reportes: [`notebooks/ia07/15_optimizacion_hiperparametros.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/ia07/15_optimizacion_hiperparametros.ipynb), [`reports/ia07/informe_resultados.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/informe_resultados.md), [`reports/ia07/informe_auditoria_kimi.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/informe_auditoria_kimi.md), [`reports/ia07/revision_auditoria_kimi.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/revision_auditoria_kimi.md).

---

## 1. Resumen de Verificaciones

| Dimensión Auditada | Verificación | Estado | Evidencia |
|---|---|---|---|
| **1. Integridad del panel y partición** | `4,221` filas totales; `3,560` elegibles (`2,869` entrenamiento $\le 2021$, `691` prueba `2022–2025`); SHA-256 `c0a116958c422ffc…` | **APROBADO** | [`integridad_previa.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/integridad_previa.json) y [`cargar_muestra()`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/optimizacion_hiperparametros.py#L63-L85) |
| **2. Reproducción exacta de baselines 07 y 08** | Reproducción exacta de predicciones de `07_baseline_variantes.ipynb` (`rtol=1e-9`) y de las 216 puntuaciones CV y predicciones de `08_mejoras_baseline.ipynb` | **APROBADO** | [`ReproduccionTests`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_optimizacion_hiperparametros.py#L59-L101) |
| **3. Aislamiento contra fuga temporal y de prueba** | [`EvaluadorCV`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/optimizacion_hiperparametros.py#L162-L190) rechaza filas de prueba; imputación, `ClipRatios` y escalado se ajustan dentro de cada pliegue; invariancia ante perturbación de prueba con control positivo | **APROBADO** | [`SinFugaTests`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_optimizacion_hiperparametros.py#L103-L134) |
| **4. Presupuesto equivalente y determinismo** | `16` estudios × `2` métodos × `20` semillas × `60` trials = `38,400` trials (`100% COMPLETE`); primeros `10` trials idénticos en las `320` parejas estudio-semilla; segunda ejecución completa idéntica | **APROBADO** | [`trials.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/trials.csv), [`verificacion_determinismo.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/verificacion_determinismo.json) |
| **5. Congelación criptográfica previa a prueba** | [`seleccion_congelada.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/seleccion_congelada.csv) (`9ee2e553a717bd57…`) congelada en `22:43:31Z` antes de evaluar prueba en `22:44:01Z` | **APROBADO** | [`seleccion_congelada.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/seleccion_congelada.json), [`evaluacion_prueba.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/evaluacion_prueba.json) |
| **6. Recálculo independiente de métricas de prueba** | `MAE`, `RMSE` y `R2` recalculados sobre las `72` configuraciones desde [`predicciones_prueba.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/predicciones_prueba.csv) | **APROBADO** | Diferencia máxima: `6.05e-09` (MAE), `5.59e-09` (RMSE), `1.15e-14` ($R^2$) |
| **7. Corrección de inferencia pareada por semilla (Wilcoxon)** | [`_wilcoxon_pareada()`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/optimizacion_hiperparametros.py#L334-L339) y emparejamiento por semilla en [`analizar_convergencia()`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/optimizacion_hiperparametros.py#L342-L377) con 4 pruebas nuevas (`30` en total) | **OBSERVADO** | Código y tests actualizados, pero falta reejecutar `--analizar` para actualizar [`comparacion_metodos.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/comparacion_metodos.csv) y [`comparacion_metodos_agregada.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/comparacion_metodos_agregada.csv) en disco |
| **8. Estructura y ejecución del notebook 15** | `37` celdas (`25` Markdown con títulos numerados `1..13` en negrita, `12` de código ejecutadas `1..12` sin errores) | **OBSERVADO** | Pendiente de reejecutar para mostrar las nuevas columnas `p_wilcoxon` y `p_wilcoxon_holm` |

---

## 2. Errores Críticos

- **Ninguno (`0`).**

---

## 3. Observaciones Importantes

1. **Sincronización pendiente entre el código actualizado (`Wilcoxon`) y los CSV/informes en disco (OBSERVADO):**
   - El 4 de noviembre de 2026 (`12:32–12:34`) se modificaron [`src/optimizacion_hiperparametros.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/optimizacion_hiperparametros.py#L334-L377) y [`tests/test_optimizacion_hiperparametros.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_optimizacion_hiperparametros.py#L171-L208) para incorporar la prueba de rangos con signo de Wilcoxon pareada por semilla (`p_wilcoxon`, `p_wilcoxon_holm`, `estudios_p_wilcoxon_menor_005`, `estudios_p_wilcoxon_holm_menor_005`).
   - Sin embargo, los archivos en disco [`reports/ia07/comparacion_metodos.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/comparacion_metodos.csv) y [`reports/ia07/comparacion_metodos_agregada.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/comparacion_metodos_agregada.csv) conservan su fecha del 3 de noviembre (`17:46`) y aún no contienen las columnas de Wilcoxon. Tampoco se han actualizado aún [`informe_resultados.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/informe_resultados.md), [`15_optimizacion_hiperparametros.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/ia07/15_optimizacion_hiperparametros.ipynb) ni [`registro_pruebas.txt`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/registro_pruebas.txt).
2. **Ventaja estructural de `seleccion_08` en validación (OBSERVADO — Documentado):**
   - La especificación `seleccion_08` fue elegida previamente en el notebook `08_mejoras_baseline.ipynb` sobre las mismas ventanas de validación temporal, por lo que su `mse_cv` tiene sesgo optimista al competir contra `E0_07`, `E1_07` y `E2_07` para elegir al ganador de cada cohorte. Está documentado explícitamente en [`informe_resultados.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/informe_resultados.md#L104).
3. **Evaluación exploratoria en la partición de prueba `2022–2025` (OBSERVADO — Documentado):**
   - A diferencia de los Sprints 08 y 09 (que se mantuvieron estrictamente dentro de entrenamiento `<= 2021`), IA07 evalúa una única vez las configuraciones congeladas de Ridge sobre la partición de prueba `2022–2025` para contrastar con los notebooks 07 y 08. Como dicha partición ya fue inspeccionada en el Sprint 06, los resultados en prueba tienen carácter exploratorio/comparativo y no confirmatorio.

---

## 4. Observaciones Menores

1. **Precisión terminológica en tiempos de cómputo:** En [`informe_resultados.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/informe_resultados.md#L97) y en el notebook 15 se indica que un trial tarda "unos 13 ms en Random Search y 17 ms en TPE"; conviene precisar que `13.09 ms` y `16.79 ms` corresponden a las **medianas** (las medias son `23.28 ms` y `26.51 ms`).
2. **Ampliación opcional de `test_metricas_reconstruidas_y_mismas_filas`:** Actualmente [`test_metricas_reconstruidas_y_mismas_filas`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_optimizacion_hiperparametros.py#L258-L264) verifica `RMSE`, igualdad de `id_fila` y rango de años `2022..2025`; puede añadirse la verificación explícita de `MAE` y `R2` como se propuso en [`revision_auditoria_kimi.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/revision_auditoria_kimi.md#L70).

---

## 5. Recomendaciones

1. Ejecutar `~/.venvs/tesis-fcl-ia07/bin/python scripts/reproduce_optimizacion_hiperparametros.py --analizar` para regenerar [`comparacion_metodos.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/comparacion_metodos.csv) y [`comparacion_metodos_agregada.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/comparacion_metodos_agregada.csv) con las columnas `p_wilcoxon` y `p_wilcoxon_holm` (este comando no toca `seleccion_congelada.csv` ni `metricas_prueba.csv`).
2. Actualizar [`informe_resultados.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/informe_resultados.md), reejecutar [`15_optimizacion_hiperparametros.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/ia07/15_optimizacion_hiperparametros.ipynb) y actualizar [`registro_pruebas.txt`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/registro_pruebas.txt) con las `30` pruebas unitarias.

---

## 6. Dictamen Final

**DICTAMEN: APROBADO CON OBSERVACIONES**

