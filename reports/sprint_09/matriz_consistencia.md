# Matriz de consistencia — propuesta para revisión académica (Sprint 09)

**Estado:** propuesta. No sustituye el alcance oficial de la tesis sin aprobación del asesor. Revisa la versión inicial ([antecedente_6eeac16/matriz_consistencia.md](antecedente_6eeac16/matriz_consistencia.md)).

## Relación con el alcance oficial

El alcance oficial está en el [README](../../README.md) del repositorio: "Predicción del Flujo de Caja Libre mediante Inteligencia Artificial".
- **Objetivo general:** desarrollar un modelo basado en IA para predecir el FCL de empresas y evaluar su precisión frente a métodos tradicionales.
- **Seis objetivos específicos:** preparación de datos, variables relevantes, modelos tradicionales, de ML y de deep learning, comparación, IA explicable, y simulación de escenarios.

Esta matriz operacionaliza **solo la parte verificable con el panel actual**, sin reemplazar lo anterior:

| Elemento oficial | Tratamiento en esta matriz |
|---|---|
| Objetivos 2, 4 y 5 (variables relevantes, comparación, influencia de variables) | Cubiertos por las filas 1 a 4 |
| Objetivo 3 (modelos tradicionales y de ML) | Parcial: referencias simples, Ridge y boosting |
| Objetivo 3, parte de deep learning | Fuera de esta matriz; pendiente |
| Objetivo 6 (simulación e incertidumbre) | Fuera de esta matriz; pendiente |
| Objetivo 5 entendido como XAI formal (SHAP u otros) | Fuera de esta matriz: aquí solo hay importancia por retirada |
| FCL de la fórmula oficial: EBIT·(1−t) + D − CAPEX − ΔCT | **No es la variable dependiente usada.** Se usa un FCL preliminar = FCO + CAPEX reportado, que no es un FCFF validado. Adoptarlo en la tesis requiere decisión académica explícita. |

## Matriz

| Problema | Objetivo | Hipótesis | Variables independientes y dependiente | Indicadores |
|---|---|---|---|---|
| **General.** ¿En qué medida la información financiera, macroeconómica y bursátil, procesada con modelos de aprendizaje automático, permite predecir el FCL preliminar del ejercicio siguiente con menor error que las referencias simples? | Evaluar, con validación temporal anidada por moneda, si algún procedimiento predictivo con atributos financieros y externos reduce el error de predicción del FCL preliminar t+1 frente a la media histórica y la persistencia. | **HG:** al menos una combinación de algoritmo y conjunto de atributos reduce el RMSE anual medio en ≥ 1 % frente a la media histórica y frente a la persistencia, con menor RMSE en ≥ 4 de 5 años externos y MAE anual medio no mayor, en cada moneda. | **VI:** atributos financieros (19), macroeconómicos (4) y bursátiles (3) del ejercicio t. **VD:** FCL preliminar(t+1). **Factores experimentales:** algoritmo y conjunto de atributos. | RMSE y MAE anuales medios; Δ RMSE % y Δ MAE % frente a cada referencia; años con mejora; peor empeoramiento anual; métricas concatenadas como contraste. |
| **E1. Aporte macroeconómico.** ¿Añadir variables macroeconómicas mejora la predicción frente a usar solo variables financieras? | Comparar E1 (financieras + macroeconómicas) con E0 (financieras), con el mismo algoritmo, filas, pliegues y presupuesto de ajuste. | **H1:** E1 reduce el RMSE anual medio en ≥ 1 % frente a E0, con menor RMSE en ≥ 4 de 5 años y MAE no mayor, para un mismo algoritmo y moneda. Se contrasta también con externos rezagados (t−1) y comparando E2 con E3. | **VI:** bloque macroeconómico (inflación, tipo de cambio, tasa de referencia, crecimiento del PBI), con el bloque financiero constante. **VD:** FCL preliminar(t+1). **Factor:** presencia del bloque. | Δ RMSE % E1/E0 y E2/E3; Δ MAE %; años con mejora; igual en la sensibilidad t−1; Δ RMSE al retirar el bloque macro de E2. |
| **E2. Aporte bursátil.** ¿Añadir variables bursátiles mejora la predicción frente a las financieras y frente a financieras + macroeconómicas? | Comparar E3 (financieras + bursátiles) con E0, y E2 (todas) con E1. | **H2:** E3 frente a E0 y E2 frente a E1 cumplen el criterio de mejora (≥ 1 % de RMSE, ≥ 4 de 5 años, MAE no mayor), para un mismo algoritmo y moneda. | **VI:** bloque bursátil (rentabilidad del índice, volatilidad diaria anualizada, monto negociado en renta variable). **VD:** FCL preliminar(t+1). **Factor:** presencia del bloque. | Δ RMSE % E3/E0 y E2/E1; Δ MAE %; años con mejora; sensibilidad t−1; Δ RMSE al retirar el bloque bursátil de E2. |
| **E3. Procedimientos predictivos.** ¿Qué procedimiento (algoritmo y conjunto de atributos) presenta menor error, y supera a las referencias simples? | Comparar Ridge y boosting en cada variante, y cada combinación con la media histórica y la persistencia, separando el efecto del algoritmo del efecto de los atributos. | **H3a:** boosting cumple el criterio frente a Ridge con la misma variante. **H3b:** la combinación de menor RMSE cumple el criterio frente a ambas referencias simples. | **VI:** los atributos de cada variante. **VD:** FCL preliminar(t+1). **Factores:** algoritmo (Ridge, boosting) e hiperparámetros elegidos internamente; las referencias simples como comparadores. | Δ RMSE % y Δ MAE % boosting/Ridge por variante; Δ frente a la media y la persistencia; años con mejora; concentración del error por empresa. |
| **E4. Importancia y selección.** ¿Qué atributos y bloques aportan de forma estable a la predicción, y seleccionar atributos dentro del entrenamiento mejora frente a usar todos? | Cuantificar la importancia por retirada (individual y por bloques) y su estabilidad entre años; evaluar E4 (selección interna) frente a E2 y E0. | **H4a:** al menos un atributo o bloque tiene aporte estable: retirarlo aumenta el RMSE en ≥ 4 de 5 años, con aumento medio ≥ 1 %. **H4b:** E4 cumple el criterio de mejora frente a E2 con el mismo algoritmo. | **VI:** presencia o retirada de cada atributo o bloque; subconjunto elegido por E4. **VD:** FCL preliminar(t+1); respuesta del análisis: cambio del error. **Factor:** conjunto de atributos. | Δ RMSE = RMSE sin atributo − RMSE completo (positivo = aporta); Δ %; años con aporte o perjuicio; frecuencia de selección en E4; Δ RMSE % E4/E2. |

## Operacionalización

- **Unidad de análisis:** empresa (RPJ) y ejercicio, con un ejercicio de horizonte. Soles y dólares se evalúan por separado; no se suman errores entre monedas.
- **Variable dependiente:** `objetivo_fcl_t1` = FCO(t+1) + CAPEX_reportado(t+1) de la misma empresa.
  - Se une por ejercicio consecutivo exacto, en la misma moneda.
  - Queda inválida si el CAPEX es positivo y no se imputa.
  - No es un FCFF validado.
- **Variables independientes:** los nombres exactos están en [protocolo.json](protocolo.json). Los externos usan el año calendario t; la sensibilidad usa t−1.
- **Factores experimentales**, que no son variables independientes en sentido causal:
  - algoritmo: Ridge o HistGradientBoosting, con hiperparámetros elegidos en los pliegues internos;
  - conjunto de atributos: E0 a E4.
- **Referencias:** media histórica y persistencia de FCL(t).
- **Indicadores:**
  - RMSE = √(media del error al cuadrado);
  - MAE = media del error absoluto;
  - Δ error % = 100·(candidato/comparador − 1), donde negativo significa mejora;
  - importancia: Δ RMSE al retirar, donde positivo significa que el atributo aporta.

  Los errores anuales se promedian dando igual peso a cada año.
- **Criterio de contraste:**
  - una hipótesis se considera **respaldada** si cumple la regla en las combinaciones indicadas, y **no respaldada** si no la cumple;
  - es una regla exploratoria, no una prueba de significancia estadística;
  - las hipótesis pueden quedar no respaldadas.
- **Diseño:** cuantitativo, predictivo, longitudinal y observacional, con experimentos computacionales sobre variantes. Los resultados describen capacidad predictiva, no causalidad.
- **Limitaciones de validez:**
  - Los años 2017–2021 ya se examinaron; la partición 2022–2025 ya fue consultada en el Sprint 06 y no se usa. Sin confirmación independiente, los resultados son exploratorios.
  - La disponibilidad real de los datos al pronosticar, las revisiones históricas y la escala monetaria no están acreditadas.
