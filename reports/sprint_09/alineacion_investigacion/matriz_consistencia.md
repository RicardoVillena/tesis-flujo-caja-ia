# Matriz de consistencia — alcance del plan de tesis y componente implementado

**Estado:** propuesta para revisión académica. No sustituye el plan de tesis (`notebooks/Trabajo_de_investigacion_final.pdf`) ni la matriz anterior ([../matriz_consistencia.md](../matriz_consistencia.md)). Las variables se detallan en [matriz_operacionalizacion.md](matriz_operacionalizacion.md).

## A. Alcance original del plan de tesis (resumido fielmente; sin reformular)

**Título del plan:** "Valoración Corporativa Probabilística: Estimación del valor intrínseco de empresas mediante modelos de Machine Learning: una comparación con el método DCF".

**Población:** grandes y medianas empresas **no financieras** que cotizan en bolsa.

La sección 3.3.2 (variables) del plan está **vacía**.

| Problema (plan) | Objetivo (plan) | Hipótesis (plan) | Variables (plan) | Indicadores (plan) | ¿Contrastable con los datos actuales? |
|---|---|---|---|---|---|
| General: ¿cómo un DCF mejorado con LSTM y Monte Carlo optimiza la precisión de la valorización y la evaluación de riesgos de cola? | Desarrollar y validar un modelo de simulación probabilística de valorización (DCF + ML + XAI) | — (las cuatro hipótesis siguientes) | Valor de la empresa; flujos de caja; WACC; ratios contables; macro | RMSE, MAE, R²; rangos e intervalos de valor | **No.** Faltan FCFF validado, tasa de descuento, precios por emisor y LSTM/Monte Carlo evaluados (ver [viabilidad_pendientes.md](viabilidad_pendientes.md)). |
| PE1: mejora en el pronóstico de trayectorias de flujos con LSTM frente a enfoques deterministas | OE1: pronosticar trayectorias de flujos y riesgos de cola con LSTM y Monte Carlo | H1: el modelo híbrido LSTM + Monte Carlo da un rango de valoración más preciso y evalúa mejor los riesgos de cola | Flujos futuros; distribución de valor | Error de pronóstico; métricas de cola | **Parcial.** Solo el pronóstico puntual de un flujo (FCL preliminar t+1) con Ridge y boosting frente a referencias deterministas. LSTM, Monte Carlo y colas: no evaluados. |
| PE2: efecto no lineal de los umbrales de apalancamiento y tenencias de efectivo sobre el valor intrínseco | OE2: cuantificar efectos no lineales del apalancamiento y del efectivo sobre el valor | H2: el apalancamiento y las reservas de efectivo incrementan significativamente la capacidad predictiva del valor | Apalancamiento; efectivo; valor de la firma | Mejora predictiva; umbrales | **Parcial y desplazado.** El apalancamiento (pasivo/activo) está en los datos. **El efectivo no existe.** La variable dependiente disponible es el FCL preliminar, no el valor. No se contrasta "significativamente". |
| PE3: influencia asimétrica de la incertidumbre global sobre los precios, condicionada al tamaño | OE3: efecto moderador de la incertidumbre global (riesgo geopolítico, sentimiento) según el tamaño | H3: la incertidumbre global tiene un impacto no lineal condicionado a la escala de la firma | Índices de incertidumbre (WUI, GPR); tamaño; precio | Patrones de interacción | **No.** No hay índices de incertidumbre global ni precios por emisor. Solo se evalúa si las variables macro y bursátiles agregadas ayudan a predecir el FCL, y el tamaño como atributo. |
| PE4: XAI con supervisión humana para transparencia y gobernanza | OE4: SHAP, dependencias parciales y Human-in-the-Loop | H4: la eficiencia operativa impulsada por IA eleva la valoración, validada con gobernanza explicable | Eficiencia operativa; gobernanza; valoración | — | **No.** Solo hay importancia por retirada con reajuste, no SHAP. No hay datos de eficiencia operativa por IA ni un proceso Human-in-the-Loop evaluado. |

**Incoherencias internas del plan,** que conviene resolver con el asesor:
- La partición se describe como 70/15/15 y como 80/20.
- La winsorización se describe al 1 % y 99 % y al 5 % y 95 %.
- Se propone validación cruzada k-fold junto con división cronológica.
- La sección de variables está vacía.

## B. Componente implementado y contrastable (Sprints 08–09)

| Problema | Objetivo | Hipótesis (contrastables) | Variables | Indicadores |
|---|---|---|---|---|
| General: ¿la información financiera, macroeconómica y bursátil permite predecir el FCL preliminar del ejercicio siguiente con menos error que las referencias simples, en empresas no financieras? | Evaluar con validación temporal anidada por moneda si Ridge o boosting con estos atributos superan a la media histórica y a la persistencia | HG: al menos una combinación algoritmo-atributos reduce el RMSE anual medio en ≥ 1 % frente a ambas referencias, en ≥ 4 de 5 años, con MAE no mayor | **VI:** financieros, tamaño, macroeconómicos y bursátiles de t. **VD:** FCL preliminar(t+1). **Factores:** algoritmo y conjunto de atributos | RMSE y MAE anuales medios; Δ % frente a referencias; años con mejora; concentración del error |
| E1: ¿alinear la población (no financieras) cambia la evidencia sobre las variables externas? | Repetir E0–E3 en la población no financiera (y en la conservadora como sensibilidad) | H1': en la población no financiera, E1, E2 o E3 cumplen la regla frente a E0 o E1, con el mismo algoritmo | Bloques macro y bursátil; población como factor | Δ RMSE % E1/E0, E3/E0, E2/E1, E2/E0 |
| E2: ¿el tamaño aporta a la predicción? (adaptación parcial de PE2 y PE3 del plan) | Añadir ln(activo total) a E0 y E2 | H2': E0T frente a E0 o E2T frente a E2 cumplen la regla | Tamaño = ln(activo total); apalancamiento (ya en E0) | Δ RMSE % E0T/E0 y E2T/E2; importancia del bloque tamaño |
| E3: ¿qué atributos y bloques aportan de forma estable? (adaptación parcial de OE4) | Importancia por retirada (individual y por bloques) en E2T, por moneda, modelo y año | H3': algún bloque aumenta el RMSE en ≥ 4 de 5 años al retirarlo, con un aumento medio ≥ 1 % | Atributos de E2T | Δ RMSE al retirar (positivo = aporta); años con aporte |

**Diferencias que no deben ocultarse:**
- **Variable dependiente:** la implementada es el FCL preliminar, no el valor intrínseco, el precio ni el FCFF.
- **Hipótesis:** las hipótesis "prima" (H1', H2', H3') son adaptaciones contrastables; no equivalen a las H1–H4 del plan.
- **Carácter de los resultados:** exploratorios, porque los años 2017–2021 ya se habían examinado.
