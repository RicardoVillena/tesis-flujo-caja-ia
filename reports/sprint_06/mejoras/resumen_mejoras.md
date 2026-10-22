Mejoras del Baseline: evaluacion condicional retrospectiva

Muestra inalterada: 3560 casos elegibles, 2869 entrenamiento y 691 prueba. Soles y dolares se modelan por separado.
Clipping p1/p99 por fold; alpha 0.1–10000 con cuatro ventanas expansivas por años objetivo (dos para BANCOS por cobertura limitada). Seleccion final solo por MSE anual de validacion.

Politica sectorial seleccionada antes de evaluar prueba:

Moneda | n | MAE | RMSE | R2 | R2 OOS media | R2 OOS persistencia
--- | --- | --- | --- | --- | --- | ---
D lares | 92 | 147873.2512 | 323976.8077 | 0.508855 | 0.514117 | 0.118533
Soles | 599 | 696262.3068 | 2118786.2605 | -4.507376 | -4.455796 | -2.092864

Ganadores por cohorte decididos en CV:
D lares/no_bancario: niveles_t_externos_t_1, E1_macroeconomico, alpha=1000; RMSE CV anual=270451.5561.
D lares/todas: niveles_t_externos_t_1, E1_macroeconomico, alpha=1000; RMSE CV anual=270451.5561.
Soles/no_bancario: sin_niveles_t_externos_t_1, E2_bursatil, alpha=1000; RMSE CV anual=338435.7601.
Soles/todas: niveles_t_externos_t, E1_macroeconomico, alpha=10; RMSE CV anual=844654.1191.
Soles/bancario: niveles_t_externos_t_1, E1_macroeconomico, alpha=10; RMSE CV anual=2886677.1556.

Comparacion con E0 del 07:
D lares: MAE reduce 35.2%, RMSE reduce 59.7%.
Soles: MAE aumenta 83.2%, RMSE aumenta 48.7%.

Un R2 OOS negativo significa no superar la referencia ingenua en SSE, aunque se reduzca el error respecto a Ridge 07.
El modelo elegido para BANCOS por CV empeora en prueba; no se reemplaza usando sus metricas. Las mejoras no son universales y debe conservarse esta evidencia negativa.
Pendiente: escala monetaria, publicacion/vintages, validez del FCL bancario y evaluacion independiente futura. La prueba actual ya fue inspeccionada al motivar estas mejoras; no se usa para elegir modelos.
