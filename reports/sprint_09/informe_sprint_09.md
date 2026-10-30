# Sprint 09 — Aporte de variables externas, selección e importancia de variables

**Carácter:** exploratorio.
- Los años externos 2017–2021 ya se examinaron en el Sprint 08, y los resultados de E0 a E2 ya se habían visto en la versión inicial del Sprint 09 (commit `6eeac16`).
- El protocolo de este informe se versionó antes de ejecutar E3, E4, la sensibilidad t−1 y la importancia por bloques (commit `cdf93a1`). No se cambiaron rejillas ni criterios.
- La prueba 2022–2025 no se usó.
- El objetivo es el FCL preliminar t+1 (FCO + CAPEX reportado), no un FCFF validado. Soles y dólares se evalúan por separado.

Protocolo: [protocolo.json](protocolo.json). Matriz de consistencia: [matriz_consistencia.md](matriz_consistencia.md). Verificación: [verificacion.md](verificacion.md).

## Diseño

- **Variantes:**

  | Variante | Atributos | Número |
  |---|---|---|
  | E0 | Financieros | 19 |
  | E1 | E0 + macroeconómicos | 23 |
  | E2 | E1 + bursátiles | 26 |
  | E3 | E0 + bursátiles | 22 |
  | E4 | Selección dentro de cada entrenamiento externo | variable |

  En E4 la selección es por eliminación hacia atrás con los hiperparámetros de E2 congelados, aceptando una retirada si mejora al menos un 1 % en al menos 2 de 3 años internos, con un máximo de 5. Después se reajustan los hiperparámetros.
- **Modelos:** Ridge y HistGradientBoosting, con las mismas rejillas del Sprint 08 (8 configuraciones cada uno) y los mismos pliegues para todas las variantes.
- **Referencias:** media histórica y persistencia de FCL(t).
- **Validación anidada:** años externos 2017–2021; validación interna con los 3 años previos y al menos 8 años de historia. Todas las variantes usan las mismas filas: 119 en dólares y 829 en soles.
- **Disponibilidad temporal:**
  - **Supuesto principal:** los atributos de t están disponibles al pronosticar t+1. Esto **no está acreditado**: el Sprint 08 no verificó la disponibilidad de ningún atributo y marcó 12 con posible fuga temporal.
  - **Sensibilidad declarada de antemano:** los 7 externos se reemplazan por su valor de t−1 (variantes `E1_rezago`, `E2_rezago` y `E3_rezago`). El rezago no acredita publicación ni elimina las revisiones de las series.
- **Regla de mejora:** al menos 1 % menos de RMSE anual medio, menor RMSE en al menos 4 de 5 años y MAE anual medio no mayor. Es exploratoria; no es una prueba de significancia.
- **Signo de los cambios:** en las comparaciones entre variantes, un Δ negativo significa que el candidato tiene menos error. En la importancia, Δ RMSE = RMSE sin el atributo − RMSE completo, de modo que un valor positivo significa que el atributo aporta.

## RMSE anual medio por procedimiento (unidad monetaria reportada)

| Procedimiento | Dólares | Soles |
|---|---|---|
| Media histórica | 288.696 | 933.387 |
| Persistencia | **192.066** | 1.310.531 |
| Ridge E0 / E1 / E2 / E3 / E4 | 246.748 / 248.768 / 247.885 / 246.335 / 267.496 | 924.856 / 919.902 / 919.862 / 924.840 / 919.862 |
| Boosting E0 / E1 / E2 / E3 / E4 | 230.788 / 232.885 / 234.081 / 234.770 / 231.302 | 915.430 / 924.584 / 911.069 / **905.410** / 914.410 |
| Ridge E1 / E2 / E3 con rezago t−1 | 247.330 / 247.659 / 247.185 | 919.546 / 925.493 / 919.579 |
| Boosting E1 / E2 / E3 con rezago t−1 | 234.295 / 234.295 / 231.230 | 922.840 / 933.109 / 930.967 |

Detalle por año: [metricas_por_anio.csv](metricas_por_anio.csv). Las 94 comparaciones están en [resumen_comparaciones.csv](resumen_comparaciones.csv), y su detalle anual en [comparaciones_por_anio.csv](comparaciones_por_anio.csv). Gráficos: [dólares](graficos/variantes_dolares.png) y [soles](graficos/variantes_soles.png).

## Respuestas

### 1. ¿Agregar macroeconomía mejora frente a E0?

**No.** Ninguna de las 4 comparaciones cumple la regla, ni tampoco ninguna de las 4 de la sensibilidad t−1.

| Moneda, modelo | E1 frente a E0: Δ RMSE / Δ MAE / años con mejora | Con rezago t−1 |
|---|---|---|
| Dólares, Ridge | +0,82 % / +0,99 % / 3 | +0,24 % / +1,50 % / 3 |
| Dólares, boosting | +0,91 % / +3,29 % / 1 | +1,52 % / +1,24 % / 1 |
| Soles, Ridge | −0,54 % / **+2,75 %** / 3 | −0,57 % / +1,54 % / 3 |
| Soles, boosting | +1,00 % / +2,93 % / 0 | +0,81 % / +2,33 % / 1 |

Comparar E2 con E3 (añadir macro sobre financieros + bursátiles) tampoco cumple la regla en ninguna combinación. Retirar el bloque macroeconómico de E2 cambia el RMSE entre −0,48 % y −0,03 % en media, sin aporte estable.

### 2. ¿Agregar información bursátil mejora frente a E0 y E1?

**No.** No hay ninguna comparación que cumpla la regla.

- **E3 frente a E0:**
  - dólares: Ridge −0,17 % (3 años), boosting +1,73 % (1 año);
  - soles: Ridge −0,00 % (3 años), boosting −1,09 % (2 años; MAE −0,59 %).
- **E2 frente a E1:**
  - dólares: Ridge −0,36 % (2 años), boosting +0,51 % (4 años);
  - soles: Ridge −0,00 % (2 años), boosting −1,46 % (solo 2 años; MAE −3,06 %).
- **Sensibilidad t−1:** tampoco cumple en ninguna comparación. En dólares, boosting con E2_rezago produce predicciones idénticas a E1_rezago en las 119 filas: los bursátiles rezagados no cambiaron ninguna predicción.
- **Bloque bursátil:** retirarlo de E2 no tiene un aporte estable en ningún modelo ni moneda.

### 3. ¿La selección de atributos (E4) mejora frente a usar todos?

**No.** E4 se compara con E2 usando el mismo algoritmo, así que mide el efecto de seleccionar:

| Moneda, modelo | E4 frente a E2: Δ RMSE / Δ MAE / años con mejora | Qué seleccionó |
|---|---|---|
| Dólares, Ridge | **+7,91 %** / +8,71 % / 0 | Retiró sobre todo rezagos de FCO y FCL; después bajó alpha a 100 en 2018 y 2019. La selección interna sobreajustó. |
| Dólares, boosting | −1,19 % / +2,80 % / 3 | No cumple: mejora solo en 3 años y empeora el MAE. |
| Soles, Ridge | 0,00 % | No retiró ningún atributo en ningún año. |
| Soles, boosting | +0,37 % / 0 años | Solo retiró atributos en 2019. |

Los atributos seleccionados en cada pliegue están en [seleccion_e4.csv](seleccion_e4.csv), y el historial paso a paso en [seleccion_e4_historial.csv](seleccion_e4_historial.csv).

Para separar el efecto del algoritmo, boosting frente a Ridge con la misma variante cumple la regla solo en soles E0 (−1,02 %), soles E3 (−2,10 %) y dólares E4 (−13,53 %, porque Ridge E4 empeora). En las otras 7 de las 10 comparaciones no la cumple.

### 4. ¿Qué variables aportan de forma estable?

Se considera **aporte estable** que retirar el atributo aumente el RMSE en al menos 4 de 5 años, con un aumento medio de al menos 1 %, sobre E2 con la configuración congelada. Detalle en [importancia_individual.csv](importancia_individual.csv) y [importancia_bloques.csv](importancia_bloques.csv).

- **Bloques:**
  - El **bloque financiero** aporta de forma estable en dólares (Ridge +25,03 %, boosting +26,47 %, los 5 años) y en soles con boosting (+1,31 % y 4 de 5 años; en MAE +15,69 %).
  - En soles con Ridge su aporte medio es +0,83 %, inferior al umbral. Con alpha entre 10.000 y 1.000.000 el modelo queda muy regularizado.
  - Los bloques **macroeconómico** y **bursátil** no aportan de forma estable en ninguna moneda ni modelo.
- **Atributos individuales con aporte estable:**
  - Dólares, Ridge: `FCL_preliminar_std3_previa` (+4,48 %, 5/5), `FCO_std3_previa` (+3,33 %, 5/5), `FCO_lag3` (+1,81 %, 5/5) y `FCO_lag1` (+1,44 %, 4/5).
  - Dólares, boosting: `FCO_lag3` (+1,39 %, 4/5), `fco_ingresos` (+1,33 %, 4/5) y `crecimiento_ActivoTotal` (+1,05 %, 4/5).
  - Soles, boosting: `crecimiento_ActivoTotal` (+1,01 %, 4/5).
- **Perjuicio estable:** `margen_neto` en dólares con boosting. Retirarlo reduce el RMSE los 5 años, con una media de −1,19 %.
- **Ningún atributo macroeconómico ni bursátil** tiene aporte estable.

Gráficos: [individual en dólares](graficos/importancia_individual_dolares.png), [individual en soles](graficos/importancia_individual_soles.png), [bloques en dólares](graficos/importancia_bloques_dolares.png) y [bloques en soles](graficos/importancia_bloques_soles.png).

**Cómo interpretar la importancia:**
- Es una importancia predictiva condicional al modelo y a los demás atributos; **no implica causalidad**.
- La redundancia entre atributos (por ejemplo, los rezagos de FCO y FCL) puede repartir u ocultar aportes: un atributo con importancia individual pequeña puede pertenecer a un bloque informativo.
- Los externos no se permutaron entre empresas del mismo año, porque son constantes dentro del año; se retiraron y se reajustó el modelo.

### 5. ¿La mejor alternativa supera las referencias simples?

- **Dólares: no.** La persistencia tiene el menor RMSE (192.066). El mejor modelo, boosting E0 (230.788), es un **20,16 % peor** que la persistencia y solo la supera en 1 de 5 años. Ningún modelo ni variante supera a la persistencia. Todos los modelos superan a la media histórica de forma consistente.
- **Soles: sí, con márgenes pequeños frente a la media histórica.** El menor RMSE es de boosting E3 (905.410), que cumple la regla:
  - frente a la media histórica: −3,00 % de RMSE, 4 de 5 años, MAE −11,75 %;
  - frente a la persistencia: −30,91 %.

  También cumplen frente a ambas referencias boosting E2 y E4, y Ridge E1, E2 y E4 (Ridge con solo −1,44 % a −1,45 % frente a la media). Ridge E0 y E3 no cumplen frente a la media.
  - Como dato descriptivo (no es una comparación prevista y no constituye una decisión), boosting E3 tiene un 1,57 % menos de RMSE que Ridge E2, el modelo vigente del Sprint 08.
- **Concentración del error:** según el procedimiento, entre el 80 % y el 90 % del error cuadrático externo se concentra en 3 empresas. La empresa dominante es CM0006 o B20027 en dólares y B80004 en soles ([concentracion_error.csv](concentracion_error.csv)). Las conclusiones dependen de pocas empresas.

### 6. Estado de las hipótesis

| Hipótesis | Estado | Evidencia |
|---|---|---|
| HG: algún procedimiento supera a ambas referencias | **Respaldada en soles**; **no respaldada en dólares** | En soles cumplen boosting E2, E3 y E4 y Ridge E1, E2 y E4. En dólares nada supera a la persistencia. |
| H1: el bloque macroeconómico mejora | **No respaldada** | 0 de 8 comparaciones, sensibilidad t−1 incluida; E2 frente a E3, 0 de 4. |
| H2: el bloque bursátil mejora | **No respaldada** | E3 frente a E0 y E2 frente a E1: 0 de 8; con t−1, 0 de 8. |
| H3a: boosting supera a Ridge | **No respaldada en general** | 3 de 10 comparaciones por variante, sin un patrón por moneda. |
| H3b: la mejor combinación supera a ambas referencias | Respaldada en soles; no respaldada en dólares | Ver la respuesta 5. |
| H4a: existe algún aporte estable | **Respaldada para variables financieras** | Bloque financiero y 8 combinaciones atributo-modelo-moneda; ninguna variable externa. |
| H4b: E4 mejora frente a E2 | **No respaldada** | 0 de 4; en dólares con Ridge empeora un 7,91 %. |

**Pendientes** (no se resolvieron en este sprint):
- confirmación en datos no examinados;
- disponibilidad real de los atributos al pronosticar y versiones históricas de las series;
- escala monetaria;
- validación del FCL preliminar como FCFF;
- concentración del error en pocas empresas.

## Conclusión

Con este protocolo y estos años, **no hay evidencia de que las variables macroeconómicas o bursátiles mejoren la predicción** del FCL preliminar frente a usar solo variables financieras. Tampoco hay evidencia de que seleccionar atributos dentro del entrenamiento mejore frente a usar todos. El aporte predictivo estable proviene de variables financieras, en particular de los rezagos y la volatilidad histórica de FCO y FCL.

En dólares, ningún modelo supera a la persistencia simple. En soles, los modelos superan a ambas referencias, pero la mejora frente a la media histórica es pequeña y depende de pocas empresas.

Este resultado negativo para la hipótesis de las variables externas se entrega como resultado de investigación. No se excluyeron empresas, ni se cambiaron objetivos, rejillas o criterios para obtener una mejora.
