# Informe de Auditoría Técnica y Metodológica — Integración de Variables Bursátiles (`06_integracion_bursatil.ipynb`)

**Proyecto:** `tesis-flujo-caja-ia` — *Tesis de Maestría en Inteligencia Artificial (UNI)*  
**Notebook auditado:** `notebooks/06_integracion_bursatil.ipynb` (`SHA-256: d6178e3d76739762577108afea049572f2cab8361a83d5aa87fb0a54b30103e6`)  
**Salidas auditadas:**  
- `data/processed/panel_financiero_macro_bursatil.csv` (`4221 × 68`, `SHA-256: c0a116958c422ffc93daa218b5cc1f47e85831a7137e029f312fee5b6d0b4b2c`)  
- `reports/diccionario_integracion_bursatil.csv` (`68 × 21`, `SHA-256: 20eeb1f82b1f29329c1eaaf25071f1f00a53aade1e576b0db2291e48bbd30534`)  
- `reports/validacion_integracion_bursatil.json` (`SHA-256: 222c0c19c022c2933a7b010e1d338874b38f8ab2df87460ff8d371a5e847b5d1`)  
**Entradas verificadas:**  
- `data/processed/panel_financiero_macroeconomico.csv` (`4221 × 62`, `SHA-256: 435148cba6e72380fd96ee809bc7cd8a0875ae629b9c12b04254bf71d38bde99`)  
- `data/processed/bursatil_mercado_anual.csv` (`21 × 17`, `SHA-256: f2f29a4a70cefe51c24a2b9b0e6e8a0a31ca75b856d4d24b897dc44b24bd4dfe`)  
**Rama Git:** `sprint-06-data-modeling` (`HEAD -> 485d2ce`)  
**Entorno de ejecución verificado:** Conda `tesis-fcl` (`Python 3.12.15`)  
**Fecha de auditoría:** 21 de octubre de 2026  
**Rol:** Auditor Independiente (Python, Ciencia de Datos, Econometría y Mercados Financieros)

---

## 1. Resumen de Verificaciones

Se ejecutó una auditoría integral e independiente sobre `notebooks/06_integracion_bursatil.ipynb` y sus archivos de salida, combinando inspección estática de las 34 celdas (11 bloques de código ejecutados secuencialmente `1..11` y 23 celdas Markdown), recálculo matemático de las series bursátiles contra las fuentes originales del BCRP, verificación celda por celda de la matriz consolidada (`4,221 × 68`) y re-ejecución completa del notebook en un directorio temporal aislado mediante `nbclient` en el entorno `tesis-fcl`.

| Dimensión Auditada | Verificación Ejecutada | Evidencia / Resultado Cuantitativo | Estado |
| :--- | :--- | :--- | :---: |
| **1. Integración: Filas y Empresas** | Conservación de las `4,221` observaciones y `336` empresas (`RPJ`) | `4,221` filas antes y después; `336` códigos `RPJ` únicos (`len=6`); orden de filas 100% idéntico (`__orden_bursatil__`). | **APROBADO** |
| **1. Integración: 62 Columnas Previas** | Integridad exacta de las 62 columnas financieras y macroeconómicas | Diferencia numérica máxima $= 0.0$ (`float_precision="round_trip"`); `20,675` valores faltantes previos intactos; `0` faltantes añadidos. | **APROBADO** |
| **1. Integración: Clave y Cardinalidad** | Unión izquierda (`how="left"`, `validate="many_to_one"`) mediante `Ejercicio == anio` ($t$) | `4,221` coincidencias exactas en `2005–2025`; `0` filas sin coincidencia; `0` duplicados `(RPJ, Ejercicio)` antes y después; sin uso de `anio_objetivo` ($t+1$). | **APROBADO** |
| **1. Integración: Identificadores y Particiones** | Conservación de `RPJ`, `RUC`, `objetivo_fcl_t1`, `anio_objetivo` y `particion` | `RPJ` (`336`) y `RUC` (`331` distintos, incluyendo las `63` filas de origen con `RUC="0"`) exactos; `entrenamiento=2,869`, `prueba=691`, `sin_etiqueta_elegible=661`. | **APROBADO** |
| **1. Integración: Fuentes y Exclusión de Cotizaciones Individuales** | Correspondencia con fuentes BCRP y ausencia de cotizaciones individuales no verificadas | Se integran `3` indicadores de mercado agregado (`PN01142MM`, `PD04694MD`, `PM06345MA`) y `3` controles metodológicos; `sin_instrumentos_individuales = True`. | **APROBADO** |
| **2. Econometría: Fórmulas y Unidades** | Recálculo de rentabilidad dic/dic, volatilidad diaria anualizada ($\text{ddof}=1, \sqrt{252}$) y monto anual de renta variable | Discrepancia $< 10^{-12}$ frente a `bursatil_mercado_mensual.csv`, `bursatil_mercado_diario.csv` y el JSON crudo `PM06345MA` en los `21` años (`2005–2025`). | **APROBADO** |
| **2. Econometría: Faltantes, Extremos y Estacionariedad** | Exclusión de niveles no estacionarios (`indice_general_cierre`, `capitalizacion_millones_pen`) y de la suma diaria con anomalía en 2016 | `0` faltantes en las `6` columnas bursátiles integradas; `0.00%` de observaciones de prueba fuera del soporte de entrenamiento en rentabilidad (`[-59.78%, 168.30%]`) y volatilidad (`[9.80%, 46.05%]`). | **APROBADO** |
| **2. Econometría: Prevención de Data Leakage** | Cálculo de estadísticos exclusivamente sobre los `16` años únicos de entrenamiento (`2005–2020`) y prueba de perturbación | Perturbar la partición de prueba (`* 100 + 1000`) deja exactamente invariantes (`check_exact=True`) las estadísticas descriptivas y la selección de predictores. | **APROBADO** |
| **2. Econometría: Disponibilidad Real Histórica** | Distinción explícita entre correspondencia anual (`Ejercicio = anio`) y disponibilidad *point-in-time* en la fecha de predicción | Documentado como `"disponibilidad_real_historica": "NO_VERIFICADA"` por falta de fechas efectivas de publicación y versiones históricas (*vintages*). | **NO VERIFICADO** *(Limitación de origen documentada)* |
| **3. Estructura y Documentación del Notebook** | Revisión de las 34 celdas (Celda 0 + 11 bloques `[Markdown título/desc] -> [Código] -> [Markdown interpretación]`) | Los 11 bloques cumplen: título numerado en negrita (`**1. ...**` a `**11. ...**`), descripción previa de 1–2 líneas, ejecución limpia (`1..11`) e interpretación breve de 1–2 líneas. | **APROBADO** |
| **4. Reproducibilidad (`tesis-fcl`)** | Ejecución aislada completa con `nbclient` en `tesis-fcl` (`Python 3.12.15`) sin sobrescribir originales | Regeneración bit a bit idéntica del panel (`SHA-256: c0a11695...0b4b2c`) y del diccionario (`SHA-256: 20eeb1f8...30534`). | **APROBADO** |
| **5. Arquitectura y Preservación Git** | Inmutabilidad de los notebooks `02`, `03`, `04`, `05`, `EDA` y todos los datasets previos | Verificación criptográfica de los `76` archivos preexistentes protegidos (`archivos_previos_preservados = True`). | **APROBADO** |

---

## 2. Errores Críticos

No se encontraron errores críticos. La unión preserva exactamente la estructura del panel, evita el uso de información futura de $t+1$ (`anio_objetivo`), no introduce cotizaciones individuales no verificadas y mantiene inalteradas las 62 columnas precedentes.

---

## 3. Errores Importantes

No se encontraron errores importantes. Cabe destacar que el cuaderno incorpora proactivamente la recomendación econométrica de la auditoría previa (`OBS-BUR-03`), **excluyendo las variables bursátiles en niveles** (`indice_general_cierre`, `indice_cierre_publicado_anual`, `capitalizacion_millones_pen`) y la suma diaria afectada por montos negativos en mayo de 2016 (`monto_acciones_suma_observaciones_diarias_millones_pen`), e integrando únicamente:
1. **Tres candidatos predictivos de mercado agregado (`predictor_candidato = True`):**
   - `rentabilidad_indice_anual_pct` (`PN01142MM`, variación % diciembre/diciembre).
   - `volatilidad_diaria_anualizada_pct` (`PD04694MD`, $100 \times \text{std}(\ln(1+r_d), \text{ddof}=1) \times \sqrt{252}$).
   - `monto_renta_variable_anual_millones_pen` (`PM06345MA`, monto anual oficial negociado en renta variable en millones de PEN).
2. **Tres variables de control diagnóstico (`predictor_candidato = False`, `rol_en_dataset = "control"`):**
   - `transicion_metodologica_2015` (booleano que marca el cambio metodológico de mayo de 2015 entre el IGBVL y el S&P/BVL Peru General).
   - `regimen_documentado` (categoría documental: `"IGBVL previo"`, `"Transicion mayo 2015"`, `"S&P/BVL Peru General"`).
   - `diferencia_diario_mensual_revisar` (booleano para los 11 años donde $|\text{retorno compuesto diario} - \text{retorno dic/dic}| > 0.1$ puntos porcentuales).

---

## 4. Observaciones Menores

### `OBS-IBUR-01` — Escala nominal en soles de `monto_renta_variable_anual_millones_pen` y leve desplazamiento de soporte en 2023

- **Clasificación:** OBSERVADO (Menor — documentado en `reports/validacion_integracion_bursatil.json`, línea 768)
- **Ubicación:** `notebooks/06_integracion_bursatil.ipynb` (Celdas 26 y 29) y `data/processed/panel_financiero_macro_bursatil.csv`.
- **Evidencia verificable:** Mientras que `rentabilidad_indice_anual_pct` y `volatilidad_diaria_anualizada_pct` tienen el **100.00% (`691/691`)** de las observaciones de la partición de prueba (`Ejercicio` `2021–2024`) dentro del soporte histórico de entrenamiento (`2005–2020`), la variable `monto_renta_variable_anual_millones_pen` presenta en el año `2023` un valor de `6,807.1860` millones de PEN, ligeramente inferior al mínimo de entrenamiento (`7,727.7840` millones de PEN en `2015`), lo que ubica al **25.18% (`174/691`)** de las filas de prueba fuera del rango de entrenamiento.
- **Explicación:** El cuaderno ya advierte explícitamente en la Celda 26 que *"su escala nominal requiere evaluar idoneidad posteriormente"*. En la etapa de modelado supervisado se podrá evaluar si conviene expresarla como variación porcentual o razón respecto al PBI nominal/capitalización, siempre ajustando cualquier transformación exclusivamente dentro de la partición de entrenamiento.

---

### `OBS-IBUR-02` — Baja dimensión temporal efectiva ($T_{\text{train}} = 16$ años) en regresores agregados de mercado

- **Clasificación:** OBSERVADO (Menor — propiedad estructural del panel documentada en Celda 26)
- **Ubicación:** `notebooks/06_integracion_bursatil.ipynb` (Celdas 26 y 29).
- **Evidencia verificable:** Al ser indicadores agregados del mercado bursátil peruano, todas las empresas de un mismo `Ejercicio` $t$ comparten el mismo valor anual. En la partición de entrenamiento (`2005–2020`, `2,869` observaciones) existen `16` puntos temporales distintos para las variables macroeconómicas y bursátiles combinadas ($4$ predictores macro + $3$ predictores bursátiles $= 7$ regresores agregados anuales frente a $T_{\text{train}} = 16$).
- **Explicación:** En la etapa de modelado debe controlarse la colinealidad entre regresores agregados anuales y aplicarse validación cruzada por bloques anuales (*expanding window* sobre `Ejercicio`) para evitar que árboles profundos memoricen identificadores de año.

---

### `OBS-IBUR-03` — Disponibilidad histórica efectiva (*real-time vintage*) no verificable en las fuentes de origen

- **Clasificación:** NO VERIFICADO (Limitación intrínseca de las fuentes públicas documentada por el autor)
- **Ubicación:** `notebooks/06_integracion_bursatil.ipynb` (Celdas 26 y 32) y `reports/validacion_integracion_bursatil.json` (`"disponibilidad_real_historica": "NO_VERIFICADA"`).
- **Explicación:** El cuaderno distingue con rigor metodológico entre la **correspondencia anual del ejercicio** (`Ejercicio == anio`, verificada al 100% y libre de cruce con `anio_objetivo` $t+1$) y la **disponibilidad histórica efectiva** en la fecha exacta de emisión de cada estado financiero, dado que ni la SMV ni el BCRP proveen marcas de tiempo históricas de publicación o versiones sin revisión (*vintages*) para 2005–2025.

---

## 5. Resultados de Pruebas de Reproducibilidad e Integridad

1. **Ejecución completa en entorno `tesis-fcl` (Sección 4):**
   - Se ejecutó `notebooks/06_integracion_bursatil.ipynb` de principio a fin mediante `nbclient` usando `/home/ricardo/miniconda3/envs/tesis-fcl/bin/python` (`Python 3.12.15`) en un directorio temporal aislado.
   - Las 11 celdas de código finalizaron sin errores ni advertencias de ejecución, regenerando exactamente los mismos archivos de salida:
     - `data/processed/panel_financiero_macro_bursatil.csv`: `4,221` filas × `68` columnas (`SHA-256: c0a116958c422ffc93daa218b5cc1f47e85831a7137e029f312fee5b6d0b4b2c`).
     - `reports/diccionario_integracion_bursatil.csv`: `68` variables × `21` metadatos (`SHA-256: 20eeb1f82b1f29329c1eaaf25071f1f00a53aade1e576b0db2291e48bbd30534`).
2. **Verificación celda por celda contra archivos originales:**
   - Las primeras `62` columnas de `panel_financiero_macro_bursatil.csv` son idénticas bit a bit a `panel_financiero_macroeconomico.csv` (diferencia numérica máxima $= 0.0$ en las `4,221` filas).
   - Las `6` columnas nuevas coinciden exactamente en cada fila con el registro de `bursatil_mercado_anual.csv` correspondiente a su `Ejercicio` ($t$).
   - Los valores extremos históricos del mercado (como el auge de `+168.2951%` en `2006` y la caída de `-59.7789%` con volatilidad de `46.0531%` durante la crisis financiera internacional de `2008`) se conservan íntegros sin recortes ni *winsorization* arbitraria.
3. **Auditoría del formato documental del notebook (Sección 3):**
   - El cuaderno consta de 34 celdas: 1 celda inicial de título general y 11 bloques compuestos por `[Celda Markdown de título en negrita y descripción de 1–2 líneas] -> [Celda de código Python con execution_count 1..11] -> [Celda Markdown de interpretación breve de 1–2 líneas]`.
   - En los gráficos de la Celda 29 se incluyen marcas enteras de año (`ax.set_xticks(range(2005, 2026, 5))`), corrigiendo la observación estética reportada en el cuaderno anterior.
4. **Auditoría de arquitectura y preservación del repositorio (Sección 5):**
   - Se comprobó mediante hashes `SHA-256` que ningún archivo previo (`notebooks/02_feature_engineering.ipynb`, `notebooks/03_extraccion_macroeconomica.ipynb`, `notebooks/04_integracion_datos.ipynb`, `notebooks/05_extraccion_bursatil.ipynb`, `notebooks/EDA_FCL_2005_2025.ipynb`, ni sus datasets en `data/raw/` y `data/processed/`) fue alterado.

---

## 6. Recomendaciones

1. **Selección automatizada de predictores desde el catálogo en la etapa de modelado:** Utilizar la columna `predictor_candidato == True` de `reports/diccionario_integracion_bursatil.csv` para garantizar que tanto `pbi_real_millones_soles_2007` como los tres controles metodológicos bursátiles (`transicion_metodologica_2015`, `regimen_documentado`, `diferencia_diario_mensual_revisar`) queden excluidos de la matriz predictiva $X$.
2. **Regularización y validación temporal de regresores anuales agregados:** Dado que los 4 predictores macroeconómicos y los 3 predictores bursátiles varían únicamente por año ($T_{\text{train}} = 16$ ejercicios en `2005–2020`), emplear validación cruzada temporal por bloques anuales (*expanding window*) y evaluar análisis de sensibilidad con y sin el bloque de variables agregadas.

---

## 7. Dictamen Final

**DICTAMEN:** **APROBADO**

El cuaderno `notebooks/06_integracion_bursatil.ipynb`, el panel consolidado `data/processed/panel_financiero_macro_bursatil.csv` (`4,221 × 68`), el catálogo `reports/diccionario_integracion_bursatil.csv` y el archivo de control `reports/validacion_integracion_bursatil.json` cumplen íntegramente con todos los requisitos técnicos, econométricos, de reproducibilidad en `tesis-fcl` y de prevención de fuga de información temporal.

