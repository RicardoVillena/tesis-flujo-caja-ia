# Informe de Auditoría Técnica y Metodológica — Extracción de Variables Bursátiles (`05_extraccion_bursatil.ipynb`)

**Proyecto:** `tesis-flujo-caja-ia` — *Tesis de Maestría en Inteligencia Artificial (UNI)*  
**Archivo principal auditado:** `notebooks/05_extraccion_bursatil.ipynb` (`SHA-256: 6fa0c670a967500ef99e579f7887a77df368773556d3be2fa70bb38a4576c634`)  
**Entregables auditados:**  
- **Datos originales (`data/raw/bvl/`):** `530` capturas originales (`.bin` + `.meta.json`), `manifest_bursatil.json` y `README.md`  
- **Datos procesados (`data/processed/`):**  
  - `bursatil_mercado_anual.csv` (`21 × 17`, `SHA-256: f2f29a4a70cefe51c24a2b9b0e6e8a0a31ca75b856d4d24b897dc44b24bd4dfe`)  
  - `bursatil_mercado_mensual.csv` (`253 × 4`, `SHA-256: a0522c12621af4f737018af0cd678a14d9214b85a9f544504e27823cce987711`)  
  - `bursatil_mercado_diario.csv` (`5478 × 4`, `SHA-256: df3cebc3b15d7770ec4128ec2bb54927f270d32ba3133de8290ec348c4519ea1`)  
  - `bursatil_empresas_cobertura.csv` (`336 × 14`, `SHA-256: dc602de27ce324c372e9f5fcee39176a43a50ed7f57c8af29d5d9d177429760e`)  
  - `bursatil_registro_smv.csv` (`1032 × 30`, `SHA-256: b956f9a3aaf1f048cb687481061fb8de99196988407b277e38bc07f245a85ad4`)  
  - `bursatil_instrumentos_smv.csv` (`849 × 16`, `SHA-256: 9ac863c55669a2f8e917bf6d2782c45e5a96e3df693d3450706ab0caf2fa9be1`)  
- **Reportes y metadatos (`reports/`):** `14` archivos CSV de control/diccionario (`bursatil_*.csv`) y `validacion_extraccion_bursatil.json` (`SHA-256: 965830664a26ab215e3d75b566bd6a51a6580340928f1a85ec6c675bc501fd2c`)  
**Rama Git:** `sprint-06-data-modeling` (`HEAD -> 485d2ce`)  
**Fecha de auditoría:** 21 de octubre de 2026  
**Rol:** Auditor Senior Independiente (Python, Ciencia de Datos, Econometría Financiera y Machine Learning)

---

## 1. Resumen Ejecutivo

Se realizó una auditoría técnica, econométrica y metodológica exhaustiva e independiente del cuaderno `notebooks/05_extraccion_bursatil.ipynb` (43 celdas: 14 bloques de código ejecutados secuencialmente `1..14` y 29 celdas Markdown), así como de los 530 archivos crudos almacenados en `data/raw/bvl/`, los 6 datasets procesados en `data/processed/` y los 15 archivos de validación y catálogos en `reports/`.

1. **Trazabilidad e integridad de extracción (BCRP, SMV y BVL):**
   - Las 7 series agregadas del mercado bursátil peruano provienen directamente de la API oficial del BCRP (`PN01142MM`, `PN01159MM`, `PM06338MA`, `PM06345MA`, `PM06348MA`, `PD04694MD`, `PD04696MD`).
   - La identificación de valores inscritos proviene del servicio SOAP oficial de Datos Abiertos de la SMV (`ServiceValores.svc`, operaciones `consultaValoresRUC` y `consultaValoresRAZONSOCIAL`), ejecutando 512 consultas sobre las 336 empresas del panel financiero.
   - Se verificó criptográficamente (`SHA-256`) la integridad de las **530 respuestas crudas** (`.bin` y `.meta.json`) registradas en `data/raw/bvl/manifest_bursatil.json` y de las **20 tablas CSV exportadas**, sin que ningún archivo o notebook preexistente (`02`, `03`, `04`, `EDA`) sufriera modificaciones (`archivos_preexistentes_preservados`).
2. **Rigor econométrico y financiero:**
   - Se comprobó la exactitud matemática (`rtol = 1e-12`) de la rentabilidad anual diciembre/diciembre del Índice General BVL ($R_t = 100 \times (I_{\text{dic}, t} / I_{\text{dic}, t-1} - 1)$), la volatilidad diaria anualizada ($\sigma_t = 100 \times \text{std}(\ln(1+r_{d,t}), \text{ddof}=1) \times \sqrt{252}$) y el retorno diario compuesto ($100 \times (\prod(1+r_{d,t}) - 1)$).
   - El cuaderno identifica y preserva sin manipulación tres valores negativos de origen en la serie diaria de monto negociado en acciones `PD04696MD` (`05.May.16: -0.248453`, `06.May.16: -0.320838`, `09.May.16: -1.590270`), anulando únicamente la suma anual de dicho indicador diario en 2016 (`NaN`) mientras conserva intacta la serie oficial anual/mensual de renta variable (`PM06345MA` / `PN01159MM`).
   - Se evita cualquier sesgo de supervivencia (*survivorship bias*) o *look-ahead bias*: las 336 empresas se conservan íntegramente (`bursatil_empresas_cobertura.csv`) y las cotizaciones instantáneas devueltas por la SMV (incluyendo 138 fechas de última cotización en 2026) quedan aisladas en el registro de consulta (`cotizacion_asignada_al_panel = False`).

**Dictamen Final:** **APROBADO** (con 3 observaciones menores de carácter informativo y visual que no afectan la validez de los datos ni requieren reprocesamiento).

---

## 2. Errores Críticos

No se detectaron errores críticos de extracción, invención de datos, contaminación temporal (*data leakage*), sesgo de supervivencia ni alteración de archivos previos.

---

## 3. Errores Importantes

No se detectaron errores importantes en los cálculos financieros, el manejo de valores faltantes (`n.d.`), la validación de códigos ISIN ni la arquitectura de datos exportados.

---

## 4. Observaciones Menores

### `OBS-BUR-01` — Emisores recuperados por razón social exacta sin nodo `<RUC>` en la respuesta SOAP de la SMV

- **Severidad:** Menor (Documentada correctamente en el cuaderno; relevante para futuras uniones por empresa)
- **Archivo y ubicación:** `notebooks/05_extraccion_bursatil.ipynb` (Celda 23, líneas 704–710; Celda 26, líneas 762–764) y `data/processed/bursatil_empresas_cobertura.csv`.
- **Evidencia verificable:** De las 161 empresas con valores devueltos por el servicio SOAP de la SMV, 154 fueron localizadas mediante `consultaValoresRUC` (`EMISOR_VERIFICADO_RUC_Y_NOMBRE`) y 7 mediante la consulta de respaldo `consultaValoresRAZONSOCIAL` (`RESULTADO_CON_IDENTIDAD_PENDIENTE`):
  - 4 emisores constituidos en el extranjero cuyo `RUC` en el panel financiero de origen es `"0"`: `B60051` (`CREDICORP LTD.`, nemónico `BAP`), `OE2305` (`INTERCORP FINANCIAL SERVICES INC.`, nemónico `IFS`), `OE5087` (`INRETAIL PERU CORP.`, nemónico `INRETC1`) y `OE3161` (`MINERA IRL LIMITED`, nemónico `MIRL`).
  - 3 emisores nacionales con RUC de 11 dígitos cuya consulta `consultaValoresRUC` devolvió `CodigoError = 107` (*Empresa NO Inscrita en SMV*), pero que sí aparecen en `consultaValoresRAZONSOCIAL` con coincidencia exacta de razón social (`nombre_verificado == True`): `CD0022` (`EMPRESA ELECTRICIDAD DEL PERU - ELECTROPERU S.A.`, `ELECPBC1`), `CI0011` (`LAIVE S.A.`, `LAIVEBC1`) y `OE4115` (`AGROINDUSTRIAS AIB S.A.`, `AIBC1`).
- **Evaluación metodológica:** Dado que la estructura XML `ValorObtenidoBE` de la SMV no devuelve el RUC del emisor, la decisión de Codex de exigir `consulta_por == "RUC"` para marcar `correspondencia_emisor_verificada = True` es conservadora y metodológicamente correcta. En caso de utilizar el catálogo de emisores en análisis posteriores, se sugiere considerar una regla específica para emisores extranjeros (`RUC == "0"`) con coincidencia exacta de razón social y nemónico BVL.

---

### `OBS-BUR-02` — Marcas decimales de año (`2007.5`, `2012.5`, etc.) en el eje horizontal del gráfico de mercado (Celda 35)

- **Severidad:** Menor (Estética / Visualización)
- **Archivo y ubicación:** `notebooks/05_extraccion_bursatil.ipynb` (Celda 35, líneas 1022–1028).
- **Evidencia verificable:** En los cuatro subgráficos de la Celda 35 (`Indice General BVL: cierre`, `Variacion anual del indice`, `Volatilidad diaria anualizada`, `Renta variable negociada anual`), al graficar `ax.plot(anual.index, anual[col])` sin invocar `ax.set_xticks(range(2005, 2026, 4))`, `matplotlib` asigna marcas automáticas cada 2.5 años (`2005.0`, `2007.5`, `2010.0`, `2012.5`, `2015.0`, `2017.5`, `2020.0`, `2022.5`, `2025.0`).
- **Corrección recomendada (opcional):** Añadir `ax.set_xticks(range(2005, 2026, 4))` dentro del bucle de la Celda 35 (tal como se hizo en los cuadernos `03` y `04`) para mostrar únicamente años enteros.

---

### `OBS-BUR-03` — Códigos internos de 8 caracteres en el campo `<CodigoISIN>` del servicio SOAP de la SMV

- **Severidad:** Menor (Anomalía de la fuente oficial correctamente detectada y reportada)
- **Archivo y ubicación:** `notebooks/05_extraccion_bursatil.ipynb` (Celda 26, líneas 755–765) y `reports/bursatil_calidad_instrumentos.csv`.
- **Evidencia verificable:** Las 1,032 filas devueltas por el servicio `ServiceValores.svc` de la SMV contienen en el nodo `<CodigoISIN>` códigos internos de 8 caracteres (p. ej., `73630100`, `61630100`, `2519Y108`) sin el prefijo de país ISO 3166-1 alpha-2 (`PE` / `BM` / `PA`) ni el dígito verificador Luhn de la norma ISO 6166 (12 caracteres).
- **Evaluación metodológica:** El cuaderno implementa correctamente el validador `isin_valido` (formato `[A-Z]{2}[A-Z0-9]{9}[0-9]` + algoritmo de Luhn módulo 10), verifica que `isin_valido` es `False` en las 1,032 filas y se abstiene de autocompletar prefijos o dígitos verificadores sin respaldo documental.

---

## 5. Resultados de las Verificaciones

| Categoría | Verificación realizada | Evidencia / Resultado cuantitativo | Estado |
| :--- | :--- | :--- | :---: |
| **1. Extracción BCRP (Mercado)** | Consulta a la API oficial del BCRP de 7 series bursátiles (`2` mensuales, `3` anuales, `2` diarias) para `2005–2025` (más base `2004-12` / `2004`) | Códigos verificados: `PN01142MM` (`253` meses), `PN01159MM` (`252` meses), `PM06338MA` (`22` años), `PM06345MA` (`21` años), `PM06348MA` (`21` años), `PD04694MD` (`5,478` días), `PD04696MD` (`5,478` días). | **APROBADO** |
| **1. Extracción SMV (Valores)** | Consulta al Web Service SOAP oficial `ServiceValores.svc` (`consultaValoresRUC` y `consultaValoresRAZONSOCIAL`) sobre las 336 empresas | `512` consultas SOAP registradas con hash `SHA-256`; `1,032` filas de valores recibidas (`849` instrumentos únicos de `161` empresas; `154` verificadas por RUC y nombre). | **APROBADO** |
| **1. Verificación BVL e Históricos** | Inspección de recursos públicos de la BVL sin inventar endpoints ni atribuir cotizaciones vigentes a años pasados | Documentado como `API_PUBLICA_HISTORICA_NO_VERIFICADA` y `historicos_individuales_descargados = 0`; ninguna empresa fue eliminada (`empresas_conservadas = 336`). | **APROBADO** |
| **1. Trazabilidad y Caché (`data/raw/bvl/`)** | Comprobación de los `530` archivos `.bin` y `.meta.json` frente a `manifest_bursatil.json` | `530/530` archivos `.bin` coinciden bit a bit con su hash `SHA-256` registrado en `.meta.json` y en `manifest_bursatil.json`. | **APROBADO** |
| **2. Fórmulas de Rentabilidad y Volatilidad** | Contraste numérico de rentabilidad anual dic/dic, retorno diario compuesto y volatilidad anualizada ($\text{ddof}=1, \sqrt{252}$) | Diferencia máxima $< 10^{-12}$ respecto al recálculo independiente en los 21 años (`2005–2025`). | **APROBADO** |
| **2. Tratamiento de `n.d.` y Anomalías** | Verificación de no imputación de `199` `n.d.` en `PD04694MD`, `186` `n.d.` en `PD04696MD` y `3` montos negativos en mayo de 2016 | Los `n.d.` se mantienen como `NaN`; los 3 montos negativos de mayo de 2016 en `PD04696MD` se reportan en `bursatil_anomalias_montos.csv` y asignan `NaN` a la suma diaria de 2016. | **APROBADO** |
| **2. Cambio Metodológico (Mayo 2015) y Discrepancias** | Documentación del cambio IGBVL $\to$ S&P/BVL Peru General y contraste entre series mensuales, anuales y diarias | Se documenta la diferencia de `16.86` puntos en 2008 entre `PN01142MM` (`7048.67`) y `PM06338MA` (`7031.81`), así como las diferencias entre retorno compuesto diario y cierre mensual. | **APROBADO** |
| **2. Prevención de Data Leakage** | Separación entre instantánea SMV (`FechaUltCot` hasta oct-2026) y series históricas `2005–2025` | `cotizaciones_snapshot_fuera_periodo = 138` aisladas en el registro; `cotizacion_asignada_al_panel = False` en el 100% de instrumentos. | **APROBADO** |
| **3. Código Python y Ejecución** | Revisión de los 14 bloques de código (`execution_count` `1..14`), manejo de sesiones HTTP, reintentos y excepciones XML/JSON | Ejecución limpia de principio a fin sin errores; validación explícita de estructura JSON y nodos SOAP/XML. | **APROBADO** |
| **4. Documentación del Notebook** | Verificación de estructura en las 43 celdas (título general + 14 bloques `[Markdown título/desc] -> [Código] -> [Markdown interpretación]`) | Los 14 bloques tienen título numerado en negrita (`**1. ...**` a `**14. ...**`), descripción previa de 1–2 líneas e interpretación breve posterior sin texto superfluo. | **APROBADO** |
| **5. Integridad de los 20 CSV Exportados** | Comprobación de dimensiones, tipos, ausencia de duplicados y hashes `SHA-256` contra `validacion_extraccion_bursatil.json` | Los 6 CSV en `data/processed/` y 14 CSV en `reports/` coinciden al 100% en filas, columnas y hash `SHA-256`. | **APROBADO** |
| **6. Arquitectura y Preservación Git** | Verificación de inmutabilidad de archivos previos (`02`, `03`, `04`, `EDA`, CSV financieros/macro y `README.md`) | Todos los hashes registrados en `archivos_preexistentes_preservados` permanecen intactos. | **APROBADO** |

---

## 6. Recomendaciones

1. **Para visualización (opcional, `OBS-BUR-02`):** Si se vuelve a ejecutar `05_extraccion_bursatil.ipynb`, añadir `ax.set_xticks(range(2005, 2026, 4))` en la Celda 35 para evitar etiquetas de año con decimales (`.5`).
2. **Para una eventual integración de variables bursátiles de mercado al panel (`OBS-BUR-03`):** En caso de incorporar variables de `data/processed/bursatil_mercado_anual.csv` al panel financiero-macroeconómico, priorizar los indicadores relativos (`rentabilidad_indice_anual_pct`, `volatilidad_diaria_anualizada_pct`) sobre los niveles nominales (`indice_general_cierre`, `capitalizacion_millones_pen`), respetando siempre la unión por `Ejercicio == anio` ($t$) y nunca por `anio_objetivo` ($t+1$).

---

## 7. Dictamen Final

**DICTAMEN:** **APROBADO**

El cuaderno `notebooks/05_extraccion_bursatil.ipynb`, sus 530 archivos crudos respaldados en `data/raw/bvl/`, los 6 datasets procesados en `data/processed/` y los 15 reportes de control y validación en `reports/` cumplen rigurosamente con todos los criterios de trazabilidad, exactitud econométrica, manejo transparente de limitaciones de fuente, prevención de *data leakage* y calidad documental.

