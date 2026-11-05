# Informe de Auditoría Independiente — Sprint 09 (Variantes E0–E4, Importancia, Alineación y Experimento Final)

**Fecha de auditoría:** 4 de noviembre de 2026  
**Proyecto:** `tesis-flujo-caja-ia`  
**Rama evaluada:** `sprint-09-variantes-importancia` (commits `6eeac16` a `8239c27`)  
**Alcance:**
- **Etapa 1 (Variantes E0–E4, sensibilidad $t-1$ e importancia de variables):** [`src/variantes_importancia.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/variantes_importancia.py), [`reports/sprint_09/informe_sprint_09.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/informe_sprint_09.md), [`reports/sprint_09/matriz_consistencia.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/matriz_consistencia.md), [`reports/sprint_09/matriz_operacionalizacion.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/matriz_operacionalizacion.md).
- **Etapa 2 (Alineación con el plan de tesis y población no financiera):** [`src/alineacion_investigacion.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/alineacion_investigacion.py), [`reports/sprint_09/alineacion_investigacion/informe_alineacion.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/alineacion_investigacion/informe_alineacion.md).
- **Etapa 3 (Experimento final: formulaciones directa, corrección de persistencia y relativa; pérdida cuadrática y absoluta):** [`src/experimento_final.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/experimento_final.py), [`src/importancia_procedimiento_final.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/importancia_procedimiento_final.py), [`reports/sprint_09/experimento_final/resumen_tecnico.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/experimento_final/resumen_tecnico.md), [`notebooks/sprint_09/14_presentacion_resultados.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/sprint_09/14_presentacion_resultados.ipynb).

---

## 1. Resumen de Verificaciones

| Dimensión Auditada | Verificación | Estado | Evidencia |
|---|---|---|---|
| **1. Protocolos congelados antes de ejecutar** | Verificación de SHA-256 en las 3 subetapas del Sprint 09 | **APROBADO** | [`sprint_09/protocolo.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/protocolo.json) (`5b69af83…`), [`alineacion_investigacion/protocolo.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/alineacion_investigacion/protocolo.json) (`99fee593…`), [`experimento_final/protocolo.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/experimento_final/protocolo.json) (`c2430bd4…`) |
| **2. Aislamiento temporal y de prueba (`2022–2025`)** | Toda la experimentación usa únicamente entrenamiento (`anio_objetivo <= 2021`); años externos `2017–2021` con búsqueda interna estrictamente anterior | **APROBADO** | [`test_sprint_09.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_sprint_09.py) (`10/10`), [`test_alineacion_investigacion.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_alineacion_investigacion.py) (`9/9`), [`test_experimento_final.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_experimento_final.py) (`9/9`) |
| **3. Recálculo independiente de métricas** | Recálculo de `RMSE` y `MAE` desde las `25,308` filas de [`experimento_final/predicciones.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/experimento_final/predicciones.csv) contra las `380` filas de [`metricas_por_anio.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/experimento_final/metricas_por_anio.csv) | **APROBADO** | Diferencia máxima: `6.33e-08` en RMSE y `3.73e-09` en MAE |
| **4. Reproducción exacta entre etapas** | Consistencia numérica con Sprint 08, versión inicial `6eeac16` y etapa de alineación | **APROBADO** | Diferencia relativa máxima $\le 4.82 \times 10^{-15}$ en [`verificacion_reproduccion.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/experimento_final/verificacion_reproduccion.json) |
| **5. Metodología de importancia de variables** | Retirada de atributos individuales y por bloques (sin permutar variables macro/bursátiles dentro del mismo año, donde son constantes) y reajuste con hiperparámetros congelados | **APROBADO** | [`importancia_bloques.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/importancia_bloques.csv), [`importancia_individual.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/importancia_individual.csv) |
| **6. Ejecución de [`14_presentacion_resultados.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/sprint_09/14_presentacion_resultados.ipynb)** | `40` celdas (`24` Markdown, `16` código), ejecución lineal `1..16` sin errores | **OBSERVADO** | Celdas `[32]` y `[33]` son código consecutivo sin Markdown intermedio; no listado aún en [`notebooks/README.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/README.md) |

---

## 2. Errores Críticos

- **Ninguno (`0`).**

---

## 3. Observaciones Importantes

1. **Inestabilidad de la formulación relativa al activo en soles (OBSERVADO — Documentado):**
   - En [`experimento_final/resumen_tecnico.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/experimento_final/resumen_tecnico.md#L33), la formulación relativa con pérdida cuadrática explota en soles (`RMSE` de `2.0` a `6.0` millones frente a `0.26–0.29` millones de la formulación directa) debido a denominadores casi nulos (`FOSSAL 2017`, ratio `385`) multiplicados por activos grandes o con salto de escala (`CD0009 2016`). Está correctamente declarada como diagnóstica y no validada económicamente.
2. **Multiplicidad de comparaciones en el Experimento Final (OBSERVADO — Documentado):**
   - En [`experimento_final`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/experimento_final/resumen_tecnico.md#L18) se evalúan `36` procedimientos modelados por moneda y `312` comparaciones pareadas totales. Que `persistencia|boosting_abs:E1` supere a la persistencia simple en ambas monedas (`-1.75%` en dólares, `5/5` años; `-1.06%` en soles, `4/5` años) tiene márgenes cercanos al umbral del `1%` y debe presentarse como hallazgo exploratorio sujeto a confirmación independiente.
3. **Advertencia de derechos de redistribución en repositorio público (OBSERVADO — Documentado):**
   - Como advierte [`reports/sprint_09/verificacion.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/verificacion.md#L58), el push del commit `ecf7f16` publicó archivos en `data/raw/` (documentos empresariales PDF/texto y tablas de Damodaran/BCRP/BVL) cuya licencia de redistribución pública no está acreditada (a diferencia de ODbL para SMV).

---

## 4. Observaciones Menores

1. **Omisión en el índice de notebooks:** [`notebooks/README.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/README.md) no incluye la sección correspondiente a `notebooks/sprint_09/14_presentacion_resultados.ipynb`.
2. **Formato de celdas en el notebook 14:** En [`14_presentacion_resultados.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/sprint_09/14_presentacion_resultados.ipynb), las celdas `[32]` y `[33]` aparecen seguidas sin celda Markdown intermedia y el kernel en metadatos figura como `python3` en lugar de `tesis-fcl`.

---

## 5. Resultados Clave Verificados

1. **Panel completo (Etapa 1 — 119 filas en dólares, 829 en soles):**
   - Ni el bloque macroeconómico ($H_1$) ni el bloque bursátil ($H_2$) ni la selección interna E4 ($H_{4b}$) cumplen la regla de mejora consistente frente a usar solo variables financieras (`E0`).
   - El único bloque con aporte predictivo estable es el **bloque financiero** (rezagos y desviación estándar histórica de `FCO` y `FCL`).
2. **Población no financiera y corrección de persistencia (Etapa 3 — 119 filas en dólares, 547 en soles):**
   - Cambiar de predicción directa a **corrección de persistencia** con `HistGradientBoosting` de pérdida absoluta (`persistencia|boosting_abs`) reduce el `RMSE` anual medio entre `15.7%` y `16.8%` en dólares y entre `7.3%` y `8.7%` en soles (`5/5` años).
   - `persistencia|boosting_abs:E1` logra superar de forma consistente a la persistencia simple en ambas monedas (`-1.75%` en dólares y `-1.06%` en soles), manteniendo y ampliando su ventaja al excluir la empresa dominante (`-2.78%` en dólares sin `CM0006`; `-2.07%` en soles sin `CM0004`).

---

## 6. Dictamen Final

**DICTAMEN: APROBADO CON OBSERVACIONES**

