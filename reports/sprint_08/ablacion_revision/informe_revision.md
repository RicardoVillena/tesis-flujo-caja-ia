# Sprint 08 — Revisión de la evaluación de variables (exploratoria) y cierre de la etapa

**Carácter:** EXPLORATORIA: los años externos 2017–2021 ya se examinaron en la ejecución anterior; no es confirmación independiente ni prueba final. Solo entrenamiento (años objetivo ≤ 2021), por moneda; prueba 2022–2025 no interviene. Resultados anteriores preservados en `reports/sprint_08/ablacion/`.

## Cambios de esta revisión

- seleccionar(): la versión anterior se detenía si la retirada de menor RMSE no era admisible, aunque otra sí lo fuera (corregido).
- rejilla de alpha ampliada una sola vez a [0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0, 100000.0, 1000000.0], idéntica para completo y reducido; alpha se elige solo en pliegues internos.
- referencias simples en las mismas filas y años externos.
- Umbrales, años externos e internos, máximo de 5 retiradas y reglas de decisión: sin cambios.

## Decisión final por moneda

- **D lares: Conservar los 26 atributos.** Reducido frente a completo: RMSE anual medio -2.73 %, mejora en 1 y empeora en 3 de 5 años (regla: Conservar modelo completo). Frente a referencias simples, el modelo completo NO aporta una mejora consistente (media histórica: mejora consistente, RMSE -14.14 %; persistencia: sin mejora, RMSE +29.06 %). Lista final propuesta por el procedimiento: crecimiento_pbi_real_pct (pendiente de evaluación posterior).
- **Soles: Conservar los 26 atributos.** Reducido frente a completo: RMSE anual medio +0.00 %, mejora en 0 y empeora en 0 de 5 años (regla: Conservar modelo completo). Frente a referencias simples, el modelo completo aporta una mejora consistente (media histórica: mejora consistente, RMSE -1.45 %; persistencia: mejora consistente, RMSE -29.81 %). Lista final propuesta por el procedimiento: sin retiradas (pendiente de evaluación posterior).

## Regularización

- D lares: alpha completo por año externo 10000, 1000, 1000, 1000, 1000; reducido 1000, 1000, 1000, 1000, 1000; final 1000/1000. Selecciones en el máximo (1e6): 0 de 10 externas y 0 de 2 finales.
- Soles: alpha completo por año externo 1e+06, 1e+06, 1e+06, 10000, 10000; reducido 1e+06, 1e+06, 1e+06, 10000, 10000; final 1000/1000. Selecciones en el máximo (1e6): 6 de 10 externas y 0 de 2 finales.
- **Limitación:** la selección vuelve a alcanzar el máximo de la rejilla ampliada en al menos una moneda; la regularización óptima puede ser mayor. Conforme al protocolo, no se amplía de nuevo y la etapa se cierra con esta limitación documentada.

## Métricas externas por moneda (promedio de años; RMSE y MAE en unidad monetaria reportada)

| moneda | procedimiento | RMSE anual medio | MAE anual medio | RMSE concatenado | MAE concatenado |
|---|---|---|---|---|---|
| D lares | media_historica | 288,696 | 151,261 | 309,286 | 149,730 |
| D lares | persistencia | 192,066 | 89,316 | 202,295 | 88,174 |
| D lares | completo_alpha_interno | 247,885 | 128,570 | 272,219 | 126,001 |
| D lares | reducido | 241,112 | 126,784 | 265,366 | 124,455 |
| D lares | E2_alpha_1 | 408,560 | 204,176 | 430,203 | 203,940 |
| Soles | media_historica | 933,387 | 263,398 | 1,051,246 | 260,377 |
| Soles | persistencia | 1,310,531 | 276,048 | 1,440,228 | 272,859 |
| Soles | completo_alpha_interno | 919,862 | 258,677 | 1,029,430 | 255,780 |
| Soles | reducido | 919,862 | 258,677 | 1,029,430 | 255,780 |
| Soles | E2_alpha_1 | 1,641,968 | 319,507 | 2,039,244 | 318,514 |

Las concatenadas ponderan años por número de filas; el criterio es el promedio anual. Detalle por año: `metricas_por_anio.csv`.

## Modelo frente a referencias simples

| moneda | modelo | referencia | ΔRMSE anual medio % | ΔMAE anual medio % | años mejor (RMSE) | años mejor (MAE) | peor año ΔRMSE % | veredicto |
|---|---|---|---|---|---|---|---|---|
| D lares | completo_alpha_interno | media_historica | -14.14 | -15.00 | 5 | 5 | -0.79 | mejora consistente |
| D lares | completo_alpha_interno | persistencia | +29.06 | +43.95 | 1 | 1 | +128.98 | sin mejora |
| D lares | reducido | media_historica | -16.48 | -16.18 | 5 | 5 | -11.51 | mejora consistente |
| D lares | reducido | persistencia | +25.54 | +41.95 | 1 | 1 | +128.98 | sin mejora |
| Soles | completo_alpha_interno | media_historica | -1.45 | -1.79 | 5 | 4 | -0.02 | mejora consistente |
| Soles | completo_alpha_interno | persistencia | -29.81 | -6.29 | 4 | 4 | +22.10 | mejora consistente |
| Soles | reducido | media_historica | -1.45 | -1.79 | 5 | 4 | -0.02 | mejora consistente |
| Soles | reducido | persistencia | -29.81 | -6.29 | 4 | 4 | +22.10 | mejora consistente |

Filas de persistencia con respaldo en la media histórica (FCL(t) no válido o ausente): D lares 0 de 119; Soles 6 de 829. No se elimina ninguna fila.

## Selección por pliegue y comparación con la ejecución anterior

| moneda | año externo | retirados (anterior) | retirados (revisión) | alpha completo ant./rev. | alpha reducido ant./rev. | motivo de parada (revisión) |
|---|---|---|---|---|---|---|
| D lares | 2017 | FCO_lag1, FCL_preliminar_lag1 | FCO_lag1, FCL_preliminar_lag1 | 10000/10000 | 1000/1000 | paso 3: ninguna de 24 retiradas es admisible; la de menor RMSE (FCO_lag2) mejora 0.55 % en 2 años internos |
| D lares | 2018 | — | FCL_preliminar_lag2 | 1000/1000 | 1000/1000 | paso 2: ninguna de 25 retiradas es admisible; la de menor RMSE (FCL_preliminar_lag1) mejora 9.88 % en 1 años internos |
| D lares | 2019 | FCL_preliminar_lag1, FCL_preliminar_lag2 | FCL_preliminar_lag1, FCL_preliminar_lag2 | 1000/1000 | 1000/1000 | paso 3: ninguna de 24 retiradas es admisible; la de menor RMSE (FCO_lag1) mejora 1.32 % en 1 años internos |
| D lares | 2020 | — | — | 1000/1000 | 1000/1000 | paso 1: ninguna de 26 retiradas es admisible; la de menor RMSE (FCL_preliminar_lag1) mejora 2.92 % en 1 años internos |
| D lares | 2021 | crecimiento_TotalIngreso | crecimiento_TotalIngreso | 1000/1000 | 1000/1000 | paso 2: ninguna de 25 retiradas es admisible; la de menor RMSE (fco_activo) mejora 0.67 % en 1 años internos |
| Soles | 2017 | — | — | 10000/1e+06 | 10000/1e+06 | paso 1: ninguna de 26 retiradas es admisible; la de menor RMSE (FCO_std3_previa) mejora 0.00 % en 2 años internos |
| Soles | 2018 | — | — | 10000/1e+06 | 10000/1e+06 | paso 1: ninguna de 26 retiradas es admisible; la de menor RMSE (fco_activo) mejora 0.03 % en 2 años internos |
| Soles | 2019 | fco_activo, FCO_std3_previa, FCL_preliminar_std3_previa | — | 10000/1e+06 | 10000/1e+06 | paso 1: ninguna de 26 retiradas es admisible; la de menor RMSE (FCO_std3_previa) mejora 0.02 % en 3 años internos |
| Soles | 2020 | — | — | 10000/10000 | 10000/10000 | paso 1: ninguna de 26 retiradas es admisible; la de menor RMSE (FCO_std3_previa) mejora 0.37 % en 2 años internos |
| Soles | 2021 | — | — | 10000/10000 | 10000/10000 | paso 1: ninguna de 26 retiradas es admisible; la de menor RMSE (fco_activo) mejora 0.50 % en 1 años internos |
| D lares | final_2021 | crecimiento_pbi_real_pct | crecimiento_pbi_real_pct | 1000/1000 | 1000/1000 | — |
| Soles | final_2021 | — | — | 1000/1000 | 1000/1000 | — |

Cambio del RMSE anual medio externo respecto a la ejecución anterior: D lares E2_alpha_1 +0.00 %; Soles E2_alpha_1 +0.00 %; D lares completo_alpha_interno +0.00 %; Soles completo_alpha_interno +0.12 %; D lares reducido +0.01 %; Soles reducido -0.59 %.

## Limitaciones

- Revisión exploratoria sobre años externos ya examinados: cualquier mejora observada aquí no es una estimación independiente.
- Cinco años externos por moneda; dólares con 21–26 filas por año y errores dominados por pocas empresas (ver ejecución anterior).
- Sin fechas de publicación ni vintages: la separación por ejercicio no acredita disponibilidad real de la información.
- La persistencia usa FCL(t), que exige conocer los estados de t al pronosticar, con la misma condición de disponibilidad que los atributos.
- Cambios del usuario en archivos rastreados presentes y no modificados: notebooks/03_extraccion_macroeconomica.ipynb, reports/auditoria_extraccion_macroeconomica.md.

## Archivos

`configuracion.json`, `pliegues_externos.csv`, `pliegues_internos.csv`, `historial_seleccion.csv`, `historial_lista_final.csv`, `predicciones_externas.csv`, `metricas_por_anio.csv`, `comparaciones_pareadas.csv`, `resumen.csv`, `frente_a_referencias.csv`, `respaldo_persistencia.csv`, `comparacion_seleccion_anterior.csv`, `comparacion_metricas_anterior.csv`, `decision_final.csv`, `lista_final_propuesta.csv`, `integridad.json`. Reproducción: `python scripts/reproduce_ablacion_variables.py --revision`.
