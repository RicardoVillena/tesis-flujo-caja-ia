# INFORME DE AUDITORÍA TÉCNICA Y METODOLÓGICA — EXTRACCIÓN MACROECONÓMICA (2005–2025)

- **Proyecto:** `tesis-flujo-caja-ia` (Maestría en Inteligencia Artificial — UNI)
- **Archivo principal auditado:** [`notebooks/03_extraccion_macroeconomica.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/03_extraccion_macroeconomica.ipynb)
- **Rama auditada:** `sprint-06-data-modeling` (`HEAD -> 485d2ce`)
- **Fecha de re-auditoría (versión corregida):** 21 de octubre de 2026
- **Entorno de verificación:** Conda `tesis-fcl` (`Python 3.12.15`, `pandas 3.0.6`, `numpy 2.5.4`, `matplotlib 3.11.2`, `requests 2.34.2`, `nbformat 5.11.1`, `nbclient 0.11.0`)
- **Dictamen final:** **APROBADO**

---

## 1. Resumen ejecutivo

Se realizó la auditoría integral e independiente de la versión corregida de [`notebooks/03_extraccion_macroeconomica.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/03_extraccion_macroeconomica.ipynb), junto con los cinco archivos crudos de [`data/raw/bcrp/`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/raw/bcrp/), el dataset consolidado [`data/processed/macroeconomia_peru_2005_2025.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/macroeconomia_peru_2005_2025.csv) y los siete artefactos diagnósticos y de trazabilidad en [`reports/`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/).

**Resultado de la re-auditoría:**
La entrega corregida por Codex **subsanó de manera verificable el 100% de los errores críticos (`CRIT-01`, `CRIT-02`), importantes (`IMP-01` a `IMP-06`) y observaciones técnicas (`OBS-01` a `OBS-04`)** detectados en la primera revisión:

1. **Extracción oficial BCRPData (`2005–2025`):** Se consultan y conservan cinco series oficiales del BCRP: PBI real en millones de soles de 2007 (`PM04860AA`), variación porcentual anual del PBI real (`PM04863AA`), IPC de Lima Metropolitana Dic. 2021 = 100 (`PN38705PM`, desde `Dic.2004`), tipo de cambio interbancario venta promedio mensual (`PN01206PM`) y tasa de interés de referencia monetaria (`PD04722MM`). Todos los archivos originales en [`data/raw/bcrp/`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/raw/bcrp/) cuentan con hash `SHA-256` verificado en [`manifest_2005_2025.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/raw/bcrp/manifest_2005_2025.json) y respaldo de versiones en [`data/raw/bcrp/versiones/`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/raw/bcrp/versiones/).
2. **Eliminación de fuga de información temporal (*data leakage*) en valores extremos (`CRIT-01` resuelto):** Los cuartiles $Q_1$ y $Q_3$ y los umbrales $\text{RIQ}$ se calculan exclusivamente sobre la ventana histórica de referencia `2005–2021` (`CORTE_RIQ = 2021`) y se proyectan sin reajuste sobre `2022–2025`. Las tasas de referencia de `2020` (`0,6667%`) y `2021` (`0,7708%`) quedan dentro del límite inferior histórico (`0,6354%`) y dejan de estar contaminadas por las subidas de tasas de `2022–2025`.
3. **Incorporación del crecimiento del PBI real (`CRIT-02` resuelto):** El dataset [`macroeconomia_peru_2005_2025.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/macroeconomia_peru_2005_2025.csv) (`21 filas × 5 variables`) incluye ahora `crecimiento_pbi_real_pct` (`PM04863AA`), cuya consistencia aritmética con las tasas de variación de `PM04860AA` (`2006–2025`) se verifica con tolerancia `atol = 0,02 pp`. El criterio RIQ se aplica sobre `crecimiento_pbi_real_pct` (y no sobre el nivel $I(1)$), identificando correctamente el choque COVID-19 de `2020` (`-10,9333%`).
4. **Reproducibilidad exacta y cumplimiento documental (`IMP-01` a `IMP-06` resueltos):** Se ejecutó el notebook completo (`31 celdas totales: 1 celda de título + 10 bloques × 3 celdas`) mediante `nbclient` en un entorno aislado temporal con el kernel `tesis-fcl` (`Python 3.12.15`). Los 7 archivos CSV generados coinciden **bit a bit (`SHA-256` idéntico)** con los del repositorio, el archivo [`reports/validacion_macroeconomia_bcrp.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/validacion_macroeconomia_bcrp.json) se produce íntegramente desde la Celda 29, y ningún archivo de `data/raw/bcrp/` es modificado ni reescrito cuando `ACTUALIZAR = False`.

---

## 2. Errores críticos

**Ninguno vigente (0 errores críticos pendientes).**

### Verificación de cierre de los errores críticos previos:
- **`CRIT-01` (Fuga temporal en umbrales RIQ — Celda 20):** **CORREGIDO Y VERIFICADO.**
  - *Evidencia:* En la Celda 20, `referencia = anual.loc[2005:CORTE_RIQ, variables_riq]` restringe el cálculo de `q1` y `q3` a `2005–2021`. En la Celda 26 se verifica mediante perturbación sintética (`alterado.loc[2022:] = alterado.loc[2022:] * 100 + 1000`) que los cuartiles históricos son 100% invariantes a los valores de `2022–2025`. Los tres valores extremos identificados y conservados sin alteración son: `crecimiento_pbi_real_pct` en `2020` (`-10,9333%`), `inflacion_lima_dic_dic_pct` en `2022` (`8,4592%`) y `tasa_referencia_promedio_pct` en `2023` (`7,5417%`).
- **`CRIT-02` (No estacionariedad del nivel de PBI y omisión de `crecimiento_pbi_real_pct` — Celdas 5, 17, 20 y 26):** **CORREGIDO Y VERIFICADO.**
  - *Evidencia:* Se descargó la serie oficial `PM04863AA` en [`data/raw/bcrp/PM04863AA_2005_2025.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/raw/bcrp/PM04863AA_2005_2025.json) (`SHA-256: ed135ac83d4ef5ffd665063a39f34fa17eb6dedeb9c15a02bc9881a187199e5b`), se integró `crecimiento_pbi_real_pct` al dataset anual y se excluyó el nivel `pbi_real_millones_soles_2007` de `variables_riq`.

---

## 3. Errores importantes

**Ninguno vigente (0 errores importantes pendientes).**

### Verificación de cierre de los errores importantes previos:
- **`IMP-01` (Trazabilidad de `validacion_macroeconomia_bcrp.json` — Celda 29):** **CORREGIDO Y VERIFICADO.** La Celda 29 genera la totalidad del archivo [`reports/validacion_macroeconomia_bcrp.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/validacion_macroeconomia_bcrp.json) con rutas relativas y control de secuencia de bloques (`etapas == list(range(1, 10))`).
- **`IMP-02` (Estándar de documentación por bloque — Celdas 0 a 30):** **CORREGIDO Y VERIFICADO.** Los 10 bloques cumplen estrictamente el patrón `[Celda Markdown: **N. Título** + descripción de 1–2 líneas] -> [Celda Code] -> [Celda Markdown: interpretación de 1 línea]`, con el título general separado en la Celda 0.
- **`IMP-03` (Clarificación de criterios de anualización — Celdas 4 y 5):** **CORREGIDO Y VERIFICADO.** Se documenta explícitamente la diferencia conceptual entre inflación acumulada diciembre/diciembre, variación de IPC medios anuales y promedios mensuales de tipo de cambio y tasa de referencia.
- **`IMP-04` (Manejo de excepciones HTTP/JSON y abreviaturas `sep/set/sept` — Celdas 8, 11 y 26):** **CORREGIDO Y VERIFICADO.** La Celda 8 captura errores de red, JSON y estructura identificando serie y URL, cierra la sesión en bloque `finally` y valida el contenido JSON incluso cuando el encabezado HTTP del BCRP reporta `text/html; charset=utf-8`. La Celda 11 soporta `sep`, `set` y `sept`.
- **`IMP-05` (Separación arquitectónica entre `data/processed/` y `reports/` — Celda 29):** **CORREGIDO Y VERIFICADO.** En `data/processed/` permanece únicamente [`macroeconomia_peru_2005_2025.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/macroeconomia_peru_2005_2025.csv), mientras los 7 archivos de metadatos, diccionario, calidad, cobertura, umbrales, extremos y validación se ubican en [`reports/`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/).
- **`IMP-06` (Regla de disponibilidad y cruce temporal sin fuga — Celda 5 y `diccionario_macroeconomia_bcrp.csv`):** **CORREGIDO Y VERIFICADO.** La columna `disponibilidad` establece expresamente la unión `anio = Ejercicio (t)` (nunca `anio_objetivo (t+1)`) y advierte sobre el desfase de publicación y las revisiones posteriores de cifras macroeconómicas.

---

## 4. Observaciones menores

### `OBS-01` (Nueva) — Texto de la columna `ponderacion` para `PN38705PM` en el diccionario de variables
- **Gravedad:** Menor (no bloqueante)
- **Archivo y ubicación:** [`notebooks/03_extraccion_macroeconomica.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/03_extraccion_macroeconomica.ipynb) (Celda 5, línea 13) y [`reports/diccionario_macroeconomia_bcrp.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/diccionario_macroeconomia_bcrp.csv#L3).
- **Detalle:** La expresión `np.where(series.frecuencia.eq("M"), "Media de registros mensuales: igual peso 1/12 cuando aplica; no media diaria", "No aplica")` asigna ese texto a las tres series mensuales (`PN38705PM`, `PN01206PM`, `PD04722MM`). Aunque incluye la salvedad *"cuando aplica"* y la columna `metodo` aclara `100 * (IPC diciembre / IPC diciembre previo - 1)`, sería aún más específico indicar `"No aplica (variación dic/dic)"` para `PN38705PM`.
- **Corrección recomendada (opcional):** Asignar la descripción de ponderación `1/12` únicamente a `PN01206PM` y `PD04722MM`.

### `OBS-02` (Preexistente) — Modificación previa sin confirmar en `README.md` en el árbol de Git
- **Gravedad:** Menor (higiene de repositorio)
- **Archivo y ubicación:** [`README.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/README.md#L270-L292).
- **Detalle:** `git status` muestra `M README.md` (edición en las líneas 270–292 anterior a la ejecución del notebook macroeconómico). La Celda 2 y la Celda 29 del notebook verifican correctamente que dicho archivo no fue alterado durante la ejecución (`SHA-256: 9e3f1448...`).
- **Corrección recomendada:** Confirmar o revertir `README.md` según decisión del autor del repositorio antes de realizar el *commit* de la rama.

### `OBS-03` (Informativa) — Reconexión HTTP en vivo durante la sesión de auditoría (`NO VERIFICADO`)
- **Gravedad:** Informativa (restricción del entorno de auditoría)
- **Archivo y ubicación:** [`notebooks/03_extraccion_macroeconomica.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/03_extraccion_macroeconomica.ipynb) (Celda 8, modo `ACTUALIZAR = True`).
- **Detalle:** Conforme a la Sección 8, la reconexión HTTP en vivo a `https://estadisticas.bcrp.gob.pe` desde el entorno aislado de auditoría se registra como **NO VERIFICADO**. Se verificaron al 100% los 5 archivos JSON crudos en [`data/raw/bcrp/`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/raw/bcrp/) (incluida la descarga de `PM04863AA` registrada en `manifest_2005_2025.json` con fecha `2026-10-21T21:30:02.542645+00:00`), sus hashes `SHA-256` y la ejecución completa del notebook desde la caché verificada (`ACTUALIZAR = False`).

---

## 5. Resultados de las verificaciones

| # | Categoría | Verificación | Estado | Evidencia verificada |
|---|---|---|---|---|
| 1.1 | Extracción | Procedencia de la API oficial del BCRP (`BCRPData`) | **APROBADO** | 5 archivos JSON en `data/raw/bcrp/` con URLs oficiales `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{codigo}/json/{inicio}/{fin}/esp` y estructura nativa `config` + `periods`. |
| 1.2 | Extracción | Exactitud de códigos de series (`PM04860AA`, `PM04863AA`, `PN38705PM`, `PN01206PM`, `PD04722MM`) | **APROBADO** | Códigos y metadatos `config.series[0].name` verificados para las 5 series. |
| 1.3 | Extracción | Correspondencia con PBI (nivel y crecimiento), inflación, tipo de cambio y tasa de interés | **APROBADO** | Las 5 variables cubren exactamente los cuatro indicadores macroeconómicos requeridos. |
| 1.4 | Extracción | Cobertura temporal 2005–2025 | **APROBADO** | 21 años (`2005–2025`) en series anuales (`PM04860AA`, `PM04863AA`), 252 meses en `PN01206PM` y `PD04722MM`, y 253 meses en `PN38705PM` (incluye `Dic.2004`). |
| 1.5 | Extracción | Ausencia de datos inventados o sustituidos sin justificación | **APROBADO** | Igualdad exacta respecto a los JSON originales (`rtol = 1e-12` en promedios/inflación e igualdad exacta en PBI nivel y crecimiento). |
| 1.6 | Extracción | Gestión de errores de conexión, codificación, HTML y abreviaturas (`sep/set/sept`) | **APROBADO** | Bloques `try/except/finally` con identificación de serie y URL, validación del cuerpo JSON y soporte verificado para `Sep`, `Set` y `Sept` (Celdas 8, 11 y 26). |
| 1.7 | Extracción | Reconexión HTTP en vivo (`ACTUALIZAR = True`) desde el sandbox de auditoría | **NO VERIFICADO** | Sandbox de auditoría sin acceso a red externa; verificados los 5 archivos descargados y sus hashes `SHA-256` en modo `ACTUALIZAR = False` (`OBS-03`). |
| 1.8 | Extracción | Trazabilidad e inmutabilidad de originales (`manifest_2005_2025.json` y `versiones/`) | **APROBADO** | Con `ACTUALIZAR = False`, los `mtime` y `SHA-256` de `data/raw/bcrp/` permanecen 100% inalterados; el historial previo del manifiesto se conserva en `data/raw/bcrp/versiones/`. |
| 2.1 | Estadística y Econometría | Frecuencia original y procedimientos de conversión a frecuencia anual | **APROBADO** | Nivel y variación oficial para PBI, variación Dic/Dic para IPC y media aritmética de 12 meses para TC y tasa de referencia. |
| 2.2 | Estadística y Econometría | Diferencias entre promedios, tasas de crecimiento y variaciones acumuladas | **APROBADO** | Documentadas en Celda 4 y en `reports/diccionario_macroeconomia_bcrp.csv`; consistencia verificada entre `PM04863AA` y `pct_change` de `PM04860AA` (`atol = 0,02 pp`). |
| 2.3 | Estadística y Econometría | Tratamiento de valores faltantes y ausencia de duplicados | **APROBADO** | `0` valores faltantes y `0` duplicados en las 5 series originales y en el dataset anual `(21, 5)`. |
| 2.4 | Estadística y Econometría | Identificación y conservación de valores extremos sobre variables adecuadas | **APROBADO** | El criterio RIQ se aplica a `crecimiento_pbi_real_pct`, `inflacion_lima_dic_dic_pct`, `tipo_cambio_promedio_soles_usd` y `tasa_referencia_promedio_pct`, detectando `2020` (PBI `-10,93%`), `2022` (inflación `8,46%`) y `2023` (tasa `7,54%`), conservándolos sin alteración. |
| 2.5 | Estadística y Econometría | Prevención de fuga de información temporal (*Data Leakage*) | **APROBADO** | Cuartiles RIQ calculados estrictamente sobre `2005–2021` (`CORTE_RIQ = 2021`), invariancia ante perturbaciones en `2022–2025` probada con `assert` en Celda 26, y llave `anio = Ejercicio (t)` documentada en el diccionario. |
| 3.1 | Código Python | Ejecución completa de las 10 celdas de código en `tesis-fcl` (`Python 3.12.15`) | **APROBADO** | Ejecutadas las 31 celdas (10 de código) mediante `nbclient` en entorno aislado sin errores (`0 errores`). |
| 3.2 | Código Python | Rutas relativas, compatibilidad Ubuntu/WSL y eficiencia | **APROBADO** | Resolución limpia de `ROOT` tanto desde la raíz como desde `notebooks/`; sin rutas absolutas locales en los archivos exportados. |
| 3.3 | Código Python | Consistencia exacta entre resultados en memoria y archivos exportados | **APROBADO** | Los 7 CSV son idénticos bit a bit (`SHA-256` exacto), la relectura con `float_precision="round_trip"` cumple `check_exact=True`, y `validacion_macroeconomia_bcrp.json` coincide al 100% con lo generado por la Celda 29. |
| 4.1 | Documentación | Título numerado en negrita y descripción de 2–3 líneas como máximo por bloque | **APROBADO** | Celdas Markdown `1, 4, 7, 10, 13, 16, 19, 22, 25, 28`: todas cuentan con título numerado en negrita (`**1.**` a `**10.**`) y de 1 a 2 líneas de descripción. |
| 4.2 | Documentación | Interpretación breve después de cada resultado relevante | **APROBADO** | Celdas Markdown `3, 6, 9, 12, 15, 18, 21, 24, 27, 30`: cada uno de los 10 bloques cuenta con su celda de interpretación breve independiente. |
| 4.3 | Documentación | Ausencia de textos sobre utilidad para la tesis | **APROBADO** | Redacción técnica, concisa y libre de comentarios especulativos sobre la tesis. |
| 5.1 | Datos generados | Dimensiones `(21, 5)`, cobertura `2005–2025`, completitud e integridad CSV | **APROBADO** | `data/processed/macroeconomia_peru_2005_2025.csv` (`SHA-256: 7dba8aec32f8eae7086b2cb393f7c22d9741314893bef1f8d081bc8d91b1377e`) contiene 21 filas y 5 columnas completas en precisión `float64`. |
| 6.1 | Git y Arquitectura | Respeto de notebooks previos, ubicación en `data/processed/` y `reports/`, sin credenciales | **APROBADO** | `EDA_FCL_2005_2025.ipynb` y `02_feature_engineering.ipynb` intactos; dataset en `data/processed/` y 7 reportes/metadatos en `reports/`; sin archivos temporales sueltos ni credenciales. |

---

## 6. Recomendaciones opcionales de refinamiento

1. **`[Opcional — OBS-01]`** En la Celda 5 de [`notebooks/03_extraccion_macroeconomica.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/03_extraccion_macroeconomica.ipynb), asignar `"No aplica (variación dic/dic)"` en la columna `ponderacion` para la serie `PN38705PM`, reservando el texto `"Media de registros mensuales: igual peso 1/12; no media diaria"` para `PN01206PM` y `PD04722MM`.
2. **`[Opcional — OBS-02]`** Revisar el cambio preexistente en [`README.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/README.md#L270-L292) (`M README.md`) antes de efectuar el *commit* de cierre del sprint.

---

## 7. Dictamen final

**DICTAMEN FINAL: APROBADO**

El notebook [`notebooks/03_extraccion_macroeconomica.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/03_extraccion_macroeconomica.ipynb) y sus artefactos derivados en [`data/raw/bcrp/`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/raw/bcrp/), [`data/processed/macroeconomia_peru_2005_2025.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/macroeconomia_peru_2005_2025.csv) y [`reports/`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/) cumplen rigurosamente todos los criterios de extracción oficial, validez estadística y econométrica, prevención de fuga temporal, reproducibilidad en Python (`tesis-fcl`), estructura documental de los 10 bloques y arquitectura del repositorio.
