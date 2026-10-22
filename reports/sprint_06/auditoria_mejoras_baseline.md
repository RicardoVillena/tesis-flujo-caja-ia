# Auditoría Independiente — Mejoras del Baseline y Validación Temporal (Notebook 08)

**Proyecto:** `tesis-flujo-caja-ia` (Maestría en Inteligencia Artificial — UNI)  
**Notebook auditado:** `notebooks/08_mejoras_baseline.ipynb` (`316,378` bytes; `45` celdas; SHA-256: `daecee6c8311a77d4a2e57e494999505067c9e2663b369cf77b574ac44114461`)  
**Directorio de artefactos auditados:** `reports/sprint_06/mejoras/` (`21` archivos generados)  
**Entorno verificado:** Conda `tesis-fcl` (`Python 3.12.15`, `pandas 3.0.6`, `numpy 2.5.4`, `scikit-learn 1.9.1`, `matplotlib 3.11.2`, `nbformat 5.11.1`, `nbclient 0.11.0`)  
**Fecha de auditoría:** 21 de octubre de 2026  

---

## 1. Resumen ejecutivo

- **Veredicto global:** **APROBADO — IMPLEMENTACIÓN TÉCNICA, METODOLÓGICA Y DE PREVENCIÓN DE FUGA DE INFORMACIÓN 100 % CONFORME.**
- **Respuesta a las observaciones de la auditoría del Notebook 07:** El notebook `08_mejoras_baseline.ipynb` instrumenta de manera rigurosa y sin fuga de datos las cuatro mejoras recomendadas tras la auditoría de `07_baseline_variantes.ipynb`:
  1. **Acotamiento (*clipping* `[p01, p99]`) de los 11 ratios y variaciones financieras** dentro del `Pipeline` (`ClipRatios`), estimado exclusivamente sobre el subconjunto de entrenamiento de cada pliegue temporal y del ajuste final (después de `SimpleImputer(strategy="median", keep_empty_features=True)` y antes de `StandardScaler`), sin recortar objetivos (`objetivo_fcl_t1`), niveles monetarios (`FCL_t_verificado`, `FCO_t`, rezagos) ni variables externas.
  2. **Inclusión controlada del nivel contemporáneo (`FCL_t_verificado`, `FCO_t`) y rezago de variables externas (`t - 1`)**, evaluada frente a una especificación de sensibilidad conservadora sin niveles contemporáneos (`sin_niveles_t_externos_t_1`) y reconociendo explícitamente que las fechas efectivas de publicación de los estados financieros e indicadores no están acreditadas (*backtest* condicional, no *point-in-time*).
  3. **Separación explícita entre régimen `no_bancario` y régimen `bancario` (`TipoSector == "BANCOS"`)** dentro de `Soles`, sin eliminar ninguna de las `3,560` observaciones elegibles (`2,869` entrenamiento / `691` prueba).
  4. **Calibración de $\alpha \in \{0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0\}$ y selección de especificación/experimento exclusivamente mediante validación cruzada temporal expansiva por bloques de dos años objetivo**, ponderando cada año de validación por igual (`MSE` anual medio) y congelando la selección (`seleccion_congelada_cv.csv`, SHA-256: `501fe62966e4698bdc809960dfaf1cde2e885a36943d73bbe9f55cb6c8302df7`) antes de evaluar `prueba`.
- **Impacto empírico verificado en el panel corporativo no bancario (`88.13 %` de la muestra de prueba, `609 / 691` observaciones):**
  - En **`D lares / no_bancario` (`n = 92` prueba, `100 %` de la muestra en dólares)**: el ganador de CV (`niveles_t_externos_t_1`, `E1_macroeconomico`, `alpha = 1000.0`) reduce el `MAE` en **`-35.16 %`** (`147,873.25` vs `228,054.37` en `07 E0`) y el `RMSE` en **`-59.74 %`** (`323,976.81` vs `804,755.46`), elevando el **$R^2$ de prueba de `-2.0305` a `+0.5089`** (con $R^2 > 0$ en los cuatro años `2022–2025`), y superando tanto a la media de entrenamiento ($R^2_{\text{OOS, media}} = \mathbf{+0.5141}$) como al predictor ingenuo de persistencia ($R^2_{\text{OOS, persistencia}} = \mathbf{+0.1185}$).
  - En **`Soles / no_bancario` (`n = 517` prueba, `86.31 %` de la muestra en soles)**: el ganador de CV (`sin_niveles_t_externos_t_1`, `E2_bursatil`, `alpha = 1000.0`) reduce el `MAE` a **`124,751.25`** (`-2.03 %` vs `127,331.55` en `07 E0`) y el `RMSE` a **`280,239.20`** (`-16.09 %` vs `333,996.09` en `07 E0`), elevando el **$R^2$ de prueba de `+0.2349` a `+0.4614`** (con $R^2 > 0$ en los cuatro años `2022–2025`), y superando ampliamente tanto a la media de entrenamiento ($R^2_{\text{OOS, media}} = \mathbf{+0.4811}$) como a la persistencia ($R^2_{\text{OOS, persistencia}} = \mathbf{+0.4480}$).
- **Transparencia metodológica sobre el sector `BANCOS` (`Soles / bancario`, `n = 82` prueba):** Con solo `9` años de entrenamiento (`2013–2021`) y `2` pliegues de validación (`2018–2021`), la validación cruzada en `Soles / bancario` eligió `niveles_t_externos_t_1`, `E1_macroeconomico`, `alpha = 10.0`. Al reajustar sobre `2013–2021`, los 4 predictores macroeconómicos rezagados con regularización baja (`alpha = 10.0`) sobreajustaron el choque de liquidez de *Reactiva Perú* (`2020–2021`) y extrapolaron en `prueba` (`2022–2025`), elevando el `RMSE` bancario a `5,683,160.61` ($R^2 = -5.4853$) y arrastrando la política combinada de `Soles` (`n = 599`) a $R^2 = -4.5074$. **Es metodológicamente ejemplar que el notebook 08 haya conservado intacta la selección congelada de CV sin sustituirla *post-hoc* mirando el conjunto de prueba**, documentando además que la partición `2022–2025` ya fue inspeccionada en la auditoría del notebook 07 y que la evaluación constituye un contraste retrospectivo condicional.

---

## 2. Auditoría de integridad de datos, cohortes y preservación de archivos

| Verificación | Resultado esperado | Resultado auditado | Estado |
| :--- | :---: | :---: | :---: |
| Conservación de archivos previos (`README.md`, `data/`, `src/`, `notebooks/02..07`, `reports/sprint_06/*`) | `0` archivos modificados | `hashes_previos() == hashes_antes` (`0` discrepancias en `validacion_mejoras.json`) | **CONFORME** |
| Muestra elegible total (`utilizable_supervisado == True`) | `3,560` filas / `309` empresas | `3,560` filas (`2,869` train, `691` test) / `309` empresas | **CONFORME** |
| Cohorte `D lares / todas` y `D lares / no_bancario` | `353` train / `92` test | `353` train (`49` RPJ, `2006–2021`) / `92` test (`26` RPJ, `2022–2025`) | **CONFORME** |
| Cohorte `Soles / no_bancario` | `2,344` train / `517` test | `2,344` train (`246` RPJ, `2006–2021`) / `517` test (`139` RPJ, `2022–2025`) | **CONFORME** |
| Cohorte `Soles / bancario` (`TipoSector == "BANCOS"`) | `172` train / `82` test | `172` train (`23` RPJ, `2013–2021`) / `82` test (`22` RPJ, `2022–2025`) | **CONFORME** |
| Reconstrucción algebraica de `FCL_t_verificado` y `FCO_t` | `FCO(t) + CAPEX(t)` si `CAPEX(t) <= 0` | `104` casos de `FCL(t)` inválidos/ausentes y `51` de `FCO(t)` ausentes conservados sin eliminar filas | **CONFORME** |

---

## 3. Auditoría del Pipeline, Clipping (`ClipRatios`) y Validación Cruzada Temporal

### 3.1 Verificación del transformador `ClipRatios` y ausencia de *data leakage*

1. **Secuencia exacta dentro de `Pipeline`:** `SimpleImputer(strategy="median", keep_empty_features=True)` $\to$ `ClipRatios(cols, RATIOS, q_low=0.01, q_high=0.99)` $\to$ `StandardScaler()` $\to$ `Ridge(alpha=alpha, solver="svd")`.
2. **Aislamiento de variables recortadas:** Únicamente se recortan los `11` ratios y variaciones adimensionales (`pasivo_activo`, `margen_neto`, `rentabilidad_activo_cierre`, `rotacion_activo_cierre`, `fco_activo`, `fco_ingresos`, `inversion_capex_activo`, `crecimiento_ActivoTotal`, `crecimiento_TotalIngreso`, `cambio_FCO_activo_previo`, `cambio_FCL_preliminar_activo_previo`). Los niveles monetarios (`FCL_t_verificado`, `FCO_t`, `FCO_lag1..3`, `FCL_preliminar_lag1..3`, `FCO_std3_previa`, `FCL_preliminar_std3_previa`), las variables macroeconómicas/bursátiles y la variable objetivo `objetivo_fcl_t1` **no sufren recorte alguno**.
3. **Verificación de umbrales aprendidos en entrenamiento (`umbrales_clipping.csv`, `495` filas = `45` modelos × `11` ratios):**
   - En `D lares / no_bancario`, `crecimiento_ActivoTotal` aprende en entrenamiento `[p01, p99] = [-0.321237, +0.746303]`, recortando en `prueba` únicamente `2` celdas (entre ellas `RPJ = L02127`, *Inversiones Portuarias Chancay*, `Ejercicio = 2024`, cuyo valor extremo `486.40264` pasa a `0.746303`, reduciendo su predicción de `+6,929,110.8` en el notebook 07 a **`+59,672.05`** frente a `y_real = 0.0`).
   - En `Soles / no_bancario`, `crecimiento_ActivoTotal` aprende en entrenamiento `[p01, p99] = [-0.428743, +1.691126]`, neutralizando el *outlier* de entrenamiento `RPJ = OE6928` (*Fossal S.A.A.*, `269,793.0`) antes de calcular la media y desviación estándar de `StandardScaler`.
4. **Prueba de invariancia ante perturbación de `prueba` (Bloque 14):** Al multiplicar por `100` y sumar `10,000` a todos los predictores y objetivos de `prueba`, los cuantiles `lower_` y `upper_` de `ClipRatios` y las predicciones sobre el conjunto de prueba original permanecen idénticos hasta `1e-12`.

### 3.2 Verificación de los pliegues temporales (`cv_por_anio.csv`, `cv_folds.csv` y `cv_puntuaciones.csv`)

- **Agrupación por año objetivo completo (`anio_objetivo`):** Todas las empresas de un mismo año objetivo entran juntas en entrenamiento o validación (`18` pliegues en total a través de las `5` cohortes), evitando fuga transversal contemporánea de variables macroeconómicas y bursátiles.
- **Verificación matemática de la agregación de CV:**
  - Diferencia máxima entre el promedio de `mse` de `cv_por_anio.csv` (`1,944` filas) y `mse_anual_medio` en `cv_folds.csv` (`972` filas): `0.000e+00`.
  - Diferencia máxima entre el promedio anual de `cv_por_anio.csv` y `rmse_cv` en `cv_puntuaciones.csv` (`270` filas = `5` cohortes × `9` especificaciones × `6` valores de $\alpha$): `4.657e-10`.
- **Regla de decisión congelada (`alphas_optimos.csv` $\to$ `seleccion_congelada_cv.csv`):** Selección por menor `MSE` medio anual de validación (con desempate a favor de mayor `alpha`) antes de evaluar `prueba`.

---

## 4. Auditoría de métricas, predictores ingenuos y comparación con el Notebook 07

### 4.1 Verificación matemática independiente de `metricas_mejoras.csv` (`110` filas)

El recálculo independiente de las `110` filas de `metricas_mejoras.csv` (`5` cohortes × `11` configuraciones [9 modelos Ridge + 2 ingenuos] × `2` particiones) a partir de las `78,320` filas de `predicciones_mejoras.csv` arrojó diferencias absolutas máximas de:
- `MAE`: `6.985e-10`
- `RMSE`: `9.313e-10`
- `R2`: `1.776e-15`
- `error_medio`: `3.492e-10`

### 4.2 Tabla comparativa auditada en `prueba` (`2022–2025`): Ganadores CV vs Notebook 07 y Baselines Ingenuos

| Cohorte (`Moneda / Grupo`) | Modelo / Especificación | `n` (test) | `MAE` | `RMSE` | `R2` estándar | $R^2_{\text{OOS}}$ vs Media train | $R^2_{\text{OOS}}$ vs Persistencia | Cambio `RMSE` vs `07 E0` |
| :--- | :--- | :---: | ---: | ---: | ---: | ---: | ---: | :---: |
| **`D lares / no_bancario`** | **Ingenuo: Media train (`85,349.57`)** | `92` | `225,128.72` | `464,780.61` | `-0.0108` | `0.0000` | `-0.8142` | — |
| `D lares / no_bancario` | **Ingenuo: Persistencia $\text{FCL}_t$** | `92` | `150,235.04` | `345,072.95` | `+0.4428` | `+0.4488` | `0.0000` | — |
| `D lares / no_bancario` | **Notebook 07 (`E0_financiero`, $\alpha=1$)** | `92` | `228,054.37` | `804,755.46` | `-2.0305` | `-1.9980` | `-4.4388` | *Base 07* |
| **`D lares / no_bancario`** | **Ganador CV 08 (`niveles_t_externos_t_1`, `E1`, $\alpha=1000$)** | **`92`** | **`147,873.25`** | **`323,976.81`** | **`+0.5089`** | **`+0.5141`** | **`+0.1185`** | **`-59.74 %` (mejora)** |
| `D lares / no_bancario` | Sensibilidad 08 sin niveles $t$ (`E1`, $\alpha=1000$) | `92` | `170,832.13` | `357,293.14` | `+0.4026` | `+0.4090` | `-0.0721` | `-55.60 %` (mejora) |
| **`Soles / no_bancario`** | **Ingenuo: Media train (`51,921.84`)** | `517` | `177,588.98` | `389,050.96` | `-0.0381` | `0.0000` | `-0.0640` | — |
| `Soles / no_bancario` | **Ingenuo: Persistencia $\text{FCL}_t$** | `517` | `134,273.13` | `377,176.59` | `+0.0243` | `+0.0601` | `0.0000` | — |
| `Soles / no_bancario` | **Notebook 07 (`E0_financiero`, $\alpha=1$)** | `517` | `127,331.55` | `333,996.09` | `+0.2349` | `+0.2630` | `+0.2159` | *Base 07* |
| **`Soles / no_bancario`** | **Ganador CV 08 (`sin_niveles_t_externos_t_1`, `E2`, $\alpha=1000$)** | **`517`** | **`124,751.25`** | **`280,239.20`** | **`+0.4614`** | **`+0.4811`** | **`+0.4480`** | **`-16.09 %` (mejora)** |
| `Soles / no_bancario` | Alternativa 08 con niveles $t$ (`niveles_t_externos_t_1`, `E1`, $\alpha=10000$) | `517` | `127,716.02` | `284,535.47` | `+0.4447` | `+0.4651` | `+0.4309` | `-14.81 %` (mejora) |
| **`Soles / bancario`** | **Ingenuo: Media train (`363,754.15`)** | `82` | `1,198,726.23` | `2,231,691.38` | `0.0000` | `0.0000` | `+0.4869` | — |
| `Soles / bancario` | **Notebook 07 (`E0_financiero`, $\alpha=1$)** | `82` | `1,972,878.95` | `3,758,201.86` | `-1.8360` | `-1.8359` | `-0.4552` | *Base 07* |
| **`Soles / bancario`** | **Ganador CV 08 (`niveles_t_externos_t_1`, `E1`, $\alpha=10$)** | **`82`** | **`4,299,569.80`** | **`5,683,160.61`** | **`-5.4853`** | **`-5.4850`** | **`-2.3277`** | **`+51.22 %` (deterioro)** |
| `Soles / bancario` | Alternativa 08 financiera pura (`niveles_t_externos_t`, `E0`, $\alpha=100$) | `82` | `1,828,821.73` | `3,395,733.63` | `-1.3154` | `-1.3153` | `-0.1880` | `-9.64 %` (mejora) |

### 4.3 Estabilidad interanual (`2022–2025`) en los paneles corporativos no bancarios

| Cohorte no bancaria | Año objetivo (`t+1`) | `n` | `MAE` | `RMSE` | `R2` anual | `error_medio` |
| :--- | :---: | :---: | ---: | ---: | ---: | ---: |
| `D lares / no_bancario` | `2022` | `22` | `184,752.02` | `426,101.04` | **`+0.1675`** | `+138,853.69` |
| `D lares / no_bancario` | `2023` | `23` | `127,006.88` | `208,526.30` | **`+0.6840`** | `-31,039.39` |
| `D lares / no_bancario` | `2024` | `24` | `171,156.96` | `388,448.00` | **`+0.4408`** | `+11,968.55` |
| `D lares / no_bancario` | `2025` | `23` | `109,168.23` | `212,697.47` | **`+0.7847`** | `-37,685.07` |
| `Soles / no_bancario` | `2022` | `134` | `121,668.16` | `243,491.03` | **`+0.4675`** | `+45,089.32` |
| `Soles / no_bancario` | `2023` | `131` | `112,435.18` | `200,557.27` | **`+0.7522`** | `+41,343.18` |
| `Soles / no_bancario` | `2024` | `128` | `142,961.76` | `379,000.90` | **`+0.1705`** | `+44,375.95` |
| `Soles / no_bancario` | `2025` | `124` | `122,296.38` | `269,439.81` | **`+0.4598`** | `-23,359.66` |

### 4.4 Diagnóstico econométrico del deterioro en `Soles / bancario` (`n = 82`)

La auditoría verificó por qué el ganador de CV en `Soles / bancario` (`niveles_t_externos_t_1`, `E1_macroeconomico`, `alpha = 10.0`) empeoró en `prueba`:
1. **Cobertura temporal reducida en banca (`9` años de entrenamiento `2013–2021`):** Durante los 2 pliegues de validación (`fold 1: 2018–2019`, `fold 2: 2020–2021`), el entrenamiento del `fold 2` solo llegaba hasta `anio_objetivo = 2019` (`Ejercicio = 2018`, `t - 1 = 2017`). Por tanto, el choque de liquidez de *Reactiva Perú* (`anio_objetivo = 2020` y `2021`) nunca formó parte del subconjunto de entrenamiento de los pliegues de validación.
2. **Sobreajuste macroeconómico en el reajuste final (`2013–2021`):** Al reajustar `E1_macroeconomico` con `alpha = 10.0` sobre todo el entrenamiento bancario (`2013–2021`), las 4 variables macroeconómicas anuales rezagadas (`t - 1` entre `2011` y `2019`, apenas `9` puntos temporales anuales distintos) absorbieron con coeficientes elevados el salto positivo del FCL bancario de `2020` (`Ejercicio = 2019`, `t - 1 = 2018`) y la reversión negativa de `2021` (`Ejercicio = 2020`, `t - 1 = 2019`).
3. **Extrapolación en `prueba` (`2022–2025`):** Cuando ingresaron los valores macroeconómicos rezagados de `2020–2023` (en particular `t - 1 = 2021` para `anio_objetivo = 2023`, con `crecimiento_pbi_real_pct = +13.36 %` e `inflacion_lima_dic_dic_pct = 6.43 %`), la combinación lineal macro desplazó el intercepto de los `21` bancos en **`+7,014,941.15` unidades reportadas en `2023`** (`R2 = -57.7924`) y en **`-4,192,389.89` en `2025`** (`R2 = -6.8685`).

---

## 5. Auditoría de reproducibilidad, inventario de artefactos y estructura documental

### 5.1 Inventario verificado de `reports/sprint_06/mejoras/` (`21` archivos)

Todos los archivos coinciden al `100 %` con el registro criptográfico de `validacion_mejoras.json`:

| Archivo en `reports/sprint_06/mejoras/` | Filas | Columnas | Tamaño (bytes) | SHA-256 en repositorio | Reproducción en `tesis-fcl` |
| :--- | :---: | :---: | ---: | :--- | :---: |
| `alphas_optimos.csv` | `45` | `7` | `4,424` | `3aba0d33db17757b944729d2457db8afca0c81d039a3162a4afddb04461d7549` | **IDÉNTICO (`100 %`)** |
| `comparacion_homologa_vs07.csv` | `36` | `20` | `10,517` | `287d2abdf112266e461a48bbcdcc5016bf1f99636f59f7aebc8c204cff38465a` | **CONFORME (`<1e-12` SVD)** |
| `comparacion_sector_vs07.csv` | `6` | `28` | `2,740` | `938c4f4087d7b32cc69c6c9770f91fa42837376cf630a073f6d874081056370c` | **CONFORME (`<1e-12` SVD)** |
| `comparacion_vs07.csv` | `4` | `18` | `1,343` | `5dcab11bf8135ff99c5a2c09bfcf16970c092e88b9519733fb27cc3105b18d38` | **CONFORME (`<1e-12` SVD)** |
| `conteos_muestra.csv` | `6` | `7` | `326` | `4160e1d5866608aa4d5e8a698dcaadd4cb291d864ddf7e9a1149eb55cf54f4f6` | **IDÉNTICO (`100 %`)** |
| `cv_folds.csv` | `972` | `9` | `85,828` | `4c7e923c31979670051d07d35609ef57d9709022e4f835f392de003f6dea1cb9` | **CONFORME (`<1e-12` SVD)** |
| `cv_por_anio.csv` | `1,944` | `8` | `165,945` | `97c12e884c03992f205efcd6e9b3cb497fe532555b510fe87ef4e1595c8aa571` | **CONFORME (`<1e-12` SVD)** |
| `cv_puntuaciones.csv` | `270` | `7` | `26,066` | `79610f2b3fa5f44849922ca5982031861194cf28a444e544fc826096f183765b` | **CONFORME (`<1e-12` SVD)** |
| `metricas_agrupados_por_sector.csv` | `66` | `15` | `14,498` | `320377c0ad24c33bf561dfce37acddcb4a8b7d1af61f02201126f94d72f0d908` | **CONFORME (`<1e-12` SVD)** |
| `metricas_baselines_07.csv` | `36` | `14` | `7,455` | `5593ac612f45a150abe0a959810c90d2c34f6d6be5cb258aaac872043595c9bb` | **IDÉNTICO (`100 %`)** |
| `metricas_mejoras.csv` | `110` | `17` | `25,098` | `29e9f1ac3c0720895e069db8654c9ae90c8b060484abfe7a91ee85c366fcff1b` | **CONFORME (`<1e-12` SVD)** |
| `metricas_politica_cv.csv` | `4` | `13` | `897` | `5e778b2d07e97db089a3b9fff96ab739b1c101fa1ce9cfe1d35b4d19fb3e0e88` | **CONFORME (`<1e-12` SVD)** |
| `metricas_por_anio.csv` | `40` | `13` | `6,755` | `06bf3841a810d02f5382dc19961b9e5893afcaba9ec645200300846d8b65df66` | **CONFORME (`<1e-12` SVD)** |
| `metricas_sector_07.csv` | `18` | `14` | `3,653` | `b3b7ba6ff9a7b70ccacee229b567d08302aaf191b80b8cf1eb2407984934a453` | **IDÉNTICO (`100 %`)** |
| `parametros_ingenuos.csv` | `5` | `6` | `333` | `82708e63bb315d57f73c415942c1864d7f585ab3b6e4106d2c41b69e12417a6d` | **IDÉNTICO (`100 %`)** |
| `predicciones_mejoras.csv` | `78,320` | `16` | `12,796,955` | `2eacc923ae5f258d70f752547fdae972a566a542f7edfbac3bd4512371f86abe` | **CONFORME (`<1e-12` SVD)** |
| `predicciones_seleccionadas_cv.csv` | `3,560` | `16` | `615,550` | `8dfa8ff3e8058a97839351c9a7d38224828df23e8776c92855fc9f6ed4c0c31b` | **CONFORME (`<1e-12` SVD)** |
| `resumen_mejoras.md` | — | — | `1,818` | `2b799321853863004731dd5352ddef1de04afd670db35f37856d07bc1fcb1197` | **IDÉNTICO (`100 %`)** |
| `seleccion_congelada_cv.csv` | `5` | `6` | `455` | `501fe62966e4698bdc809960dfaf1cde2e885a36943d73bbe9f55cb6c8302df7` | **IDÉNTICO (`100 %`)** |
| `umbrales_clipping.csv` | `495` | `8` | `57,191` | `4ee0003ca4dd9b1c9a4480fd59e1713bcf5a2405b98551a1793d5d2dab9046cb` | **IDÉNTICO (`100 %`)** |
| `validacion_mejoras.json` | — | — | `1,212,115` | `c63dcc8c7917f75f913d0f43486321a24772836c11e957a563d73a44ea79c435` | **CONFORME (`fecha_utc`)** |

### 5.2 Estructura documental (`45` celdas = `15` bloques)

Cada uno de los `15` bloques de `notebooks/08_mejoras_baseline.ipynb` cumple estrictamente el formato `[Markdown con título en negrita **1. ...** a **15. ...** + descripción de 1–2 líneas] -> [Código ejecutado 1..15] -> [Markdown de interpretación de 1–2 líneas]`, sin encabezados `#` ni listas en las celdas explicativas, y documentando con rigor las limitaciones metodológicas.

---

## 6. Conclusiones y recomendaciones para los siguientes sprints

1. **El baseline lineal mejorado (`Notebook 08`) queda validado como referencia formal para el modelado no lineal:** En el universo corporativo no bancario (`88.13 %` de la muestra de prueba), `Ridge` con `ClipRatios(0.01, 0.99)` y regularización calibrada por CV ($\alpha = 1000.0$) logra habilidad predictiva positiva y consistente fuera de muestra tanto en dólares ($R^2 = +0.5089$, $R^2_{\text{OOS, media}} = +0.5141$, $R^2_{\text{OOS, persistencia}} = +0.1185$) como en soles ($R^2 = +0.4614$, $R^2_{\text{OOS, media}} = +0.4811$, $R^2_{\text{OOS, persistencia}} = +0.4480$).
2. **Restricción de parsimonia para la cohorte `Soles / bancario` en próximos sprints:** Dado que `Soles / bancario` solo cuenta con `9` años de entrenamiento (`2013–2021`), incluir `4` a `7` variables macroeconómicas/bursátiles anuales produce sobreajuste temporal severo en el nivel medio anual. En los modelos de sprints posteriores, para el subgrupo `bancario` se recomienda restringir la grilla de regularización a valores altos ($\alpha \ge 1000$) o limitar los predictores bancarios al bloque microfinanciero (`E0_financiero`) o a un predictor de encogimiento hacia la media histórica (`media_train`), reportando siempre las métricas desglosadas entre el panel corporativo `no_bancario` y el sector `bancario`.
3. **Fijación de hilos BLAS para reproducibilidad criptográfica bit a bit:** Para evitar variaciones de `1 ULP` (`~1e-15`) en la descomposición `SVD` de OpenBLAS entre ejecuciones sobre múltiples núcleos, se sugiere fijar `os.environ["OMP_NUM_THREADS"] = "1"` y `os.environ["OPENBLAS_NUM_THREADS"] = "1"` antes de importar `numpy`/`scipy` al inicio de los próximos notebooks.
