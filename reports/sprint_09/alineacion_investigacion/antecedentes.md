# Verificación de antecedentes citados en el plan de tesis

Consultas del 30 de octubre de 2026. Se distinguen tres niveles de evidencia:
- **Verificado en el original:** texto leído en la publicación.
- **Solo metadatos o resumen:** el texto completo no estaba accesible.
- **Solo en la reseña del PDF:** aparece en el plan de tesis y no pudo contrastarse.

Los PDF se descargaron con WebFetch y se leyeron con un extractor de texto local; no se conservan en el repositorio.

## Ali (2026) — apalancamiento y reservas de efectivo

Fuente: Ali, G. M. (2026). *Firm valuation using accounting-based capital structure and cash holdings: An explainable machine learning approach.* International Journal of Data and Network Science, 10, 577–596. [doi:10.5267/j.ijdns.2026.2.001](https://doi.org/10.5267/j.ijdns.2026.2.001). Acceso: texto completo (PDF del editor).

| Aspecto | Verificado en el original |
|---|---|
| Objetivo predicho | **Q de Tobin** = (pasivos totales + capitalización bursátil) / activo total. Es valor de mercado, no un flujo de caja. |
| Población | Empresas **no financieras** de la Bolsa de Egipto. Excluye las financieras "debido a sus estructuras financieras únicas" y a las empresas con estados en moneda extranjera. |
| Muestra y frecuencia | Anual. 104 empresas y 728 observaciones empresa-año; 699 tras el preprocesamiento. El periodo figura como 2016–2022 en la sección de datos y como 2015–2022 en el resumen. |
| Variables pertinentes | LEV = pasivos totales / activo total. CASH = efectivo y equivalentes / activo total. FSIZE = ln(activo total). CAPEX/activo, rentabilidad, dividendos, indicador COVID y otras (13 en total). |
| Modelo y validación | Super Learner (Extra Trees + XGBoost, meta-aprendiz lineal), SHAP y dependencias parciales. Partición 80 % entrenamiento / 20 % validación, sin que en el texto revisado conste que sea cronológica, y k-fold para construir el apilamiento. Imputación por mediana y winsorización al 5 % y 95 %. |
| Resultados | R² = 0,572 del Super Learner, frente a 0,08–0,47 de los demás modelos. Umbrales no lineales: LEV > 1,2 y efectivo > 40 % del activo. |
| Relevancia aquí | Respalda excluir el sector financiero y las definiciones de LEV, CASH y tamaño. El objetivo (Q de Tobin) no es equivalente al FCL preliminar. |
| Discrepancia con el plan | El plan atribuye a Ali una división cronológica de los datos; en el texto revisado solo consta "80 % / 20 %". El plan menciona winsorización al 1 % y 99 % y, en otro lugar, al 5 % y 95 %; Ali usa 5 % y 95 %. |

## Lu y Zhao (2025) — pronóstico de flujos y DCF

Fuente: Lu, T., y Zhao, Y.-H. (2025). *The Machine Learning-Enhanced DCF Model and Probabilistic Cash Flow Forecasting.* Proc. MSCE 2025, ACM. [doi:10.1145/3760023.3760045](https://doi.org/10.1145/3760023.3760045).

**Acceso:** solo metadatos y resumen, a través de Semantic Scholar. La página y el PDF de ACM devolvieron HTTP 403, aunque los metadatos lo declaran de acceso abierto (CC BY).

| Aspecto | Estado |
|---|---|
| Objetivo | Según el resumen: flujos de caja futuros pronosticados con LSTM a partir de datos financieros históricos, integrados en un DCF; Monte Carlo para distribuciones de valoración. La definición exacta del flujo (FCF, FCFF, etc.) **no está verificada**. |
| Población | Según el resumen: las 500 mayores empresas cotizadas de EE. UU. El periodo 2010–2024 aparece **solo en la reseña del PDF**. |
| Métodos | Según el resumen: LSTM, Monte Carlo y un componente de difusión con saltos para eventos extremos. La arquitectura (capas de 128 y 64 neuronas, Adam, Dropout, L2), los modelos de comparación (ARIMA, regresión lineal) y la **reducción del 30 % del error** aparecen **solo en la reseña del PDF**. |
| Validación | **No verificada.** |
| Relevancia aquí | Antecedente conceptual de la línea DCF probabilística. No permite comparar magnitudes de error con este trabajo sin acceso al texto completo. |

## Pham (2026) — tamaño e interacciones con la incertidumbre global

Fuente: Pham, T. T. (2026). *Global Information Uncertainty and Real Estate Stock Valuation in Emerging Markets: An Integrated Behavioral-Theoretical and Machine Learning Framework.* Real Estate Management and Valuation, 34(1), 63–83. [doi:10.2478/remav-2026-0006](https://doi.org/10.2478/remav-2026-0006). Acceso: texto completo (CC BY 4.0).

| Aspecto | Verificado en el original |
|---|---|
| Objetivo predicho | **ln(precio de la acción)**, ajustado por dividendos y divisiones. Es valor de mercado, no un flujo de caja. |
| Población y frecuencia | **Panel mensual** de 28 inmobiliarias cotizadas en Vietnam (HOSE y HNX), 2013–2024. |
| Variables pertinentes | SIZE = ln(activo total); EPS, ROE y valor contable; controles macro (IPC, petróleo, oro, tasa de la Fed); índices de incertidumbre global ESGUI, GPR, WUI y WSI. |
| Modelo y validación | Ridge, Lasso, Elastic Net, árboles, Random Forest, XGBoost optimizado con PSO, SHAP y LIME. El método menciona una partición temporal y validación cruzada de series de tiempo, pero el R² = 0,962 de XGBoost se reporta con **una partición aleatoria 80/20** ("randomly partitioned"), con robustez entre semillas aleatorias. |
| Resultados | El tamaño y el valor contable son los impulsores más influyentes; la interacción WUI × tamaño tiene forma de U invertida. |
| Relevancia aquí | Respalda considerar el tamaño (misma definición). La interacción documentada es con índices de incertidumbre global que **no existen en el panel**, y el objetivo es el precio. |
| Advertencia | Con un panel mensual, una partición aleatoria puede mezclar meses de la misma empresa entre entrenamiento y prueba: el R² reportado no es comparable con una validación temporal. |

## Consecuencias para este trabajo

- **Ali y Pham no predicen flujos de caja:** predicen valor de mercado (Q de Tobin y precio).
- **Lu y Zhao sí pronostican flujos de caja** con LSTM para integrarlos en un DCF, según su resumen. Como el texto completo no estaba accesible, **no se pudo verificar si su flujo equivale al FCL, al FCFF o a otra definición**, ni cómo lo validan. No debe afirmarse que ningún antecedente predice FCL. *(Corrección del 30 de octubre de 2026: la versión anterior de este punto afirmaba que ninguno de los tres predecía FCL.)*
- **Población:** excluir el sector financiero está respaldado por el plan y por Ali.
- **Tamaño** (ln activo total, definición de Ali y Pham): se puede construir con los datos disponibles.
- **Apalancamiento** (pasivo/activo, el LEV de Ali): ya está en E0.
- **Reservas de efectivo:** no se pueden construir porque no hay efectivo y equivalentes en los datos.
- **Interacción tamaño × incertidumbre (Pham):** no es reproducible sin índices de incertidumbre global.
