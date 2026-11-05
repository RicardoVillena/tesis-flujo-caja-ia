# Informe de Auditoría Independiente — Sprint 08 (Calidad de Atributos, Ablación y Comparación de Modelos)

**Fecha de auditoría:** 4 de noviembre de 2026  
**Proyecto:** `tesis-flujo-caja-ia`  
**Rama evaluada:** `sprint-09-variantes-importancia` (commit de cierre `ecf7f16` y estado actual `c6bb6df`)  
**Alcance:**
- **Etapa 1 (Calidad de los 26 atributos E2):** [`src/auditoria_calidad.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/auditoria_calidad.py), [`notebooks/sprint_08/11_auditoria_calidad_atributos.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/sprint_08/11_auditoria_calidad_atributos.ipynb), [`reports/sprint_08/resumen_auditoria.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/resumen_auditoria.md).
- **Etapa 2a y 2b (Ablación individual y revisión de validación anidada):** [`src/ablacion_variables.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/ablacion_variables.py), [`notebooks/sprint_08/12_ablacion_variables.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/sprint_08/12_ablacion_variables.ipynb), [`reports/sprint_08/ablacion/informe_ablacion.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/ablacion/informe_ablacion.md), [`reports/sprint_08/ablacion_revision/informe_revision.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/ablacion_revision/informe_revision.md).
- **Etapa 3 (Comparación exploratoria de modelos):** [`src/comparacion_modelos.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/comparacion_modelos.py), [`notebooks/sprint_08/13_comparacion_modelos.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/sprint_08/13_comparacion_modelos.ipynb), [`reports/sprint_08/comparacion_modelos/informe_comparacion.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/comparacion_modelos/informe_comparacion.md).
- **Informe consolidado:** [`reports/sprint_08/informe_final_sprint_08.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/informe_final_sprint_08.md).

---

## 1. Resumen de Verificaciones

| Dimensión Auditada | Verificación | Estado | Evidencia |
|---|---|---|---|
| **1. Integridad del panel base** | Conservación de 4,221 filas, 68 columnas y 3,560 elegibles (2,869 entrenamiento, 691 prueba) | **APROBADO** | SHA-256 `c0a116958c422ffc…` intacto en [`panel_financiero_macro_bursatil.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/panel_financiero_macro_bursatil.csv) |
| **2. Aislamiento de la partición de prueba** | Ninguna etapa del Sprint 08 utiliza filas ni objetivos de `2022–2025`; pruebas con perturbación y controles positivos | **APROBADO** | [`test_auditoria_calidad.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_auditoria_calidad.py), [`test_ablacion_variables.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_ablacion_variables.py), [`test_comparacion_modelos.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_comparacion_modelos.py) |
| **3. Especificación de los 26 atributos E2** | 19 financieros + 4 macroeconómicos + 3 bursátiles verificados contra el notebook 07 | **APROBADO** | [`especificacion_e2.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/especificacion_e2.json) y [`tabla_26_atributos.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/tabla_26_atributos.csv) |
| **4. Trazabilidad de celdas faltantes y colinealidad** | Las 8,285 celdas faltantes de entrenamiento tienen causa documentada; VIF y número de condición verificados (soles baja de 221.43 a 18.39 sin 3 casos extremos) | **APROBADO** | [`faltantes_causas_train.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/faltantes_causas_train.csv), [`diagnostico_vif.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/diagnostico_vif.csv) |
| **5. Auditoría de disponibilidad temporal** | Clasificación explícita: 0 verificados, 14 no verificados, 12 con posible fuga temporal | **APROBADO** | [`auditoria_temporal.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/auditoria_temporal.csv) |
| **6. Validación temporal anidada (Etapas 2b y 3)** | Años externos `2017–2021` (119 filas en dólares, 829 en soles); pliegues internos con $\ge 8$ años de historia y `anio_interno < anio_externo` | **APROBADO** | [`ablacion_revision/resumen.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/ablacion_revision/resumen.csv), [`comparacion_modelos/resumen_procedimientos.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/comparacion_modelos/resumen_procedimientos.csv) |
| **7. Coherencia de decisiones estadísticas** | Separación entre menor RMSE observado y superioridad consistente (regla predefinida: $\le -1\%$ RMSE medio, $\ge 4/5$ años, $\Delta \text{MAE} \le 0$) | **APROBADO** | [`comparacion_modelos/decision.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/comparacion_modelos/decision.csv) |
| **8. Estructura y ejecución de notebooks 11, 12 y 13** | Kernel `tesis-fcl`, ejecución lineal `1..N` sin errores (`14`, `11` y `9` celdas de código respectivamente) | **APROBADO** | Notebooks [`11`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/sprint_08/11_auditoria_calidad_atributos.ipynb), [`12`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/sprint_08/12_ablacion_variables.ipynb), [`13`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/sprint_08/13_comparacion_modelos.ipynb) |
| **9. Suite de pruebas del Sprint 08** | `51/52` pruebas aprobadas (`15/16` en Etapa 1, `21/21` en Etapa 2, `15/15` en Etapa 3) | **OBSERVADO** | 1 fallo de huella histórica en [`test_auditoria_calidad.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_auditoria_calidad.py#L181-L191) documentado en [`estado_verificacion.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/estado_verificacion.md) |

---

## 2. Errores Críticos

- **Ninguno (`0`).** No se detectó fuga de información de la partición de prueba ni de ejercicios futuros, ni alteración de los datos procesados.

---

## 3. Errores Importantes / Observaciones Metodológicas

1. **Concentración extrema del error cuadrático externo (OBSERVADO — Documentado):**
   - Las 3 empresas con mayor error concentran entre el `81.5%` y el `89.5%` del error cuadrático externo (`CM0006` en dólares; `B80004` en soles). Al excluir `B80004` en soles, Ridge pasa a tener menor RMSE que Boosting. El informe consolidado lo declara correctamente como sensibilidad descriptiva sin alterar la regla de decisión.
2. **Óptimos en el borde de la rejilla de regularización (OBSERVADO — Documentado):**
   - En la Etapa 3, `ElasticNet` selecciona el extremo superior de su rejilla de $\alpha$ en `5/5` años en dólares y `4/5` en soles, y `Ridge` alcanza $\alpha = 1,000,000$ en `3/5` años en soles. Se mantuvo la rejilla predefinida sin modificarla post-hoc.
3. **Fallo en la prueba de huella previa `test_prior_files_intact_against_head_and_pre_edit_reference` (OBSERVADO):**
   - La prueba compara el árbol contra [`referencia_integridad_previa.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/referencia_integridad_previa.csv) (tomada el 24 de octubre de 2026) y detecta cambios posteriores en [`notebooks/03_extraccion_macroeconomica.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/03_extraccion_macroeconomica.ipynb), [`reports/auditoria_extraccion_macroeconomica.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/auditoria_extraccion_macroeconomica.md) y [`notebooks/README.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/README.md). No afecta datos ni resultados del Sprint 08.

---

## 4. Resultados Clave Verificados

### 4.1 Revisión de Validación Anidada (Etapa 2b — Selección de Variables)
- **Dólares (`119` filas externas):** El procedimiento reducido cambia el RMSE anual medio en `-2.73%`, pero mejora solo en `1/5` años y empeora en `3/5`. Decisión verificada: **conservar los 26 atributos**.
- **Soles (`829` filas externas):** El procedimiento reducido no retira ningún atributo en ningún año (`0.00%`). Decisión verificada: **conservar los 26 atributos**.

### 4.2 Comparación de Modelos (Etapa 3 — RMSE Anual Medio 2017–2021)

| Moneda | Media Histórica | Persistencia | Ridge | Elastic Net | HistGradientBoosting | Modelo Recomendado |
|---|---:|---:|---:|---:|---:|---|
| **Dólares** | `288,696` | **`192,066`** | `247,885` | `259,556` | `234,081` | **Persistencia** (`-22.52%` RMSE y `-30.53%` MAE vs. Ridge; `4/5` años) |
| **Soles** | `933,387` | `1,310,531` | `919,862` | `943,622` | **`911,069`** | **Conservar Ridge** (Boosting reduce RMSE `-0.956%` < umbral `1%`) |

---

## 5. Recomendaciones

1. Mantener en la tesis la distinción explícita entre **problemas de calidad del dato** (denominadores cercanos a cero como `FOSSAL 2017` y saltos de escala como `CD0009 2016`) y **decisiones de selección de variables**, tal como se documenta en [`informe_final_sprint_08.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/informe_final_sprint_08.md).
2. Al cierre definitivo del repositorio, decidir si se actualiza o parametriza la lista de rutas vigiladas en [`test_auditoria_calidad.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_auditoria_calidad.py#L181-L191) para excluir archivos documentales modificados en sprints posteriores (`notebooks/README.md`).

---

## 6. Dictamen Final

**DICTAMEN: APROBADO CON OBSERVACIONES**

