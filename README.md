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

## Metodología de ingesta de datos

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

### Arquitectura de ingesta

La información será organizada utilizando una arquitectura de tres niveles:

```text
BRONZE
Datos originales obtenidos desde la fuente sin modificaciones.

SILVER
Datos limpiados, homologados, transformados y validados.

GOLD
Dataset final preparado para análisis estadístico y modelos de inteligencia artificial.

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
