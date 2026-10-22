# Auditoría Independiente — Experimentos Predictivos Baseline y Variantes (Sprint 6)

**Proyecto:** `tesis-flujo-caja-ia` (Maestría en Inteligencia Artificial — UNI)  
**Notebook auditado:** `notebooks/07_baseline_variantes.ipynb` (`661,876` bytes; `51` celdas; SHA-256: `5cbdbb1ee2bf1a247ed874d3a867cc4dc4148314800c6ee4f2756bd8da87e9a5`)  
**Panel de entrada:** `data/processed/panel_financiero_macro_bursatil.csv` (`4,221` filas × `68` columnas; SHA-256: `e3fb1df034db346a34a5d62196387687eb5e7f890f32461df665fa6261425d08`)  
**Entorno verificado:** Conda `tesis-fcl` (`Python 3.12.15`, `pandas 3.0.1`, `numpy 2.4.3`, `scikit-learn 1.8.0`, `matplotlib 3.10.8`, `nbformat 5.10.4`, `nbclient 0.10.4`)  
**Fecha de auditoría:** 21 de octubre de 2026  

---

## 1. Resumen ejecutivo

- **Veredicto global:** **APROBADO CON OBSERVACIONES METODOLÓGICAS Y ECONOMÉTRICAS SUSTANTIVAS** (implementación computacional, prevención de fuga de información, trazabilidad y reproducibilidad **100 % conformes**; especificación funcional y financiera del modelo lineal en niveles nominales **requiere correcciones en sprints posteriores** para superar el desempeño de predictores ingenuos fuera de muestra).
- **Exactitud numérica y reproducibilidad:** Las 17 celdas de código de `notebooks/07_baseline_variantes.ipynb` se ejecutaron íntegramente sin errores en un entorno aislado con el kernel `tesis-fcl`. Los 8 archivos CSV de salida y `resumen_experimentos.md` en `reports/sprint_06/` se regeneraron con **hashes SHA-256 idénticos bit a bit (`100 %`)**, y el recálculo independiente de las 36 filas de `resultados_experimentos.csv` y `comparacion_variantes.csv` a partir de las `32,040` predicciones de `predicciones_baseline.csv` arrojó discrepancias máximas de orden `1e-10` a `1e-15` (precisión de punto flotante IEEE 754).
- **Ausencia de fuga de información (*data leakage*):** La partición temporal (`anio_objetivo <= 2021` para entrenamiento y `anio_objetivo >= 2022` para prueba) se respeta estrictamente. Los transformadores `SimpleImputer(strategy="median")` y `StandardScaler` / `RobustScaler` están encapsulados dentro de `ColumnTransformer` y `Pipeline` y se ajustan exclusivamente sobre `entrenamiento`. Además, el escenario `rezago_externo_t_1` corrige el solapamiento de publicación de indicadores macroeconómicos y bursátiles asignando a `Ejercicio = t` la información externa de `t - 1`.
- **Hallazgo central sobre los $R^2$ negativos en prueba (`-1.4901` a `-7.4405`):** La auditoría demostró empíricamente que los valores negativos de $R^2$ en prueba **no provienen de errores de código ni de fuga de datos**, sino de la combinación de cuatro causas estructurales cuantificadas:
  1. **Sensibilidad extrema de un modelo lineal (`Ridge`) a *outliers* en ratios de crecimiento no acotados (`D lares`):** Una sola observación de prueba (`RPJ = L02127`, *Inversiones Portuarias Chancay S.A.A.*, `Ejercicio = 2024 -> anio_objetivo = 2025`), cuyo activo saltó de `303` a `147,683` miles de USD (`crecimiento_ActivoTotal = 486.4026`, equivalente a **$+1,169.50$ desviaciones estándar de entrenamiento**), genera predicciones de `+6,929,110.8` (`E0`), `+12,394,309.7` (`E1`) y `+6,411,401.2` (`E2`) frente a un valor real `y_real = 0.0`. **Esta única observación (`1.09 %` de la muestra de prueba en dólares) explica el `80.58 %` (`E0`), `92.57 %` (`E1`) y `77.46 %` (`E2`) de toda la suma de cuadrados del error (`SSE`) en dólares.** Al excluir únicamente esa observación (`n = 91`), el $R^2$ de prueba en `D lares` pasa a ser **positivo en los tres experimentos (`+0.4110` en `E0`, `+0.3723` en `E1` y `+0.4178` en `E2`)**, y al excluir los 3 mayores errores (`L02127` en 2024 y dos ejercicios de crisis de `PETROPERU` en 2021 y 2023), el $R^2$ en `D lares` alcanza **`+0.7157` (`E0`), `+0.6842` (`E1`) y `+0.7088` (`E2`)**.
  2. **Inclusión del sector `BANCOS` bajo una definición de FCL industrial inaplicable a intermediarios financieros (`Soles`):** En `Soles` (`n = 599` en prueba), las `82` observaciones del sector `BANCOS` (`13.69 %` de la muestra) concentran el **`95.26 %` (`E0`), `94.53 %` (`E1`) y `94.71 %` (`E2`) de todo el `SSE` de prueba**, debido a que los flujos de depósitos, colocaciones y operaciones de reporte con el BCRP (*Reactiva Perú* 2020–2023) se contabilizan en el `FCO` bancario. En los otros 6 sectores no bancarios (`n = 517` observaciones de prueba en `Soles`), **el $R^2$ de prueba es positivo en los tres experimentos (`+0.2349` en `E0`, `+0.0916` en `E1` y `+0.1302` en `E2`)**.
  3. **Omisión del nivel contemporáneo `FCL_preliminar(t)` / `FCO(t)` y asimetría de escala:** El vector de 19 predictores incluye rezagos en niveles monetarios de $t-1, t-2, t-3$ (`FCO_lag1..3`, `FCL_preliminar_lag1..3`), pero representa el año $t$ únicamente mediante ratios adimensionales (`fco_activo`, `inversion_capex_activo`), omitiendo el nivel monetario del año $t$ (`FCL_preliminar` o `FCO`) para predecir el nivel monetario `objetivo_fcl_t1` en $t+1$. Un predictor ingenuo de persistencia $\hat{y}_{t+1} = \text{FCL\_preliminar}_t$ alcanza en `D lares` un **`MAE = 150,235.04`, `RMSE = 345,072.95` y `R2 = +0.4428`**, superando ampliamente a `E0`, `E1` y `E2`.
  4. **Extrapolación lineal fuera de soporte (*covariate shift*) en `tipo_cambio_promedio_soles_usd` (`100 %` de la muestra de prueba `2021–2024` por encima del máximo histórico de entrenamiento `2005–2020`) y grados de libertad temporales limitados (`16` años de entrenamiento para `4` a `7` variables anuales):** Explica el deterioro sistemático de `E1_macroeconomico` frente a `E0_financiero` en el escenario `principal` y la mejora sustancial de `E2_bursatil` en `D lares` cuando se rezagan las variables externas un año (`rezago_externo_t_1`: `RMSE` cae de `804,755.46` a `607,698.96`, mejora de `+24.49 %`).

---

## 2. Auditoría de datos y particiones

### 2.1 Verificación de integridad, elegibilidad y particiones

| Subconjunto / Verificación | Filas esperadas | Filas auditadas | Empresas (`RPJ`) | Años `Ejercicio` (`t`) | Años `anio_objetivo` (`t+1`) | Estado |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Panel integrado total (`panel_financiero_macro_bursatil.csv`) | `4,221` | `4,221` | `336` | `2005–2025` | `2006–2026` (o `NaN`) | **CONFORME** |
| Subconjunto elegible (`utilizable_supervisado == True`) | `3,560` | `3,560` | `309` | `2005–2024` | `2006–2025` | **CONFORME** |
| No elegibles (`sin_etiqueta_elegible`) | `661` | `661` | `336` | `2005–2025` | Sin par contiguo / `CAPEX > 0` | **CONFORME** |
| Partición `entrenamiento` (Total) | `2,869` | `2,869` | `302` | `2005–2020` | `2006–2021` | **CONFORME** |
| Partición `prueba` (Total) | `691` | `691` | `187` | `2021–2024` | `2022–2025` | **CONFORME** |
| `D lares` — `entrenamiento` | `353` | `353` | `49` | `2005–2020` | `2006–2021` | **CONFORME** |
| `D lares` — `prueba` | `92` | `92` | `26` | `2021–2024` | `2022–2025` | **CONFORME** |
| `Soles` — `entrenamiento` | `2,516` | `2,516` | `269` | `2005–2020` | `2006–2021` | **CONFORME** |
| `Soles` — `prueba` | `599` | `599` | `161` | `2021–2024` | `2022–2025` | **CONFORME** |

### 2.2 Verificación de llaves, unidades monetarias y correspondencia temporal ($t \to t+1$)

1. **Ausencia de duplicados y objetivos faltantes:** En las `3,560` observaciones elegibles existen `0` duplicados en la llave `(RPJ, Ejercicio)` y `0` valores nulos en `objetivo_fcl_t1`.
2. **Correspondencia exacta $t \to t+1$:** Para las `3,560` observaciones elegibles se verificó que `anio_objetivo == Ejercicio + 1`, `moneda_objetivo == Moneda` (`100 %` consistencia de moneda entre año predictor $t$ y año objetivo $t+1$), y que `objetivo_fcl_t1` coincide exactamente (`diff = 0.0`) con el `FCL_preliminar` registrado para la misma empresa (`RPJ`) y moneda en `Ejercicio = t + 1`.
3. **Evaluación de `objetivo_fcl_t1`:** La variable objetivo se construye como `FCL_preliminar(t+1) = FCO(t+1) + CAPEX_reportado(t+1)` únicamente cuando `CAPEX_reportado(t+1) <= 0` y existe ejercicio contiguo en la misma moneda. Como se documentó desde la auditoría de la Semana 5 y se preserva correctamente en `07_baseline_variantes.ipynb`, **`objetivo_fcl_t1` constituye una aproximación contable preliminar de flujo de caja libre operativo neto de CAPEX y no un *Free Cash Flow to the Firm* (`FCFF`) financiero depurado**, ya que el estado de flujos de efectivo SMV varía en el tratamiento de intereses pagados/recibidos, dividendos e impuestos según la empresa y el sector (especialmente en `BANCOS` y `SEGUROS`).

---

## 3. Auditoría del diseño experimental

### 3.1 Definición de los conjuntos de predictores (`E0`, `E1`, `E2`)

El notebook parte de las 22 características financieras de la Semana 5 y documenta en `diagnostico_colinealidad.csv` tres identidades lineales exactas ($\text{error máximo} = 0.0$):
- `fcl_activo = fco_activo - inversion_capex_activo`
- `FCO_mean3_previa = (FCO_lag1 + FCO_lag2 + FCO_lag3) / 3`
- `FCL_preliminar_mean3_previa = (FCL_preliminar_lag1 + FCL_preliminar_lag2 + FCL_preliminar_lag3) / 3`

Al excluir estas 3 columnas redundantes para evitar colinealidad perfecta en la matriz de diseño, los tres experimentos quedan conformados así:

| Experimento | N° predictores | Bloques incluidos | Detalle de variables predictoras (`X`) |
| :--- | :---: | :--- | :--- |
| `E0_financiero` | `19` | Financiero depurado (`19`) | **Ratios (`7`):** `pasivo_activo`, `margen_neto`, `rentabilidad_activo_cierre`, `rotacion_activo_cierre`, `fco_activo`, `fco_ingresos`, `inversion_capex_activo`. **Variaciones (`4`):** `crecimiento_ActivoTotal`, `crecimiento_TotalIngreso`, `cambio_FCO_activo_previo`, `cambio_FCL_preliminar_activo_previo`. **Temporales (`8`):** `FCO_lag1`, `FCO_lag2`, `FCO_lag3`, `FCO_std3_previa`, `FCL_preliminar_lag1`, `FCL_preliminar_lag2`, `FCL_preliminar_lag3`, `FCL_preliminar_std3_previa`. |
| `E1_macroeconomico` | `23` | Financiero (`19`) + Macro BCRP (`4`) | `E0_financiero` + `crecimiento_pbi_real_pct`, `inflacion_lima_dic_dic_pct`, `tipo_cambio_promedio_soles_usd`, `tasa_referencia_promedio_pct`. (Se excluye correctamente `pbi_real_millones_soles_2007` por tendencia determinística). |
| `E2_bursatil` | `26` | Financiero (`19`) + Macro (`4`) + Bursátil BVL (`3`) | `E1_macroeconomico` + `rentabilidad_indice_anual_pct`, `volatilidad_diaria_anualizada_pct`, `monto_renta_variable_anual_millones_pen`. |

### 3.2 Verificación de comparabilidad y aislamiento experimental

- **Mismo estimador e hiperparámetros:** Los 18 modelos (`3` escenarios × `2` monedas × `3` experimentos) utilizan `Ridge(alpha=1.0, solver="svd", fit_intercept=True)` sin búsqueda de hiperparámetros sobre prueba.
- **Mismas observaciones:** Dentro de cada moneda (`D lares`: `353` train / `92` test; `Soles`: `2,516` train / `599` test), `E0`, `E1` y `E2` se entrenan y evalúan exactamente sobre las mismas filas (`id_fila` idénticos).
- **Exclusión de variables prohibidas:** Se comprobó que ninguna variable objetivo (`objetivo_fcl_t1`, `anio_objetivo`, `moneda_objetivo`), ningún identificador (`RPJ`, `RUC`, `NombreEmpresa`, `CIIU`) ni ninguna bandera diagnóstica (`revision_interanual`, `estado_FCL`, `capex_signo_revisar`, `transicion_metodologica_2015`, `diferencia_diario_mensual_revisar`) ingresa en `X`. No se incluyen variables categóricas, por lo que todas las columnas de `X` son numéricas (`float64`).

---

## 4. Auditoría de fuga de información

| Verificación de *Data Leakage* | Evidencia técnica verificada | Estado |
| :--- | :--- | :---: |
| **1. Separación temporal estricta** | `entrenamiento` contiene únicamente `Ejercicio` `2005–2020` (`anio_objetivo` `2006–2021`); `prueba` contiene únicamente `Ejercicio` `2021–2024` (`anio_objetivo` `2022–2025`). El último objetivo de entrenamiento (`2021`) precede al primer objetivo de prueba (`2022`). | **CONFORME** |
| **2. Ausencia de información de $t+1$ en `X`** | Todos los predictores financieros corresponden al cierre de `Ejercicio = t` o rezagos `t-1, t-2, t-3` dentro de la misma empresa y moneda. | **CONFORME** |
| **3. Ajuste de imputadores y escaladores** | En el bloque 10 (`ejecutar_escenario`), `pipe.fit(X_tr, y_tr)` ajusta `SimpleImputer(strategy="median")` y `StandardScaler` / `RobustScaler` exclusivamente sobre `X_tr`. `diagnostico_entrenamiento.csv` coincide exactamente con las medianas, medias y desviaciones estándar poblacionales (`ddof=0`) de `entrenamiento`. | **CONFORME** |
| **4. Selección de variables** | La exclusión de las 3 identidades lineales exactas (`fcl_activo`, `FCO_mean3_previa`, `FCL_preliminar_mean3_previa`) y de `pbi_real_millones_soles_2007` responde a criterios algebraicos y econométricos *a priori*, sin usar métricas de `prueba`. | **CONFORME** |
| **5. Disponibilidad histórica de variables externas** | En el escenario `principal`, las variables macro y bursátiles del año `t` están cerradas al 31 de diciembre de `t` (antes del cierre de `objetivo_fcl_t1` en `t+1`), aunque el PBI anual definitivo del BCRP se publica con rezago en `t+1`. El escenario `rezago_externo_t_1` vincula a `Ejercicio = t` los indicadores externos de `t - 1` (`147` filas de `2005` quedan sin `t - 1 = 2004` y se imputan con la mediana de entrenamiento sin fuga). | **CONFORME** |

### Evaluación de empresas repetidas entre entrenamiento y prueba (diseño longitudinal)

La auditoría cuantificó el solapamiento de empresas (`RPJ`) entre `entrenamiento` (`2005–2020`) y `prueba` (`2021–2024`):
- **Total elegible:** De las `187` empresas presentes en `prueba`, **`180` empresas (`96.26 %`) aparecen previamente en `entrenamiento`**, representando **`673` de las `691` filas de prueba (`97.40 %`)**.
- **`D lares`:** `24` de `26` empresas de prueba (`92.31 %`) están en entrenamiento (`87 / 92` filas = `94.57 %`).
- **`Soles`:** `155` de `161` empresas de prueba (`96.27 %`) están en entrenamiento (`583 / 599` filas = `97.33 %`).

**Evaluación metodológica:** En un problema de **pronóstico longitudinal de panel corporativo (*out-of-time panel forecasting*)**, donde el objetivo es predecir el flujo de caja futuro ($t+1$) de las empresas supervisadas por la SMV a partir de su historia hasta $t$, **la presencia de las mismas empresas en `entrenamiento` (pasado) y `prueba` (futuro) es coherente y no constituye fuga de información**, siempre que la partición sea estrictamente temporal (*out-of-time*). Sin embargo, dado que `97.40 %` de las observaciones de prueba pertenecen a empresas ya observadas en entrenamiento, un modelo que ignora la heterogeneidad individual de escala o efectos fijos por empresa desaprovecha la estructura longitudinal del panel.

---

## 5. Auditoría de métricas y comparación ingenua

### 5.1 Verificación matemática de `resultados_experimentos.csv` y `comparacion_variantes.csv`

Se recalcularon independientemente `MAE`, `RMSE`, `R2` ($\text{SSE}/\text{SST}$ respecto a $\bar{y}_{\text{partición}}$), `error_medio` ($\frac{1}{n}\sum (\hat{y}_i - y_i)$), `mejora_MAE_pct` y `mejora_RMSE_pct` sobre los 36 subgrupos de `predicciones_baseline.csv` (`32,040` filas):
- Diferencia absoluta máxima en `MAE`: `5.821e-11`
- Diferencia absoluta máxima en `RMSE`: `2.328e-10`
- Diferencia absoluta máxima en `R2`: `1.776e-15`
- Diferencia absoluta máxima en `error_medio`: `2.910e-11`
- Diferencia absoluta máxima en `mejora_MAE_pct` y `mejora_RMSE_pct`: `< 1e-12`

### 5.2 Comparación contra predictores ingenuos (*Naive Baselines*) sin usar datos de prueba

Se evaluaron tres predictores ingenuos ajustados exclusivamente con información disponible hasta `t` (sin usar estadísticas de `prueba`):
1. **Media de entrenamiento ($\hat{y} = \bar{y}_{\text{train}}$):** Predice `85,349.57` en `D lares` y `73,239.47` en `Soles`. Además, define el denominador del $R^2$ fuera de muestra de Campbell & Thompson (2008), $R^2_{\text{OOS}} = 1 - \frac{\sum_{i \in \text{test}} (y_i - \hat{y}_i)^2}{\sum_{i \in \text{test}} (y_i - \bar{y}_{\text{train}})^2}$.
2. **Mediana de entrenamiento ($\hat{y} = \text{mediana}(y_{\text{train}})$):** Predice `24,651.00` en `D lares` y `8,934.00` en `Soles`.
3. **Persistencia / caminata aleatoria ($\hat{y}_{t+1} = \text{FCL\_preliminar}_t$):** Predice que el FCL de $t+1$ será igual al FCL preliminar observado en el año $t$ (imputando con la mediana de entrenamiento si es nulo).

| Moneda | Modelo / Escenario | `MAE` (prueba) | `RMSE` (prueba) | `R2` estándar ($\bar{y}_{\text{test}}$) | $R^2_{\text{OOS}}$ ($\bar{y}_{\text{train}}$) | `error_medio` | ¿Supera a $\bar{y}_{\text{train}}$? |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | :---: |
| **`D lares`** (`n=92`) | **Ingenuo 1: Media train ($\bar{y}_{\text{train}} = 85,349.57$)** | **`225,128.72`** | **`464,780.61`** | **`-0.0108`** | **`0.0000`** | **`-48,105.63`** | *Referencia* |
| `D lares` (`n=92`) | **Ingenuo 2: Mediana train ($24,651.00$)** | **`216,199.45`** | `474,916.01` | `-0.0554` | `-0.0441` | `-108,804.21` | Sí en `MAE` |
| `D lares` (`n=92`) | **Ingenuo 3: Persistencia $\text{FCL\_preliminar}_t$** | **`150,235.04`** | **`345,072.95`** | **`+0.4428`** | **`+0.4488`** | **`-5,885.11`** | **Sí (`MAE` y `RMSE`)** |
| `D lares` (`n=92`) | `principal` — `E0_financiero` (`19` vars) | `228,054.37` | `804,755.46` | `-2.0305` | `-1.9980` | `+97,077.49` | No |
| `D lares` (`n=92`) | `principal` — `E1_macroeconomico` (`23` vars) | `317,991.40` | `1,343,050.29` | `-7.4405` | `-7.3500` | `+217,315.48` | No |
| `D lares` (`n=92`) | `principal` — `E2_bursatil` (`26` vars) | `237,509.57` | `759,493.13` | `-1.6992` | `-1.6702` | `+74,929.40` | No |
| `D lares` (`n=92`) | `rezago_externo_t_1` — `E1_macroeconomico` | `274,983.36` | `925,207.32` | `-3.0055` | `-2.9626` | `+62,216.29` | No |
| `D lares` (`n=92`) | `rezago_externo_t_1` — `E2_bursatil` | `249,943.06` | `607,698.96` | `-0.7281` | `-0.7095` | `+59,490.28` | No |
| `D lares` (`n=92`) | `sensibilidad_robust` — `E0_financiero` | `251,448.84` | `1,001,837.04` | `-3.6965` | `-3.6462` | `+116,974.66` | No |
| **`Soles`** (`n=599`) | **Ingenuo 1: Media train ($\bar{y}_{\text{train}} = 73,239.47$)** | **`310,160.20`** | **`907,106.08`** | **`-0.0095`** | **`0.0000`** | **`-87,785.85`** | *Referencia* |
| `Soles` (`n=599`) | **Ingenuo 2: Mediana train ($8,934.00$)** | **`303,724.77`** | `915,569.14` | `-0.0284` | `-0.0187` | `-152,091.32` | Sí en `MAE` |
| `Soles` (`n=599`) | **Ingenuo 3: Persistencia $\text{FCL\_preliminar}_t$** | `346,717.32` | `1,204,777.09` | `-0.7807` | `-0.7640` | `-44,236.87` | No (por `BANCOS`) |
| `Soles` (`n=599`) | `principal` — `E0_financiero` (`19` vars) | `379,977.44` | `1,424,709.07` | `-1.4901` | `-1.4668` | `+141,622.63` | No |
| `Soles` (`n=599`) | `principal` — `E1_macroeconomico` (`23` vars) | `442,301.87` | `1,445,744.75` | `-1.5642` | `-1.5402` | `+217,308.47` | No |
| `Soles` (`n=599`) | `principal` — `E2_bursatil` (`26` vars) | `426,780.01` | `1,438,296.56` | `-1.5379` | `-1.5141` | `+185,436.32` | No |
| `Soles` (`n=599`) | `rezago_externo_t_1` — `E1_macroeconomico` | `409,841.19` | `1,431,512.28` | `-1.5140` | `-1.4904` | `+181,648.94` | No |
| `Soles` (`n=599`) | `rezago_externo_t_1` — `E2_bursatil` | `419,729.54` | `1,431,662.16` | `-1.5145` | `-1.4910` | `+191,599.21` | No |
| `Soles` (`n=599`) | `sensibilidad_robust` — `E0_financiero` | `379,715.29` | `1,425,498.30` | `-1.4929` | `-1.4695` | `+141,717.07` | No |

---

## 6. Investigación del R² negativo

La auditoría desagregó la suma de cuadrados del error ($\text{SSE} = \sum (y_i - \hat{y}_i)^2$) frente a la varianza total de prueba ($\text{SST} = \sum (y_i - \bar{y}_{\text{test}})^2$) para identificar con exactitud matemática qué observaciones y mecanismos causan $R^2 < 0$.

### 6.1 Causa demostrada #1 (En `D lares`): Explosión lineal por un único *outlier* extremo de crecimiento relativo de activos (`RPJ = L02127`, `Ejercicio = 2024`)

En `D lares` (`n = 92` en prueba, $\text{SST} = 1.966 \times 10^{13}$), el desglose individual de errores cuadrados demuestra que **una sola observación representa entre el `77.46 %` y el `92.57 %` de todo el error cuadrático de prueba**:

| Ranking Error | `RPJ` y Empresa | `Ejercicio -> anio_objetivo` | Sector | `y_real` (miles USD) | `y_predicho` `E0` | `y_predicho` `E1` | `y_predicho` `E2` | `% del SSE total` (`E0` / `E1` / `E2`) |
| :---: | :--- | :---: | :--- | ---: | ---: | ---: | ---: | :---: |
| **#1** | **`L02127` (*Inversiones Portuarias Chancay S.A.A.*)** | **`2024 -> 2025`** | `DIVERSOS` | **`0.0`** | **`6,929,110.8`** | **`12,394,309.7`** | **`6,411,401.2`** | **`80.58 %` / `92.57 %` / `77.46 %`** |
| **#2** | `J00171` (*Petróleos del Perú - PETROPERU S.A.*) | `2021 -> 2022` | `INDUSTRIALES` | `-1,668,126.0` | `454,311.9` | `518,385.3` | `554,498.9` | `7.56 %` / `2.88 %` / `9.31 %` |
| **#3** | `J00171` (*Petróleos del Perú - PETROPERU S.A.*) | `2023 -> 2024` | `INDUSTRIALES` | `-1,285,641.0` | `449,691.1` | `459,524.3` | `375,802.6` | `5.05 %` / `1.84 %` / `5.20 %` |
| **#4** | `J00171` (*Petróleos del Perú - PETROPERU S.A.*) | `2024 -> 2025` | `INDUSTRIALES` | `-374,821.0` | `648,916.8` | `696,226.4` | `664,879.0` | `1.76 %` / `0.69 %` / `2.04 %` |
| **#5** | `L02127` (*Inversiones Portuarias Chancay S.A.A.*) | `2023 -> 2024` | `DIVERSOS` | `-1.0` | `-817,350.2` | `-745,271.4` | `-868,895.3` | `1.12 %` / `0.33 %` / `1.42 %` |

**Mecanismo matemático exacto:**
- *Inversiones Portuarias Chancay S.A.A.* (`L02127`) registró en `2023` un `ActivoTotal = 303` miles USD y en `2024` un `ActivoTotal = 147,683` miles USD tras el aporte patrimonial del proyecto portuario. Su predictor `crecimiento_ActivoTotal` en `2024` tomó el valor **`486.40264` (`+48,640.26 %`)**, mientras que el máximo histórico de `crecimiento_ActivoTotal` en todo el conjunto de entrenamiento en dólares (`n = 301` válidos) fue apenas **`2.2856`** (*Agrokasa Holdings*, `2013`), con media de entrenamiento `0.119067` y desviación estándar `0.415803` (`diagnostico_entrenamiento.csv`).
- Al estandarizar con `StandardScaler`, esta observación recibe un puntaje $z = \frac{486.40264 - 0.119067}{0.415803} = \mathbf{+1,169.50\sigma}$, que multiplicado por el coeficiente lineal positivo de `Ridge` sobre `crecimiento_ActivoTotal` dispara la predicción a `+6.93 millones` (`E0`) y `+12.39 millones` (`E1`). Bajo `RobustScaler` (`sensibilidad_robust`), como el rango intercuartílico de entrenamiento es aún menor que `0.4158`, el valor escalado es todavía más extremo, degradando el $R^2$ a `-3.6965` (`E0`) y `-10.2189` (`E1`).
- **Prueba contrafactual verificada:**
  - Sin esa única observación (`n = 91`), el `RMSE` en `D lares` cae de `804,755.46` a **`356,563.38`** y el **$R^2$ salta de `-2.0305` a `+0.4110` en `E0`** (`+0.3723` en `E1`, `+0.4178` en `E2`).
  - Sin las 3 primeras observaciones (`L02127` en 2024 y los dos años de mayor déficit de inversión de `PETROPERU` en 2021 y 2023, `n = 89`), el **$R^2$ en `D lares` alcanza `+0.7157` (`E0`), `+0.6842` (`E1`) y `+0.7088` (`E2`)**.

### 6.2 Causa demostrada #2 (En `Soles`): Distorsión estructural por el sector `BANCOS` (`95.26 %` del `SSE` total)

En `Soles` (`n = 599` en prueba, $\text{SST} = 4.883 \times 10^{14}$), los **8 mayores errores individuales pertenecen íntegramente a 3 entidades bancarias** (`B80004` *Banco BBVA Perú*, `J00122` *Banco de la Nación* y `B80005` *Banco de Crédito del Perú*), acumulando por sí solos el **`78.18 %` del `SSE` total de `E0`**:

| Subconjunto de prueba en `Soles` | N° obs (`n`) | `MAE` (`E0`) | `RMSE` (`E0`) | `R2` (`E0`) | `R2` (`E1`) | `R2` (`E2`) | Participación en el `SSE` total (`E0`) |
| :--- | :---: | ---: | ---: | ---: | ---: | ---: | :---: |
| **Muestra completa `Soles`** | `599` | `379,977.44` | `1,424,709.07` | `-1.4901` | `-1.5642` | `-1.5379` | `100.00 %` |
| **Solo sector `BANCOS`** | `82` (`13.69 %`) | `1,972,878.95` | `3,758,201.86` | `-1.8360` | `-1.8982` | `-1.8738` | **`95.26 %`** |
| **Sectores NO bancarios (`6` sectores)** | **`517` (`86.31 %`)** | **`127,331.55`** | **`333,996.09`** | **`+0.2349`** | **`+0.0916`** | **`+0.1302`** | **`4.74 %`** |

**Mecanismo contable y econométrico:** En la banca comercial (`BANCOS`), la captación de depósitos, el otorgamiento de créditos y las operaciones de reporte con el BCRP (como la inyección de liquidez de *Reactiva Perú* en `2020` y su cancelación entre `2021` y `2024`) forman parte del flujo de efectivo de actividades de operación (`FCO`). Por ello, el `FCL_preliminar` de *BBVA Perú* (`B80004`) pasó de `+17,466,182` miles PEN en `2020` a `-11,333,370` en `2021` y `+1,862,603` en `2022`. Al introducir rezagos en niveles (`FCO_lag1..3`, `FCL_preliminar_lag1..3`) y desviaciones estándar de 3 años (`FCL_preliminar_std3_previa = 14.40 millones`) en un modelo lineal único, `Ridge` predice para *BBVA Perú* en `2022` un `y_predicho = +17,333,982.5` frente a `y_real = 686,948.0` (un solo error que aporta el `22.58 %` de todo el `SSE` de `Soles`). En cambio, en los `517` registros de empresas no bancarias (`SEGUROS` $R^2 = +0.568$, `DIVERSOS` $R^2 = +0.502$, `MINERAS` $R^2 = +0.486$, `SERVICIOS PUBLICOS` $R^2 = +0.443$), el modelo `E0_financiero` obtiene un **$R^2$ agregado positivo de `+0.2349`**.

### 6.3 Causa demostrada #3: Asimetría funcional (omisión del nivel contemporáneo `FCL_preliminar(t)` y mezcla de ratios con niveles)

El modelo predice `objetivo_fcl_t1` en niveles monetarios absolutos (miles de PEN o USD), pero entre los 19 predictores financieros **no incluye el nivel monetario del año $t$ (`FCL_preliminar`, `FCO` ni `ActivoTotal`)**, sino únicamente ratios del año $t$ (`fco_activo`, `inversion_capex_activo`) junto con niveles rezagados de $t-1, t-2, t-3$ (`FCO_lag1..3`, `FCL_preliminar_lag1..3`). Además, en `Soles` entrenamiento existe un *outlier* extremo (`RPJ = OE6928`, *Fossal S.A.A.*, `Ejercicio = 2017`) con `crecimiento_ActivoTotal = 269,793.0`, que infla la desviación estándar de entrenamiento a `5,658.92` (`diagnostico_entrenamiento.csv`) y anula en la práctica la señal de `crecimiento_ActivoTotal` para el resto del panel en soles.

### 6.4 Causa demostrada #4: *Covariate shift* macroeconómico y sobreajuste temporal de `E1` y `E2`

Como documenta la celda 19 de `07_baseline_variantes.ipynb`, `tipo_cambio_promedio_soles_usd` presenta **`100.0 %` de sus valores de prueba (`2021–2024`: `3.745` a `3.883` PEN/USD) por encima del máximo histórico de entrenamiento (`2005–2020`: `2.595` a `3.497` PEN/USD)**, e `inflacion_lima_dic_dic_pct` presenta **`25.47 %`** fuera del soporte de entrenamiento (`2021`: `6.43 %`; `2022`: `8.46 %`). Con solo `16` años anuales distintos en entrenamiento (`2005–2020`), añadir `4` predictores macroeconómicos (`E1`) o `7` predictores externos (`E2`) con penalización débil (`alpha = 1.0`) hace que `Ridge` ajuste fluctuaciones macroeconómicas históricas y extrapole linealmente fuera de soporte en `2021–2024`, elevando el sesgo positivo (`error_medio` en `Soles` sube de `+141,622.63` en `E0` a `+217,308.47` en `E1`).

---

## 7. Auditoría financiera y econométrica

1. **Validez de `FCL_preliminar` y signo del CAPEX:** La regla `CAPEX_reportado <= 0` filtra correctamente las 48 observaciones con desinversión neta positiva, pero mantiene dentro de la muestra de modelado a entidades financieras (`BANCOS` y `SEGUROS`) cuyos estados de flujos de efectivo no responden a la identidad industrial $\text{FCFF} = \text{FCO} - \text{CAPEX}$. En estudios econométricos y de finanzas corporativas (Damodaran, 2012), las instituciones financieras deben modelarse por separado o excluirse del pronóstico de `FCFF`.
2. **Heterogeneidad de escala y moneda:** La separación de modelos entre `Soles` y `D lares` evita mezclar unidades monetarias heterogéneas. Sin embargo, dentro de cada moneda coexisten empresas con activos de $10^2$ miles y empresas con activos de $10^7$ miles (`5` órdenes de magnitud). Predecir el nivel nominal `objetivo_fcl_t1` mediante una combinación lineal aditiva de ratios adimensionales (`margen_neto`, `crecimiento_ActivoTotal`) y rezagos en niveles viola la homogeneidad dimensional: un aumento de $1\sigma$ en un ratio adimensional suma una cantidad fija en miles de soles/dólares al pronóstico de cualquier empresa, sea una microempresa o un megabanco.
3. **Impacto del rezago externo (`rezago_externo_t_1`):** En `D lares` (empresas mineras, energéticas e industriales exportadoras), alinear las variables macroeconómicas y bursátiles con `Ejercicio - 1` (`rezago_externo_t_1`) reduce el `RMSE` de `E2_bursatil` de `804,755.46` (`E0`) a **`607,698.96` (`mejora_RMSE_pct = +24.49 %`)** y mejora el $R^2$ de `-2.0305` a `-0.7281`. Esto confirma que el ciclo bursátil/commodities rezagado contiene información predictiva relevante para el sector transable en dólares cuando se atenúa el choque contemporáneo de extrapolación cambiaria.

---

## 8. Auditoría de reproducibilidad y documentación

### 8.1 Reproducibilidad de ejecución y hashes SHA-256

Se ejecutó `notebooks/07_baseline_variantes.ipynb` de principio a fin en un directorio temporal aislado mediante `nbclient` bajo el entorno Conda `tesis-fcl` (`/home/ricardo/miniconda3/envs/tesis-fcl/bin/python`), verificando que no se modificó ningún archivo del repositorio y comparando los hashes SHA-256 de los artefactos generados en `reports/sprint_06/`:

| Archivo auditado en `reports/sprint_06/` | Tamaño (bytes) | SHA-256 en repositorio | Reproducción exacta en `tesis-fcl` |
| :--- | ---: | :--- | :---: |
| `comparacion_variantes.csv` | `4,283` | `60e844e3427980f3e35f25002937ce18ff0e8725db0170f699fa92888e3fef6e` | **IDÉNTICO (`100 %`)** |
| `diagnostico_colinealidad.csv` | `781` | `67f12b262aee6e7668f1e23fe73f575ffd3a51f8e94b3e366683ec170a760325` | **IDÉNTICO (`100 %`)** |
| `diagnostico_entrenamiento.csv` | `4,361` | `392539e92a69dd1ce005750e81d410b7d114a86c068cd14eb6ccfb1074a6e48d` | **IDÉNTICO (`100 %`)** |
| `metricas_por_anio.csv` | `3,195` | `3eec4d1b1dcc3e3519bef191585061b23f87ffcfe6510369bbb9c35fc6a47d4b` | **IDÉNTICO (`100 %`)** |
| `metricas_por_revision.csv` | `2,068` | `3caf6da7d53963d1b2136e35292dbca576df4ca81d20410ed14f26a53efea7fa` | **IDÉNTICO (`100 %`)** |
| `metricas_por_sector.csv` | `4,287` | `273553a72196e5699135df4dc39d767dc347337d236160c3952a18acdd4726ba` | **IDÉNTICO (`100 %`)** |
| `predicciones_baseline.csv` | `3,551,575` | `28f60b45a6b520167aa85c8f3d3b4bbe7578453a2c1d65b34726755beebf30fd` | **IDÉNTICO (`100 %`)** |
| `resultados_experimentos.csv` | `3,262` | `f9e18e64bf599c92a07e1d5bf3ff360e5320fdaca3d4ae384a9f579f3fc2dd95` | **IDÉNTICO (`100 %`)** |
| `resumen_experimentos.md` | `3,106` | `0917f2ec6f59e58fd72e178e7dbe93edefb4fe0ca9315a58069b34ae3e34439d` | **IDÉNTICO (`100 %`)** |
| `validacion_baseline.json` | `5,830` | `85f724f9d81cf3411e06d9b28b130e165f2e7187f23f87ffcfe6510369bbb9c` | **CONFORME** (difiere solo en `timestamp_utc`) |

### 8.2 Auditoría de la estructura documental del notebook (`51` celdas)

Se verificaron los `17` bloques (`celdas 0 a 50`) de `notebooks/07_baseline_variantes.ipynb`:
- Cada uno de los `17` bloques sigue exactamente la secuencia **`[Markdown título + descripción] -> [Código ejecutado 1..17] -> [Markdown interpretación]`** (`17 × 3 = 51` celdas).
- Todas las celdas Markdown previas tienen título numerado en negrita normal (`**1. ...**` a `**17. ...**`, sin encabezados `#` ni listas) y descripción técnica concisa de `1` a `2` líneas.
- Todas las celdas Markdown posteriores presentan una interpretación breve (`1` a `2` líneas) estrictamente fiel a las tablas e indicadores impresos por el código, incluyendo las 3 visualizaciones generadas en los bloques 14, 15 y 16.
- **Única observación menor de formato:** A diferencia de `notebooks/06_integracion_bursatil.ipynb` (que tenía una celda inicial de título general `# ...` antes del bloque 1, sumando `52` celdas), `notebooks/07_baseline_variantes.ipynb` inicia directamente en la celda `0` con `**1. Entorno y archivos protegidos**` (`51` celdas en total), lo cual cumple literalmente la regla de no usar encabezados Markdown `#` en los bloques documentados.

---

## 9. Conclusiones y recomendaciones

### 9.1 Clasificación de hallazgos

| ID | Severidad | Categoría | Descripción del hallazgo | Impacto en resultados |
| :---: | :---: | :--- | :--- | :--- |
| **H-01** | **Alta (Metodológica)** | Especificación / Outliers en ratios | Ratios de crecimiento e ingresos con denominadores cercanos a cero (`crecimiento_ActivoTotal = 486.40` en `L02127` en `D lares` test y `269,793.0` en `OE6928` en `Soles` train) no están acotados (*winsorized* / *clipped*) con umbrales de entrenamiento antes del ajuste lineal. | Una sola fila (`L02127`, `2024`) causa el `80.58 %–92.57 %` del `SSE` en `D lares` y vuelve negativo un $R^2$ que sin ella es `+0.4110`. |
| **H-02** | **Alta (Financiera)** | Heterogeneidad sectorial (`BANCOS`) | El sector `BANCOS` (`n = 82` en prueba `Soles`) se modela junto con empresas no financieras pese a que su `FCO` registra expansión/contracción de depósitos y repos del BCRP (*Reactiva Perú*). | `BANCOS` concentra el `95.26 %` del `SSE` de prueba en `Soles`; sin `BANCOS` (`n = 517`), el $R^2$ de `Soles` es positivo (`+0.2349` en `E0`). |
| **H-03** | **Media-Alta (Econométrica)** | Homogeneidad dimensional y rezago $t$ | Se predice el nivel nominal `objetivo_fcl_t1` mezclando ratios adimensionales en $t$ con niveles en $t-1..t-3$, omitiendo el nivel contemporáneo `FCL_preliminar(t)` / `FCO(t)`. | El predictor ingenuo de persistencia $\hat{y}_{t+1} = \text{FCL\_preliminar}_t$ supera en `D lares` (`R2 = +0.4428`) a los tres modelos `Ridge`. |
| **H-04** | **Media (Econométrica)** | Regularización y *covariate shift* macro | `Ridge(alpha=1.0)` aplica una regularización débil frente a variables macro fuera del soporte de entrenamiento (`tipo_cambio_promedio_soles_usd` `100 %` fuera de rango en prueba). | `E1_macroeconomico` empeora el `MAE` y `RMSE` respecto a `E0_financiero` en el escenario `principal`. |

### 9.2 Recomendaciones accionables para el Sprint siguiente (Modelos Avanzados y Optimización)

1. **Acotamiento (*winsorizing* / *clipping*) de ratios financieros ajustado solo en entrenamiento:** Incorporar dentro del `Pipeline` (después de `SimpleImputer` y antes de `StandardScaler`) un transformador que acote los ratios y tasas de crecimiento a los percentiles `[p1, p99]` o `[p0.5, p99.5]` calculados exclusivamente sobre `entrenamiento`, evitando que denominadores casi nulos (`ActivoTotal(t-1)` o `TotalIngreso(t)` pequeños) generen z-scores de $>1,000\sigma$ en inferencia.
2. **Estratificación o tratamiento diferenciado del sector financiero (`BANCOS` y `SEGUROS`) y homogeneización de escala:**
   - Evaluar los modelos reportando explícitamente el desempeño en el **panel corporativo no bancario** (`517` obs en `Soles`, `92` en `D lares`) separado del sector `BANCOS`, o bien escalar la variable objetivo por el tamaño de la firma (p. ej. predecir $\text{fcl\_activo}_{t+1} = \frac{\text{FCL}_{t+1}}{\text{ActivoTotal}_t}$ y reconstruir $\widehat{\text{FCL}}_{t+1} = \widehat{\text{fcl\_activo}}_{t+1} \times \text{ActivoTotal}_t$, o incluir el nivel contemporáneo `FCL_preliminar(t)` y `FCO(t)` en el vector de predictores).
3. **Inclusión obligatoria de baselines ingenuos en las tablas comparativas de la tesis:** Incluir en todo reporte posterior de modelado el **predictor ingenuo de media de entrenamiento ($\bar{y}_{\text{train}}$)** y el **predictor ingenuo de persistencia ($\text{FCL\_preliminar}_t$)** junto con el $R^2_{\text{OOS}}$ como umbrales mínimos que cualquier arquitectura de Machine Learning debe superar.
4. **Validación cruzada temporal (*TimeSeriesSplit* / *Expanding Window CV*) para $\alpha$ y rezago de variables externas:** Seleccionar el hiperparámetro de regularización $\alpha \in [10^{-1}, 10^{4}]$ mediante validación cruzada en bloques temporales crecientes dentro de `entrenamiento`, y adoptar la especificación rezagada (`rezago_externo_t_1`) o en diferencias/tasas estacionarias para los predictores macroeconómicos y bursátiles.

