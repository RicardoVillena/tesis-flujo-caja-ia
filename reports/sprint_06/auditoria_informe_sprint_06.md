# Informe de Auditoría Técnica, Estadística, Financiera y Metodológica — Informe de Síntesis del Sprint 6 (`09_informe_sprint_06.ipynb`)

- **Proyecto:** `tesis-flujo-caja-ia`
- **Notebook auditado:** [`notebooks/09_informe_sprint_06.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/09_informe_sprint_06.ipynb) (`353,001` bytes; SHA-256: `68e8cc638a5bc328d1a6b495e454c9688c13baab9ab00e04a4d7dbe77f1acb22`)
- **Insumos principales verificados por el informe:**
  - Notebooks previos: [`notebooks/EDA_FCL_2005_2025.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/EDA_FCL_2005_2025.ipynb), [`notebooks/02_feature_engineering_financiero.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/02_feature_engineering_financiero.ipynb), [`notebooks/03_extraccion_macroeconomia_bcrp.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/03_extraccion_macroeconomia_bcrp.ipynb), [`notebooks/04_integracion_datos.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/04_integracion_datos.ipynb), [`notebooks/05_extraccion_bursatil.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/05_extraccion_bursatil.ipynb), [`notebooks/06_integracion_bursatil.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/06_integracion_bursatil.ipynb), [`notebooks/07_baseline_variantes.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/07_baseline_variantes.ipynb) y [`notebooks/08_mejoras_baseline.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/08_mejoras_baseline.ipynb)
  - Paneles procesados: [`data/processed/panel_fcl_preliminar.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/panel_fcl_preliminar.csv) (`4,221 × 23`), [`data/processed/features_financieras.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/features_financieras.csv) (`4,221 × 57`), [`data/processed/panel_financiero_macroeconomico.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/panel_financiero_macroeconomico.csv) (`4,221 × 62`), [`data/processed/panel_financiero_macro_bursatil.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/panel_financiero_macro_bursatil.csv) (`4,221 × 68`), [`data/processed/macroeconomia_peru_2005_2025.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/macroeconomia_peru_2005_2025.csv) (`21 × 6`) y [`data/processed/bursatil/bursatil_mercado_anual.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/bursatil/bursatil_mercado_anual.csv) (`21 × 17`)
  - Resultados y validaciones del Sprint 6: [`reports/sprint_06/validacion_baseline.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/validacion_baseline.json), [`reports/sprint_06/resultados_experimentos.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/resultados_experimentos.csv) (`36 × 14`), [`reports/sprint_06/comparacion_variantes.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/comparacion_variantes.csv) (`36 × 16`), [`reports/sprint_06/predicciones_baseline.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/predicciones_baseline.csv) (`32,040 × 13`), [`reports/sprint_06/mejoras/validacion_mejoras.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/validacion_mejoras.json), [`reports/sprint_06/mejoras/metricas_mejoras.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/metricas_mejoras.csv) (`110 × 21`), [`reports/sprint_06/mejoras/predicciones_mejoras.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/predicciones_mejoras.csv) (`127,160 × 17`), [`reports/sprint_06/mejoras/seleccion_congelada_cv.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/seleccion_congelada_cv.csv) (`5 × 12`), [`reports/sprint_06/mejoras/metricas_politica_cv.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/metricas_politica_cv.csv) (`4 × 19`) y [`reports/sprint_06/mejoras/comparacion_sector_vs07.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/comparacion_sector_vs07.csv) (`6 × 25`)
- **Entorno de verificación:** Conda `tesis-fcl` (`Python 3.12.15`, `pandas 3.0.6`, `numpy 2.5.4`, `scikit-learn 1.9.1`, `matplotlib 3.11.2`, `nbformat 5.11.1`, `nbclient 0.11.0`)
- **Rol:** Auditor independiente (sin modificación de notebooks, datasets ni resultados previos)

---

## 1. Resumen Ejecutivo

Se realizó una auditoría independiente de extremo a extremo sobre [`notebooks/09_informe_sprint_06.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/09_informe_sprint_06.ipynb), concebido como cuaderno de cierre, síntesis y verificación reproducible del Sprint 6.

| Dimensión Auditada | Estado | Resumen de Verificación |
| :--- | :---: | :--- |
| **1. Trazabilidad y conservación de fuentes (`49` archivos)** | **APROBADO** | Lee y registra con hash SHA-256 exactamente `49` fuentes del repositorio (`7` notebooks numerados `02`–`08` más `EDA_FCL_2005_2025.ipynb`, `7` informes de auditoría previos, `README.md`, diccionarios, paneles y tablas de resultados). Verifica los inventarios SHA-256 de [`validacion_baseline.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/validacion_baseline.json) y [`validacion_mejoras.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/validacion_mejoras.json), y comprueba al cierre (`hashes_previos() == hashes_iniciales`) que ningún archivo preexistente es alterado (`0` modificaciones, `0` reentrenamientos). |
| **2. Integridad de paneles y particiones (2005–2025)** | **APROBADO** | Comprueba la conservación exacta de `4,221` observaciones y `336` empresas a lo largo de las cuatro etapas del panel (`23 → 57 → 62 → 68` columnas), así como las `3,560` observaciones elegibles (`309` empresas; `2,869` en `entrenamiento` `2006–2021` y `691` en `prueba` `2022–2025`; `D lares`: `353 / 92`; `Soles`: `2,516 / 599`), la reconstrucción exacta de `objetivo_fcl_t1` en `t+1` y las `20,675` celdas financieras faltantes. |
| **3. Recálculo independiente de las `156` filas de métricas** | **APROBADO** | Recalcula desde las predicciones individuales guardadas las `36` filas de [`resultados_experimentos.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/resultados_experimentos.csv), las `110` filas de [`metricas_mejoras.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/metricas_mejoras.csv) (incluyendo `R2_OOS_media` y `R2_OOS_persistencia`), las `4` filas de [`metricas_politica_cv.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/metricas_politica_cv.csv) y las `6` filas de [`comparacion_sector_vs07.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/comparacion_sector_vs07.csv) (`36 + 110 + 4 + 6 = 156`), con coincidencia numérica exacta (`rtol=1e-11`, `atol=1e-7`). |
| **4. Verificación de validación temporal y ausencia de fuga a prueba** | **APROBADO** | Reconstruye [`seleccion_congelada_cv.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/seleccion_congelada_cv.csv) exclusivamente a partir de [`cv_por_anio.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/cv_por_anio.csv) (`1,944` filas) y [`cv_puntuaciones.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/cv_puntuaciones.csv) (`270` filas), comprobando `max(anios_train) < min(anios_validacion)` y disyunción total frente a `ids_test` (`691` filas). |
| **5. Rigor diagnóstico y transparencia sobre resultados negativos** | **APROBADO** | Documenta sin ocultamiento los $R^2$ negativos de `E0, E1, E2` en el notebook `07`, la concentración del SSE de prueba (`80.5822 %` en una sola fila de `D lares` —*Inversiones Portuarias Chancay* `2024 → 2025`— y `95.2566 %` en las `82` filas bancarias de `Soles`), la mejora en empresas no bancarias del notebook `08` ($R^2 = +0.5089$ en `D lares` y $+0.4614$ en `Soles`) y el deterioro bancario ($R^2 = -5.4853$ en `Soles / bancario`, que arrastra la política combinada de `Soles` a $R^2 = -4.5074$). |
| **6. Limitaciones metodológicas, financieras y econométricas** | **OBSERVADO** | El bloque 11 sistematiza con precisión las `8` limitaciones estructurales del Sprint (`Disponibilidad temporal: NO_VERIFICADA`, `Escala monetaria: NO_ACREDITADA`, `Objetivo financiero: APROXIMACION`, `Dimension temporal: REDUCIDA`, `Prueba independiente: PENDIENTE`, `Fuentes bursatiles: LIMITACIONES_DOCUMENTADAS`, `Identificadores: ANOMALIA_PRESERVADA` [`63` filas con `RUC` distinto de 11 dígitos] y `Dependencia y generalizacion: NO_CERTIFICADA`). Dichas limitaciones no constituyen defectos de implementación del notebook `09`, sino condiciones metodológicas abiertas del proyecto que restringen el alcance inferencial y operativo de los resultados. |
| **7. Reproducibilidad y formato documental del notebook (`12` bloques / `36` celdas)** | **APROBADO** | Ejecutado íntegramente en `tesis-fcl` (`nbclient`, `12` celdas de código con `execution_count = 1..12`, `0` excepciones). Cumple estrictamente la estructura de `36` celdas (`12` bloques de `[Markdown título+descripción] -> [Código] -> [Markdown interpretación]`, títulos `**1. ...**` a `**12. ...**` solo en negrita, `0` encabezados `#`, `1–2` líneas por celda Markdown). |

**Dictamen Final:** **APROBADO CON OBSERVACIONES** *(la síntesis, las verificaciones cruzadas, el recálculo de las 156 filas de métricas y la reproducibilidad en `tesis-fcl` son exactos e íntegros; las observaciones corresponden a las limitaciones metodológicas y de datos del Sprint 6 que el propio informe declara explícitamente y que deben resolverse en fases posteriores de la tesis).*

---

## 2. Verificaciones Aprobadas

### 2.1. Estructura de los 12 bloques y trazabilidad de 49 fuentes (Bloques 1 a 4)
1. **Protección criptográfica e inventario inicial (Bloque 1):**
   - El Bloque 1 registra los hashes SHA-256 de todos los archivos protegidos del repositorio (`README.md`, `data/`, `reports/`, `src/`, `notebooks/` excepto el propio `09_informe_sprint_06.ipynb`), inspecciona los `7` notebooks numerados (`02` a `08`) y los `7` informes de auditoría previos, y valida los inventarios SHA-256 completos de [`reports/sprint_06/validacion_baseline.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/validacion_baseline.json) y [`reports/sprint_06/mejoras/validacion_mejoras.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/validacion_mejoras.json).
   - Comprueba mediante `pd.testing.assert_frame_equal(..., check_exact=True)` la conservación bit a bit de las columnas heredadas entre [`panel_fcl_preliminar.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/panel_fcl_preliminar.csv) (`4,221 × 23`), [`features_financieras.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/features_financieras.csv) (`4,221 × 57`), [`panel_financiero_macroeconomico.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/panel_financiero_macroeconomico.csv) (`4,221 × 62`) y [`panel_financiero_macro_bursatil.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/panel_financiero_macro_bursatil.csv) (`4,221 × 68`).
2. **Síntesis del EDA y cobertura 2005–2025 (Bloque 2):**
   - Verifica la unicidad de `(RPJ, Ejercicio)` en las `4,221` filas (`336` empresas únicas, `21` ejercicios `2005–2025`), el conteo exacto de `FCL_preliminar` disponible (`3,898` registros) y faltante (`323` registros: `18` en `D lares` y `305` en `Soles`), la asimetría muestral (`1.278728` en `D lares`, `7.659767` en `Soles`) y los valores extremos por RIQ en el objetivo de entrenamiento (`52` en `D lares`, `484` en `Soles`).
3. **Feature Engineering y reconstrucción de `objetivo_fcl_t1` (Bloque 3):**
   - Comprueba que el catálogo [`reports/diccionario_integracion_bursatil.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/diccionario_integracion_bursatil.csv) describe en el mismo orden las `68` columnas del panel final, que las `22` características financieras candidatas (`8` ratios, `4` variaciones, `10` temporales) se reducen a los `19` predictores de `E0_financiero` tras excluir las `3` redundancias lineales exactas (`fcl_activo`, `FCO_mean3_previa`, `FCL_preliminar_mean3_previa`), que se preservan las `20,675` celdas financieras faltantes y que `objetivo_fcl_t1` coincide exactamente (`rtol=0, atol=0`) con `FCO(t+1) + CAPEX_reportado(t+1)` anulado cuando `CAPEX_reportado(t+1) > 0`.
4. **Integración macroeconómica y bursátil (Bloque 4):**
   - Verifica que las `5` variables macroeconómicas de [`macroeconomia_peru_2005_2025.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/macroeconomia_peru_2005_2025.csv) (`21 × 6`) y los `3` indicadores + `3` controles de [`bursatil_mercado_anual.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/bursatil/bursatil_mercado_anual.csv) (`21 × 17`) se unieron exactamente por `Ejercicio = anio` (`usa_anio_objetivo == False`), que `pbi_real_millones_soles_2007` está marcado como no predictor (`predictor_candidato == False`) y que se documentan `336` empresas consultadas en SMV, `154` emisores identificados, `0` históricos individuales descargados, `11` años con discrepancias diario/mensual y `3` montos diarios negativos originales.

### 2.2. Síntesis y recálculo de experimentos `E0`, `E1`, `E2` y diagnóstico del `07` (Bloques 5 a 9)
1. **Recálculo exacto de las 36 filas del notebook `07` (Bloque 5):**
   - Verifica las `32,040` predicciones de [`predicciones_baseline.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/predicciones_baseline.csv), confirma la ausencia de duplicados en `(escenario, moneda, experimento, id_fila)` y recalcula `MAE`, `RMSE` y `R2` para las `36` filas de [`resultados_experimentos.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/resultados_experimentos.csv) con tolerancia estricta (`rtol=1e-11`, `atol=1e-7`).
2. **Comparación entre variantes `E0`, `E1` y `E2` (Bloques 6, 7 y 8):**
   - Comprueba las mejoras porcentuales de [`comparacion_variantes.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/comparacion_variantes.csv) (`rtol=1e-12`) y la identidad exacta de los conjuntos `id_fila` entre `E0_financiero` (`19` predictores), `E1_macroeconomico` (`23` predictores) y `E2_bursatil` (`26` predictores):

| Moneda | Experimento | $p$ | $n_{\text{test}}$ | $\text{MAE}_{\text{test}}$ | $\text{RMSE}_{\text{test}}$ | $R^2_{\text{test}}$ | $\Delta\text{MAE vs E0}$ | $\Delta\text{RMSE vs E0}$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `D lares` | `E0_financiero` | 19 | 92 | `228,054.3656` | `804,755.4557` | `-2.0305` | `0.000 %` | `0.000 %` |
| `D lares` | `E1_macroeconomico` | 23 | 92 | `317,991.4029` | `1,343,050.2583` | `-7.4405` | `-39.437 %` | `-66.889 %` |
| `D lares` | `E2_bursatil` | 26 | 92 | `237,509.5735` | `759,493.1332` | `-1.6992` | `-4.146 %` | `+5.624 %` |
| `Soles` | `E0_financiero` | 19 | 599 | `379,977.4371` | `1,424,709.0675` | `-1.4901` | `0.000 %` | `0.000 %` |
| `Soles` | `E1_macroeconomico` | 23 | 599 | `442,301.8671` | `1,445,745.2842` | `-1.5642` | `-16.402 %` | `-1.476 %` |
| `Soles` | `E2_bursatil` | 26 | 599 | `426,780.0103` | `1,438,296.5572` | `-1.5379` | `-12.317 %` | `-0.954 %` |

3. **Diagnóstico de concentración de errores y colinealidad (Bloque 9):**
   - Cuantifica directamente sobre las predicciones de prueba de `E0_financiero` que:
     - En `D lares` (`n = 92`, `0` bancos), una sola observación (`RPJ = L02127`, *Inversiones Portuarias Chancay S.A.A.*, `Ejercicio = 2024 → 2025`, con `crecimiento_ActivoTotal = 486.40264`, `y_real = 0.0` y `y_predicho = 6,929,110.8`) explica el **`80.5822 %`** del SSE total de prueba.
     - En `Soles` (`n = 599`), las `82` observaciones de `TipoSector == "BANCOS"` concentran el **`95.2566 %`** del SSE total de prueba, y el mayor residuo individual (`RPJ = B80004`, *Banco BBVA Perú*, `Ejercicio = 2022 → 2023`, `y_real = 686,948.0`, `y_predicho = 17,571,069.5`) explica el **`23.4465 %`** del SSE total de `Soles`.
   - Comprueba además en [`diagnostico_colinealidad.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/diagnostico_colinealidad.csv) que las matrices de diseño mantienen rango completo (`19/19`, `23/23`, `26/26`) con números de condición moderados en `D lares` (`13.822–14.008`) y elevados pero no singulares en `Soles` (`210.546–221.434`).

### 2.3. Verificación de las mejoras del `08`, validación temporal y cierre reproducible (Bloques 10 a 12)
1. **Recálculo completo de métricas y selección congelada por CV (Bloque 10):**
   - Comprueba las `495` filas de [`umbrales_clipping.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/umbrales_clipping.csv) (`45` modelos Ridge × `11` variables recortadas), recalcula las `110` filas de [`metricas_mejoras.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/metricas_mejoras.csv) (incluyendo la verificación exacta de `SSE_media`, `SSE_persistencia`, `R2_OOS_media` y `R2_OOS_persistencia` a partir de las predicciones ingenuas), re-deriva [`seleccion_congelada_cv.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/seleccion_congelada_cv.csv) desde [`cv_por_anio.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/cv_por_anio.csv) y [`cv_puntuaciones.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/cv_puntuaciones.csv) (`pd.testing.assert_frame_equal(..., check_exact=True)`), y recalcula las `4` filas de [`metricas_politica_cv.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/metricas_politica_cv.csv) y las `6` filas de [`comparacion_sector_vs07.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/mejoras/comparacion_sector_vs07.csv):

| Cohorte (`prueba 2022–2025`) | $n$ | Especificación ganadora en CV | $\alpha_{\text{CV}}$ | $\text{MAE}_{07}$ | $\text{MAE}_{08}$ | $\text{RMSE}_{07}$ | $\text{RMSE}_{08}$ | $R^2_{07}$ | $R^2_{08}$ | $R^2_{\text{OOS, media}}$ | $R^2_{\text{OOS, persist.}}$ |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `D lares / no_bancario` | 92 | `niveles_t_externos_t_1` (`E1`) | `1000.0` | `228,054.37` | `147,873.25` | `804,755.46` | `323,976.81` | `-2.0305` | `+0.5089` | `+0.5141` | `+0.1185` |
| `Soles / no_bancario` | 517 | `sin_niveles_t_externos_t_1` (`E2`) | `1000.0` | `127,331.49` | `124,751.25` | `333,996.15` | `280,239.20` | `+0.2349` | `+0.4614` | `+0.4811` | `+0.4480` |
| `Soles / bancario` | 82 | `niveles_t_externos_t_1` (`E1`) | `10.0` | `1,972,879.48` | `4,299,570.40` | `3,758,202.31` | `5,683,160.61` | `-1.8360` | `-5.4853` | `-5.4850` | `-2.3277` |
| **Política combinada `D lares`** | **92** | `no_bancario` (`n=92`) + `bancario` (`n=0`) | — | `228,054.37` | `147,873.25` | `804,755.46` | `323,976.81` | `-2.0305` | **`+0.5089`** | **`+0.5141`** | **`+0.1185`** |
| **Política combinada `Soles`** | **599** | `no_bancario` (`n=517`) + `bancario` (`n=82`) | — | `379,977.44` | `696,262.31` | `1,424,709.07` | `2,118,785.62` | `-1.4901` | **`-4.5074`** | **`-4.4558`** | **`-2.0929`** |

2. **Sistematización de limitaciones y cierre sin efectos secundarios (Bloques 11 y 12):**
   - El Bloque 11 verifica programáticamente las banderas de estado (`disponibilidad_real_historica == "NO_VERIFICADA"`, `disponibilidad_temporal_real == "NO_VERIFICADA"`, `prueba_independiente_del_rediseño == False`, `escala_monetaria == "NO_ACREDITADA"`, `ruc_no11 == 63`) y resume la estructura de los pliegues de CV (`4` folds en `D lares` y `Soles / no_bancario`, `2` folds en `Soles / bancario`).
   - El Bloque 12 verifica que se ejecutaron las `12` secciones, que se recalcularon las `156` filas de métricas, que se leyeron `49` archivos fuente sin cambios de hash SHA-256 y que `hashes_previos() == hashes_iniciales`.

---

## 3. Errores Críticos

**Ninguno (`0` errores críticos).**
No se detectaron discrepancias numéricas, fugas de información, alteraciones de archivos previos, omisiones de resultados adversos ni errores de ejecución en [`notebooks/09_informe_sprint_06.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/09_informe_sprint_06.ipynb).

---

## 4. Errores Importantes

**Ninguno (`0` errores importantes en la elaboración del informe).**
El notebook sintetiza con exactitud tanto los avances como los resultados negativos del Sprint 6 y respeta rigurosamente las restricciones de solo lectura y verificación independiente.

---

## 5. Observaciones Menores y Condiciones Metodológicas Documentadas

1. **Condiciones metodológicas abiertas del Sprint 6 (documentadas explícitamente en el Bloque 11 — `OBSERVADO`):**
   - El propio cuaderno registra en su tabla `limitaciones` ocho condiciones estructurales del proyecto que permanecen abiertas al cierre del Sprint 6:
     1. **`Disponibilidad temporal` (`NO_VERIFICADA`):** ausencia de fechas exactas de publicación de EE.FF. auditados SMV y de *vintages* históricos en tiempo real para las series macroeconómicas/bursátiles.
     2. **`Escala monetaria` (`NO_ACREDITADA`):** la fuente primaria no certifica explícitamente si los importes están expresados en unidades o miles de `Soles`/`D lares`, ni existe deflactación u homogeneización previa de escala en la variable objetivo.
     3. **`Objetivo financiero` (`APROXIMACION`):** `FCL_preliminar = FCO + CAPEX_reportado` (con anulación si `CAPEX_reportado > 0`) es un proxy contable preliminar y resulta estructuralmente inadecuado para `TipoSector == "BANCOS"`.
     4. **`Dimension temporal` (`REDUCIDA`):** `16` años de entrenamiento general (`2006–2021`) y solo `9` años efectivos en `Soles / bancario` (`2013–2021`, `2` pliegues de CV con `n_train_min = 93` y `n_val = 79`), lo que explica la inestabilidad de `alpha = 10.0` en la cohorte bancaria.
     5. **`Prueba independiente` (`PENDIENTE`):** dado que la partición `prueba` (`2022–2025`) ya había sido inspeccionada en el notebook `07` antes de diseñar el espacio de hipótesis del `08`, los resultados del `08` tienen carácter retrospectivo/exploratorio hasta contar con una muestra de confirmación externa o prospectiva.
     6. **`Fuentes bursatiles` (`LIMITACIONES_DOCUMENTADAS`):** empalme histórico IGBVL/S&P-BVL en 2015, `11` años con discrepancias diario/mensual, `3` montos diarios negativos en la fuente BCRP y `0` series de precios accionarios individuales descargadas.
     7. **`Identificadores` (`ANOMALIA_PRESERVADA`):** `63` filas del panel (`4` empresas: `B80004`, `B80019`, `J00041`, `OEF003`) conservan valores de `RUC` de 5–8 dígitos distintos del estándar de 11 dígitos, aunque `RPJ` mantiene unicidad e integridad completas.
     8. **`Dependencia y generalizacion` (`NO_CERTIFICADA`):** la presencia de empresas repetidas longitudinalmente y predictores anuales comunes induce correlación transversal y serial de los errores de predicción; no se reportan intervalos de confianza ni pruebas de significancia predictiva (p. ej., Diebold-Mariano con errores agrupados por año/empresa).
2. **Almacenamiento exclusivamente en memoria del diccionario `verificacion_reporte` (Bloque 12 — `OBSERVADO`):**
   - En la Celda 34 (Bloque 12), el cuaderno construye el diccionario `verificacion_reporte` con el resumen de las `12` secciones, `156` filas de métricas recalculadas y los hashes SHA-256 de las `49` fuentes leídas, sin exportarlo a disco. Esta decisión es coherente con la restricción de no crear ni modificar archivos en `reports/sprint_06/`, quedando la evidencia persistida en las salidas ejecutadas del propio `.ipynb`.

---

## 6. Auditoría de Reproducibilidad y Documentación

1. **Ejecución en el entorno Conda `tesis-fcl`:**
   - Se ejecutó [`notebooks/09_informe_sprint_06.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/09_informe_sprint_06.ipynb) de principio a fin en un directorio temporal aislado mediante `/home/ricardo/miniconda3/envs/tesis-fcl/bin/python` (`nbclient`).
   - Las `12` celdas de código finalizaron con código de salida `0`, sin excepciones ni advertencias, reproduciendo exactamente la salida final:
     - `Secciones verificadas: 12 | Celdas de codigo: 12 | Filas de metricas recalculadas: 156`
     - `Fuentes leidas: 49 | Entrenamientos: 0 | Modificaciones de archivos anteriores: 0`
2. **Cumplimiento del estándar documental (`36` celdas = `12` bloques):**
   - Cada uno de los `12` bloques sigue estrictamente el patrón `[Markdown título+descripción] -> [Código] -> [Markdown interpretación]`.
   - Todos los títulos están numerados exclusivamente en negrita (`**1. Objetivo y descripción del conjunto de datos**` hasta `**12. Conclusiones y reproducibilidad del informe**`), sin encabezados Markdown (`#`, `##`, `###`) ni viñetas, con descripciones previas e interpretaciones posteriores de `1` línea (`2` oraciones concisas) alineadas con los resultados numéricos e incluyendo `3` figuras embebidas (cobertura anual en Bloque 2 y comparaciones de `MAE`, `RMSE` y `R2` por moneda en Bloque 8).

---

## 7. Recomendaciones para el Siguiente Sprint

1. **Separación estructural entre empresas corporativas no financieras y entidades bancarias:** adoptar formalmente el universo corporativo no bancario (`TipoSector != "BANCOS"`) como dominio principal para el modelado de `FCL`, o bien definir un objetivo específico de flujo de patrimonio/dividendos para intermediarios financieros.
2. **Re-escalamiento de la variable objetivo por tamaño empresarial:** evaluar la predicción de `FCL(t+1) / ActivoTotal(t)` (con reconstrucción posterior a unidades monetarias o evaluación en ratio) y/o estimadores con pérdida robusta (`HuberRegressor`, `QuantileRegressor`) para evitar que la función de pérdida cuadrática de `Ridge` sea dominada por un reducido número de megacorporaciones.
3. **Inferencia formal sobre diferencias de capacidad predictiva:** incorporar pruebas de Diebold-Mariano o *block bootstrap* agrupado por año/empresa para contrastar estadísticamente si las mejoras de `RMSE` y `MAE` en las cohortes no bancarias son significativas frente a los benchmarks ingenuos (`media_train` y `persistencia_t`).

---

## 8. Dictamen Final

- **Estado de la auditoría de [`notebooks/09_informe_sprint_06.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/09_informe_sprint_06.ipynb):** **APROBADO CON OBSERVACIONES**
- **Justificación:** El notebook [`notebooks/09_informe_sprint_06.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/09_informe_sprint_06.ipynb) cumple cabalmente su función de informe reproducible de cierre del Sprint 6: verifica criptográficamente `49` fuentes del repositorio, recalcula sin error las `156` filas de métricas de los notebooks `07` y `08` a partir de las predicciones guardadas, comprueba la ausencia de fuga de información de prueba en la selección por validación cruzada temporal, reporta con transparencia tanto las mejoras no bancarias como el deterioro bancario, documenta las `8` limitaciones metodológicas abiertas del Sprint y se ejecuta limpiamente en el entorno `tesis-fcl` sin modificar ningún archivo previo.

