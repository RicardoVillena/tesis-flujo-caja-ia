# tesis-flujo-caja-ia
# Predicción del Flujo de Caja Libre mediante Inteligencia Artificial

## Descripción del proyecto

Este proyecto corresponde al desarrollo de una tesis de Maestría en Inteligencia Artificial orientada a la predicción del Flujo de Caja Libre (Free Cash Flow, FCL) mediante técnicas de Machine Learning, Deep Learning e Inteligencia Artificial Explicable.

La investigación busca desarrollar y evaluar modelos capaces de mejorar la estimación del flujo de caja libre utilizando información financiera histórica, variables empresariales y, cuando corresponda, variables macroeconómicas.

El sistema permitirá comparar modelos financieros tradicionales con modelos basados en inteligencia artificial y determinar si estos últimos permiten obtener mejores resultados predictivos.

---

## Objetivo general

Desarrollar un modelo basado en inteligencia artificial para la predicción del Flujo de Caja Libre de empresas, evaluando su precisión frente a métodos tradicionales de estimación financiera.

---

## Objetivos específicos

1. Analizar y preparar los datos financieros históricos utilizados en la investigación.

2. Identificar las variables financieras con mayor relación con el comportamiento del Flujo de Caja Libre.

3. Desarrollar modelos tradicionales, de Machine Learning y Deep Learning para la predicción financiera.

4. Comparar el desempeño de los modelos mediante métricas estadísticas y predictivas.

5. Aplicar técnicas de Inteligencia Artificial Explicable para identificar la influencia de las variables sobre las predicciones.

6. Generar escenarios financieros y estimaciones de incertidumbre mediante simulación.

---

## Variable objetivo

La variable principal de la investigación es el Flujo de Caja Libre.

Su cálculo general se representa mediante:

FCL = EBIT × (1 − Tasa de impuesto) + Depreciación − CAPEX − Δ Capital de Trabajo

Los principales componentes considerados son:

EBIT  
Tasa de impuesto  
Depreciación y amortización  
CAPEX  
Capital de trabajo  
Ventas  
Costos  
Márgenes operativos  
Variables financieras históricas  
Variables macroeconómicas

---

## Técnicas utilizadas

### 1. Análisis Exploratorio de Datos

Se realizará un análisis exploratorio para conocer las principales características de los datos.

Se analizarán:

Distribución de variables  
Tendencias históricas  
Correlaciones  
Valores faltantes  
Valores atípicos  
Estacionalidad  
Comportamiento temporal de las variables financieras

---

## 2. Preprocesamiento de datos

El proceso de preparación incluirá:

Limpieza de datos  
Tratamiento de valores faltantes  
Detección y tratamiento de outliers  
Normalización o estandarización  
Transformación de variables  
Codificación cuando corresponda  
Organización cronológica de las observaciones

---

## 3. Ingeniería de características

Se crearán nuevas variables que puedan mejorar la capacidad predictiva de los modelos.

Entre ellas:

Rezagos temporales  
Promedios móviles  
Tasas de crecimiento  
Variaciones porcentuales  
Ratios financieros  
Margen operativo  
ROA  
ROE  
Nivel de endeudamiento  
Capital de trabajo  
CAPEX  
Crecimiento de ventas  
Variables macroeconómicas

---

## 4. Modelos de referencia

Se utilizarán modelos tradicionales como línea base de comparación.

Entre los modelos considerados se encuentran:

Regresión lineal  
ARIMA  
Modelos financieros tradicionales de proyección

Estos modelos servirán como benchmark para evaluar las mejoras obtenidas mediante inteligencia artificial.

---

## 5. Machine Learning

Los principales algoritmos considerados son:

Random Forest  
XGBoost  
LightGBM  
Support Vector Regression  
Regresión regularizada

Estos modelos permitirán identificar relaciones no lineales entre las variables financieras.

---

## 6. Deep Learning

Para el análisis de series temporales podrán evaluarse modelos de redes neuronales como:

LSTM  
GRU  
Redes neuronales multicapa

LSTM y GRU permitirán capturar dependencias temporales presentes en los datos financieros.

---

## 7. Validación temporal

Debido a la naturaleza temporal de los datos financieros, no se realizará únicamente una división aleatoria de entrenamiento y prueba.

Se utilizarán técnicas como:

Train-Test temporal  
Time Series Cross Validation  
Walk-Forward Validation

Esto permitirá evitar la fuga de información del futuro hacia el entrenamiento del modelo.

---

## 8. Métricas de evaluación

Los modelos serán evaluados mediante diferentes métricas.

MAE – Mean Absolute Error

RMSE – Root Mean Squared Error

MAPE – Mean Absolute Percentage Error

sMAPE – Symmetric Mean Absolute Percentage Error

R² – Coeficiente de determinación

Las métricas permitirán determinar qué modelo ofrece mayor precisión en la predicción del Flujo de Caja Libre.

---

## 9. Inteligencia Artificial Explicable

Se utilizarán técnicas de Explainable Artificial Intelligence para interpretar las predicciones realizadas por los modelos.

La principal técnica considerada es:

SHAP – SHapley Additive exPlanations

SHAP permitirá identificar:

Variables más importantes  
Impacto de cada variable  
Dirección de la influencia  
Explicación global del modelo  
Explicación individual de cada predicción

---

## 10. Simulación Monte Carlo

La simulación Monte Carlo permitirá incorporar incertidumbre dentro de las proyecciones financieras.

Se podrán generar múltiples escenarios modificando variables como:

Ventas  
Costos  
Margen operativo  
CAPEX  
Capital de trabajo  
Tasa de crecimiento

Como resultado se obtendrá una distribución probabilística del Flujo de Caja Libre en lugar de una única predicción puntual.

---

## 11. Análisis de escenarios

El sistema permitirá generar diferentes escenarios financieros.

Escenario optimista  
Escenario base  
Escenario pesimista  
Escenario de estrés

Estos escenarios podrán utilizarse como apoyo para la toma de decisiones financieras.

---

## Metodología de ingesta de datos (propuesta; implementación parcial)

La investigación empleará un proceso de ingesta estructurado, reproducible y trazable para integrar información financiera proveniente principalmente de la Superintendencia del Mercado de Valores (SMV), complementada posteriormente con información bursátil de la Bolsa de Valores de Lima (BVL) y variables macroeconómicas oficiales.

### Fuente principal: Superintendencia del Mercado de Valores

La SMV será utilizada como fuente principal para la obtención de información financiera histórica de las empresas consideradas en la investigación.

La ingesta comprenderá principalmente información proveniente de:

- Estado de Situación Financiera
- Estado de Resultados
- Estado de Flujos de Efectivo
- Información financiera complementaria

Las principales variables a recuperar serán:

- Ventas
- EBIT o utilidad operativa
- Impuesto a la renta
- Depreciación y amortización
- Activo corriente
- Pasivo corriente
- Efectivo
- Cuentas por cobrar
- Inventarios
- Propiedad, planta y equipo
- CAPEX
- Flujo de efectivo operativo



### Servicio Web de Información Financiera de la SMV

La automatización de la ingesta de datos financieros se realizará mediante el Web Service oficial de Información Financiera de la Superintendencia del Mercado de Valores (SMV), disponible en https://mvnet.smv.gob.pe/ws_od_eeff/WebServiceInfoFinanciera.asmx. Este servicio permite consultar programáticamente diferentes estados financieros mediante las operaciones `obtener_BalanceGeneral`, `obtener_CambiosPatrimonio`, `obtener_EFData`, `obtener_FlujoEfectivo`, `obtener_GanciaPerdida`, `obtener_InfoFinanciera` y `obtener_ResultadosIntegrales`.

Para esta investigación se priorizarán las operaciones `obtener_InfoFinanciera`, para identificar empresas y periodos disponibles; `obtener_BalanceGeneral`, para recuperar información de activos, pasivos, patrimonio y capital de trabajo; `obtener_GanciaPerdida`, para obtener ventas, utilidad operativa, EBIT e impuesto; y `obtener_FlujoEfectivo`, para recuperar información relacionada con flujos operativos, actividades de inversión y componentes vinculados con el CAPEX.

El proceso de ingesta realizará consultas automáticas por ejercicio, periodo y tipo de información financiera mediante scripts desarrollados en Python. Estos scripts enviarán solicitudes al Web Service de la SMV, recibirán respuestas en formato XML/SOAP, extraerán los registros y los convertirán a una estructura tabular adecuada para su procesamiento.

La información recopilada se organizará en tres etapas. En la primera se conservarán los datos originales obtenidos de las fuentes oficiales, sin alterar su contenido. En la segunda se efectuarán los procedimientos de depuración, homologación, normalización y validación de los registros. Finalmente, se integrarán las variables financieras, macroeconómicas y bursátiles en un conjunto de datos estructurado para el cálculo del Flujo de Caja Libre y el desarrollo de los modelos predictivos.

El proceso comprenderá la consulta automatizada de los servicios de información financiera de la SMV, la recuperación de los estados financieros, la recepción y transformación de los registros XML/SOAP, el almacenamiento de los archivos originales, la depuración y validación de los datos y la construcción del conjunto de información consolidado. Posteriormente, se incorporarán las variables macroeconómicas y bursátiles disponibles, y se preparará el conjunto de datos para el entrenamiento y evaluación de los modelos de inteligencia artificial.

Para garantizar la trazabilidad y reproducibilidad del proceso, cada consulta almacenará metadatos como fecha de ingesta, fuente, operación utilizada, ejercicio, periodo, tipo de información, empresa, estado de la consulta, número de registros y archivo de origen.

### Proceso de adquisición, preparación e integración de datos

El procesamiento de la información comprende tres etapas:

1. Adquisición de datos: recuperación y almacenamiento de los registros originales procedentes de las fuentes oficiales, conservando su estructura y procedencia.

2. Preparación y validación: depuración de registros, homologación de variables, estandarización de formatos y verificación de consistencia temporal y financiera.

3. Integración de datos: consolidación de las variables empresariales, macroeconómicas y bursátiles en un conjunto de información longitudinal destinado al análisis estadístico y al desarrollo de modelos predictivos.

---

# Pipeline de la investigación

Datos financieros históricos

↓

Limpieza y preprocesamiento

↓

Análisis Exploratorio de Datos

↓

Ingeniería de características

↓

Selección de variables

↓

Modelos tradicionales

↓

Machine Learning

↓

Deep Learning

↓

Validación temporal

↓

Evaluación de métricas

↓

Selección del mejor modelo

↓

Inteligencia Artificial Explicable – SHAP

↓

Simulación Monte Carlo

↓

Generación de escenarios

↓

Predicción del Flujo de Caja Libre

↓

Apoyo a la toma de decisiones financieras

---

# Arquitectura propuesta

```text
FUENTES DE DATOS
       |
       v
INGESTA DE DATOS
       |
       v
PREPROCESAMIENTO
       |
       v
EDA
       |
       v
FEATURE ENGINEERING
       |
       v
SELECCIÓN DE VARIABLES
       |
       +-----------------------------+
       |              |              |
       v              v              v
    ARIMA          XGBoost        LSTM / GRU
       |              |              |
       +--------------+--------------+
                      |
                      v
              COMPARACIÓN DE MODELOS
                      |
                      v
               MEJOR MODELO
                      |
             +--------+--------+
             |                 |
             v                 v
           SHAP          MONTE CARLO
             |                 |
             +--------+--------+
                      |
                      v
                ESCENARIOS
                      |
                      v
            PREDICCIÓN DEL FCL
```

---

# Tecnologías

Python

Pandas

NumPy

Scikit-learn

XGBoost

LightGBM

TensorFlow / Keras

Statsmodels

SHAP

Matplotlib

Jupyter Notebook

Streamlit

---

# Estructura del proyecto

```text
tesis_flujo_caja_ia/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_preprocesamiento.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_modelo_baseline.ipynb
│   ├── 05_machine_learning.ipynb
│   ├── 06_deep_learning.ipynb
│   ├── 07_validacion.ipynb
│   ├── 08_shap.ipynb
│   └── 09_monte_carlo.ipynb
│
├── src/
│   ├── data_processing.py
│   ├── feature_engineering.py
│   ├── models.py
│   ├── evaluation.py
│   ├── explainability.py
│   └── simulation.py
│
├── models/
│
├── results/
│   ├── figures/
│   ├── metrics/
│   └── predictions/
│
├── app/
│   └── app.py
│
├── requirements.txt
│
└── README.md
```

---

# Flujo de ejecución

El proyecto seguirá aproximadamente la siguiente secuencia:

```text
01_eda.ipynb

02_preprocesamiento.ipynb

03_feature_engineering.ipynb

04_modelo_baseline.ipynb

05_machine_learning.ipynb

06_deep_learning.ipynb

07_validacion.ipynb

08_shap.ipynb

09_monte_carlo.ipynb
```

---

# Resultados esperados

Se espera determinar si los modelos basados en inteligencia artificial permiten obtener una mayor precisión en la predicción del Flujo de Caja Libre frente a los métodos tradicionales.

También se espera identificar las variables que tienen mayor influencia sobre el comportamiento del FCL y desarrollar una herramienta que permita realizar predicciones, análisis de escenarios y estimaciones de riesgo.

---

# Aplicación final

Como producto complementario se podrá desarrollar una aplicación en Streamlit que permita:

Cargar información financiera  
Ejecutar el modelo predictivo  
Visualizar la predicción del FCL  
Comparar escenarios  
Mostrar métricas del modelo  
Mostrar gráficos históricos  
Mostrar explicaciones SHAP  
Ejecutar simulaciones Monte Carlo  
Exportar resultados

---

# Estado del proyecto

Investigación en desarrollo.

Etapas principales:

Preparación de datos

Desarrollo de modelos

Evaluación

Interpretabilidad

Simulación

Desarrollo de aplicación

Documentación de resultados

---

# Autor

Ricardo Villena

Maestría en Inteligencia Artificial  
Universidad Nacional de Ingeniería – UNI  
Lima, Perú  
2026

## Semana 5 — Feature Engineering implementado

El notebook [`notebooks/02_feature_engineering.ipynb`](notebooks/02_feature_engineering.ipynb) prepara la predicción de **FCL_preliminar(t+1)** con información de t y anteriores. Este objetivo cumple `FCO + CAPEX_reportado` con el signo original; **no constituye un FCFF económicamente validado**.

El panel observado contiene 4.221 registros anuales de 336 empresas entre 2005 y 2025. Se generan **22 predictores**: ocho ratios financieros, cuatro variaciones y diez características temporales (rezagos 1–3, medias y desviaciones móviles). Las ventanas se interrumpen ante huecos o cambios de moneda. No se convierten monedas, completan años ni imputan objetivos.

Se conservan 4.221 filas en `data/processed/features_financieras.csv`, con 57 columnas que distinguen fuentes, predictores y controles. Hay **3.560 pares elegibles de 309 empresas** con objetivo anual siguiente observado y moneda consistente: 2.869 de entrenamiento (año objetivo hasta 2021) y 691 de prueba (2022–2025). De esos pares, 2.251 tienen los 22 predictores observados. La exportación conserva faltantes; la imputación mediana y RobustScaler en un Pipeline ilustrativo se ajustan solo con entrenamiento, por moneda, en memoria. No se entrenan modelos.

Para reproducir, con el entorno Conda `tesis-fcl` ya disponible:

```bash
conda activate tesis-fcl
python -m unittest discover -s tests -v
python scripts/execute_feature_engineering.py
```

Se requiere Python 3.12.x; ejecución verificada con 3.12.15. Las versiones verificadas están en [`requirements-feature-engineering.txt`](requirements-feature-engineering.txt); este flujo no instala paquetes. Jupyter necesita comunicación local con el kernel. También puede ejecutarse el notebook completo desde Jupyter seleccionando `tesis-fcl`.

- Cálculo reproducible: [`src/feature_engineering.py`](src/feature_engineering.py).
- Pruebas automatizadas: [`tests/test_feature_engineering.py`](tests/test_feature_engineering.py).
- Diccionario completo: [`reports/diccionario_features.md`](reports/diccionario_features.md).
- Resultados y límites: [`reports/resumen_feature_engineering.md`](reports/resumen_feature_engineering.md).
- Evidencia de ejecución y hashes de archivos protegidos: `reports/validacion_ejecucion.json`.

La selección de predictores es explícita en `PREDICTORS`; las columnas objetivo, moneda futura, elegibilidad, partición y demás controles **no forman X**. Las correlaciones se exploran solo en entrenamiento. El notebook conserva el EDA anterior y los datos originales.

Persisten limitaciones: escala monetaria no acreditada para el panel, etiqueta `D lares` deteriorada, códigos FCO/CAPEX pendientes de validación, ausencia de fechas de publicación y versiones históricas, sectores financieros heterogéneos e historiales de hasta 21 años. El corte por ejercicio es retrospectivo: antes de entrenar se debe auditar la publicación efectiva de las etiquetas en la frontera temporal. El Excel complementario no se integró sin homologación. Los resultados no acreditan capacidad predictiva.

### Correcciones de la auditoría independiente (Antigravity)

Se atendieron HAL-01–HAL-12, con detalle en [`reports/correcciones_antigravity.md`](reports/correcciones_antigravity.md). Se mantienen 22 características exportadas y se define `PREDICTORS_NO_COLINEALES` de 19 variables: excluye `fcl_activo` y las dos medias móviles, redundantes con otros predictores. El rango y VIF se verifican únicamente con entrenamiento; persiste correlación alta entre algunas características y deben evaluarse regularización y explicaciones agrupadas en la siguiente etapa.

CAPEX positivo invalida internamente todas las derivaciones de FCL y su etiqueta futura, preservando las columnas fuente. Rotación y crecimiento de ingresos exigen ingreso actual positivo. La preparación usa `SimpleImputer` y `RobustScaler` dentro de un Pipeline ajustado por moneda; hay que clonarlo y reajustarlo en cada pliegue temporal, sin reutilizar matrices transformadas globalmente.

El notebook cuantifica el sesgo de los casos completos con tablas por año y moneda y Mann-Whitney exploratorio. **No usar `dropna()` sobre predictores para modelado.** También incluye estratificación por revisión interanual y una sensibilidad de escala en memoria: rezagos/ventanas y objetivo divididos por activos positivos de t, con moneda consistente para el objetivo. No se amplía la lista de 22 ni se cambia el objetivo principal. La evaluación predictiva de estas sensibilidades queda para Semana 6; no se entrenan modelos aquí.


### Entrega completa al profesor — Semana 5

La rama de entrega es `feature-engineering`. Se incluyen:

- [Panel original: 4.221 filas](data/processed/panel_fcl_preliminar.csv).
- [Cálculos completos: 4.221 filas, 57 columnas y 22 características](data/processed/features_financieras.csv), sin eliminar NaN ni banderas.
- [Notebook ejecutado](notebooks/02_feature_engineering.ipynb), con fórmulas, tablas, gráficos e interpretaciones.
- [Funciones de cálculo](src/feature_engineering.py), [diccionario](reports/diccionario_features.md) y [trazabilidad individual de las 22 variables y los objetivos](reports/trazabilidad_variables.md).
- [Validación de cálculos](reports/validacion_calculos.json), [resumen académico](reports/resumen_feature_engineering.md), pruebas en `tests/` y evidencia de ejecución en `reports/validacion_ejecucion.json`.
- 22 XML de la SMV en `data/raw/smv/`, con [inventario y SHA-256](reports/trazabilidad_smv.json). Licencia y atribución: [data/README.md](data/README.md).

Las fichas específicas de principales cuentas y flujo de efectivo de la SMV
indican ODbL. Los XML y la base adaptada se entregan con los avisos correspondientes.
El Excel complementario y el informe interno de auditoría permanecen locales.

Para crear el entorno y reproducir desde un clon de esta rama:

```bash
conda env create -f environment-feature-engineering.yml
conda activate tesis-fcl
python -m ipykernel install --user --name tesis-fcl --display-name tesis-fcl
python -m unittest discover -s tests -v
python scripts/reproduce_features.py --check
python scripts/execute_feature_engineering.py
python scripts/reproduce_features.py --check
```

`python scripts/reproduce_features.py` regenera el dataset sin Jupyter.
`--check` exige igualdad byte a byte y preservación de NaN frente al CSV entregado.
Los faltantes se escriben como campos vacíos y se recuperan con `pd.read_csv`;
RPJ y RUC se leen como texto. No se convierten monedas ni se imputa el dataset.

El [procedimiento completo y sus límites](reports/procedimiento_smv.md) distingue
lo implementado de lo pendiente. **Feature Engineering es reproducible desde el
panel incluido. La reconstrucción histórica del panel desde fuentes oficiales
sigue incompleta**: faltan las respuestas de detalle FCO/CAPEX y el código de
selección, revisiones y consolidación. Los XML de resumen no contienen FCO/CAPEX.

Publicación remota y autenticación: [entrega y publicación](reports/entrega_semana5.md).

Revisión previa a publicación: [matriz de trazabilidad, examen del Excel y estado de entrega](reports/revision_entrega_semana5.md). Esta revisión no ejecuta operaciones de publicación.
