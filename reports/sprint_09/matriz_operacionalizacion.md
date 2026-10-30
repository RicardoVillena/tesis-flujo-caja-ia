# Matriz de operacionalización de variables

Propuesta para revisión académica. Complementa la [matriz de consistencia](matriz_consistencia.md): aquella relaciona problemas, objetivos e hipótesis; esta define cómo se observan y miden las variables.

Unidad de análisis: empresa (RPJ)–ejercicio. Horizonte predictivo: un ejercicio anual. Las monedas se analizan por separado.

| Variable y papel | Definición conceptual | Dimensión | Indicadores observables | Definición operacional | Unidad o escala | Fuente |
|---|---|---|---|---|---|---|
| Información financiera histórica — independiente | Situación financiera y trayectoria de los flujos de la empresa | Endeudamiento, rentabilidad y actividad | Pasivo/activo, margen neto, rentabilidad sobre activo, rotación del activo | Ratios del ejercicio t según las reglas de ingeniería de atributos existentes | Ratios numéricos | Estados financieros SMV; panel procesado |
| Información financiera histórica — independiente | Capacidad de generación de efectivo e inversión | Flujo operativo e inversión | FCO/activo, FCO/ingresos, CAPEX/activo | Cocientes del ejercicio t; CAPEX con su signo reportado; reglas de denominadores y faltantes según implementación | Ratios numéricos | Estados financieros SMV; panel procesado |
| Información financiera histórica — independiente | Evolución y variabilidad financiera | Crecimiento y memoria temporal | Crecimiento de activo e ingresos, cambios de ratios, rezagos 1–3 y desviaciones históricas de FCO y FCL preliminar | Construcción por empresa y ejercicio con antecedentes disponibles; ventanas y fórmulas del código y diccionario vigentes | Variaciones y valores monetarios en moneda reportada; escala monetaria pendiente de acreditación | Panel financiero e ingeniería de atributos |
| Información macroeconómica — independiente | Entorno económico agregado | Actividad económica | Crecimiento del PBI real | Variación porcentual anual oficial; año t en el experimento principal y t−1 en sensibilidad | Porcentaje anual | BCRPData |
| Información macroeconómica — independiente | Condiciones de precios, cambio y política monetaria | Precios y condiciones monetarias | Inflación Lima dic/dic, tipo de cambio promedio y tasa de referencia promedio | Inflación diciembre/diciembre; promedios mensuales anualizados según diccionario BCRP; unión por año | Porcentaje; soles por dólar; porcentaje | BCRPData |
| Información bursátil — independiente | Comportamiento agregado del mercado de valores | Rendimiento, riesgo y negociación | Rentabilidad anual del índice, volatilidad diaria anualizada y monto negociado anual en renta variable | Agregaciones del año t según extracción bursátil; sensibilidad con t−1 | Porcentaje; porcentaje anualizado; millones de soles | Fuentes BVL utilizadas en el repositorio |
| FCL preliminar del siguiente ejercicio — dependiente | Aproximación al efectivo generado por operación después de la inversión reportada | Flujo anual futuro de la empresa | `objetivo_fcl_t1` | FCO(t+1) + CAPEX_reportado(t+1), misma RPJ, ejercicio consecutivo exacto y misma moneda; inválido si CAPEX es positivo; objetivo no imputado | Valor monetario continuo en moneda reportada; escala pendiente de acreditación | Estados financieros SMV y panel procesado |

Los nombres exactos de los 19 atributos financieros, 4 macroeconómicos y 3 bursátiles se encuentran en [protocolo.json](protocolo.json). Las fórmulas de ingeniería deben mantenerse consistentes con el código y los diccionarios existentes; esta tabla no redefine sus cálculos.

## Factores del experimento e indicadores de evaluación

El algoritmo (Ridge o boosting), el conjunto de atributos (E0–E4) y el rezago externo son factores del experimento computacional. No representan causas económicas intervenidas sobre las empresas.

| Indicador | Cálculo o medición | Interpretación |
|---|---|---|
| RMSE | Raíz del promedio del error al cuadrado, por año y moneda; luego promedio simple de años | Menor error predictivo es mejor |
| MAE | Promedio del valor absoluto del error, por año y moneda; luego promedio simple de años | Menor error predictivo es mejor |
| Cambio porcentual de error | 100 × (error candidato / error comparador − 1) | Negativo indica reducción del error |
| Estabilidad temporal | Número de años externos con RMSE menor al comparador | Evita identificar una mejora promedio con una mejora estable |
| Importancia predictiva por retirada | RMSE sin atributo o bloque − RMSE completo, con reajuste según protocolo | Positivo indica que retirarlo perjudica la predicción; no demuestra causalidad |

RMSE y MAE evalúan la predicción; no sustituyen al FCL como variable dependiente. La regla de mejora (≥1% menos RMSE anual medio, mejora en ≥4/5 años y MAE no mayor) es un criterio exploratorio y no una prueba de significancia.

## Límites de medición

El objetivo actual es FCL preliminar y no FCFF validado. La disponibilidad efectiva en la fecha de pronóstico, las revisiones históricas y la escala monetaria no están acreditadas. Un rezago externo no prueba por sí solo disponibilidad real. Los resultados de 2017–2021 son exploratorios por reutilización de esos años.
