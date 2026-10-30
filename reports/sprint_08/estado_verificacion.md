# Sprint 08 — Estado de verificación

Cierre documental: 29 de octubre de 2026. Entorno: `/home/ricardo/miniconda3/envs/tesis-fcl` (Python 3.12.15, scikit-learn 1.9.1, numpy 2.5.4, pandas 3.0.6). Rama `sprint-08-auditoria-calidad`, HEAD `b286885`.

**Resumen:**
- La suite completa **no está totalmente aprobada**.
- Las pruebas específicas de la ablación, la revisión y la comparación están aprobadas.
- La Etapa 1 tiene un fallo de integridad, y otras dos auditorías previas (Sprint 07) tienen fallos de integridad. Los tres fallos se deben a archivos modificados fuera del código de modelado y no afectan predicciones ni métricas.

## 1. Ejecutado en el cierre (29 de octubre de 2026)

Comando: `/home/ricardo/miniconda3/envs/tesis-fcl/bin/python -m unittest discover -s tests -v`. Registro completo en [registro_pruebas_cierre.txt](registro_pruebas_cierre.txt), de 20:08:44 a 20:11:19 (−05:00).
- **Alcance:** las 96 pruebas del repositorio.
- **Salidas:** las pruebas del Sprint 08 regeneran sus análisis en directorios temporales; no escriben en `reports/`.

| Módulo | Etapa | Aprobadas | Fallidas | Qué verifica |
|---|---|---|---|---|
| `tests/test_auditoria_calidad.py` | Sprint 08, Etapa 1 | 15 | 1 | Especificación E2, causas de faltantes, aislamiento de prueba con controles positivos, VIF y número de condición, temporalidad, reproducción byte a byte en temporales, notebook 11 |
| `tests/test_ablacion_variables.py` | Sprint 08, ablación y revisión | 21 | 0 | Aislamiento 2022–2025, pliegues, preparación por pliegue, filas comunes, ablación exacta, métricas, elección entre retiradas admisibles, referencias simples y FCL(t), años futuros, preservación de `ablacion/`, notebook 12 |
| `tests/test_comparacion_modelos.py` | Sprint 08, comparación | 15 | 0 | Aislamiento, separación interna y externa, preparación y objetivo ajustados en entrenamiento, filas comunes, años futuros, métricas, reproducción de la revisión, convergencia, desempates, decisión coherente entre CSV e informe, notebook 13 |
| `tests/test_clasificacion_sectorial.py` | Sprint 07 | 7 | 1 | Ver la sección 3 |
| `tests/test_enriquecimiento_sectorial.py` | Sprint 07 | 11 | 1 | Ver la sección 3 |
| `tests/test_sectorial_fase3.py` | Sprint 07 | 9 | 0 | — |
| `tests/test_feature_engineering.py`, `test_delivery.py`, `test_trace_smv.py` | Anteriores | 15 | 0 | — |
| **Total** | | **93** | **3** | |

## 2. Registros anteriores (no reejecutados por separado; acreditan solo su ejecución)

| Registro | Fecha (mtime) | Resultado registrado |
|---|---|---|
| [pruebas_automatizadas.txt](pruebas_automatizadas.txt) (Etapa 1) | 2026-10-24 21:27 | 60 pruebas, todas aprobadas (antes de las modificaciones descritas en la sección 3) |
| [ablacion/pruebas_automatizadas.txt](ablacion/pruebas_automatizadas.txt) | 2026-10-29 17:02 | 77 pruebas, 3 fallos (los mismos tres) |
| [ablacion_revision/pruebas_automatizadas.txt](ablacion_revision/pruebas_automatizadas.txt) | 2026-10-29 17:46 | 81 pruebas, 3 fallos (los mismos tres) |
| [comparacion_modelos/pruebas_automatizadas.txt](comparacion_modelos/pruebas_automatizadas.txt) | 2026-10-29 19:47 | 96 pruebas, 3 fallos (los mismos tres) |

Estos registros no prueban que el estado actual coincida con el de su fecha; el estado actual es el de la sección 1.

## 3. Fallos registrados y causa documentada

| Prueba | Evidencia | Causa comprobada |
|---|---|---|
| `test_auditoria_calidad.AuditQualityTests.test_prior_files_intact_against_head_and_pre_edit_reference` | El control lista 3 archivos que difieren de `referencia_integridad_previa.csv` (huella del 24 de octubre de 2026) | (a) `notebooks/03_extraccion_macroeconomica.ipynb` y `reports/auditoria_extraccion_macroeconomica.md` tienen cambios sin commit respecto a HEAD (`git diff --stat`: 234 inserciones, 491 eliminaciones) y fecha de archivo 2026-10-24 23:19. (b) `notebooks/README.md` se actualizó en este cierre documental, por encargo. |
| `test_clasificacion_sectorial.SectorialTest.test_reproducibilidad_fuentes_y_salida_exacta` | La auditoría recalculada difiere de `reports/sprint_07/auditoria_sectorial.json` | La única ruta con hash distinto es `notebooks/03_extraccion_macroeconomica.ipynb`, por la misma modificación sin commit. |
| `test_enriquecimiento_sectorial.DocumentaryTest.test_reproduccion_exacta_catalogos_y_json_sin_red` | La auditoría recalculada difiere de `reports/sprint_07/fase_3/auditoria_enriquecimiento.json` | La única ruta con hash distinto es `notebooks/03_extraccion_macroeconomica.ipynb`, por la misma modificación sin commit. |

- **Alcance de las modificaciones:** ningún script del Sprint 08 escribe esas dos rutas. El autor de la modificación no se puede comprobar desde el repositorio.
- **Efecto:** ninguno de los tres fallos afecta los datos, las predicciones ni las métricas del Sprint 08.
- **Referencias antiguas:** no se regeneraron, ni se modificaron datos, para hacer pasar estas pruebas.
- **Observación:** `reports/sprint_07/enriquecimiento/auditoria_enriquecimiento.json` (registro congelado de la Fase 2, del 23 de octubre de 2026 a las 19:21) registra para `src/enriquecimiento_sectorial.py` un hash anterior a la última modificación de ese archivo (23 de octubre de 2026, 21:37). Ninguna prueba compara ese registro; no causa fallos.

## 4. Verificaciones del Sprint 08 incluidas en las pruebas

- **Aislamiento:** perturbar las filas y objetivos de prueba 2022–2025 no cambia ningún resultado. Hay controles positivos: si una contaminación entrara, el resultado cambiaría.
- **Temporalidad:** el entrenamiento precede a la validación interna y a la externa; perturbar un año no cambia los ajustes de años anteriores, pero sí los posteriores.
- **Reproducción:** cada etapa se ejecuta dos veces en directorios temporales y produce archivos idénticos byte a byte (salvo `tiempos_ajuste.csv`). Esto acredita determinismo en este entorno, no en otras máquinas o versiones.
- **Coherencia entre etapas:** la media histórica, la persistencia y Ridge de la comparación reproducen la revisión (diferencia relativa ≤ 5e-15). El modelo E2 reproduce las predicciones de entrenamiento del notebook 07 (diferencia 0).
- **Ejecución de los notebooks 11, 12 y 13:** completa, con la numeración de ejecución consecutiva comprobada por las pruebas.

## 5. Comprobaciones documentales del cierre

- Las cifras del [informe final](informe_final_sprint_08.md) se contrastaron con los CSV finales.
- Las rutas y enlaces locales de los documentos de cierre se verificaron.
- El cierre no modificó fuentes, código de modelado, predicciones ni métricas: se comparó el hash de todos los archivos antes y después. Solo se crearon o actualizaron:
  - `informe_final_sprint_08.md`
  - `estado_verificacion.md`
  - `README.md` (de Sprint 08)
  - `registro_pruebas_cierre.txt`
  - `notebooks/README.md`
