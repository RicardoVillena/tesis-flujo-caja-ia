# Sprint 09 — Resultados exploratorios

Comparación en años objetivo 2017–2021, con ajuste interno temporal. Prueba 2022–2025 excluida. Menor error es mejor.

| Moneda | Modelo | Comparación | ΔRMSE % | ΔMAE % | Años mejora | Cumple criterio |
|---|---|---|---:|---:|---:|---|
| D lares | boosting | E1 vs E0 | 0.91 | 3.29 | 1/5 | No |
| D lares | boosting | E2 vs E0 | 1.43 | 2.42 | 1/5 | No |
| D lares | boosting | E2 vs E1 | 0.51 | -0.84 | 4/5 | No |
| D lares | ridge | E1 vs E0 | 0.82 | 0.99 | 3/5 | No |
| D lares | ridge | E2 vs E0 | 0.46 | -0.53 | 2/5 | No |
| D lares | ridge | E2 vs E1 | -0.36 | -1.51 | 2/5 | No |
| Soles | boosting | E1 vs E0 | 1.00 | 2.93 | 0/5 | No |
| Soles | boosting | E2 vs E0 | -0.48 | -0.22 | 2/5 | No |
| Soles | boosting | E2 vs E1 | -1.46 | -3.06 | 2/5 | No |
| Soles | ridge | E1 vs E0 | -0.54 | 2.75 | 3/5 | No |
| Soles | ridge | E2 vs E0 | -0.54 | 2.58 | 3/5 | No |
| Soles | ridge | E2 vs E1 | -0.00 | -0.16 | 2/5 | No |

La comparación E1–E0 mide aporte macro; E2–E1, aporte bursátil; E2–E0, aporte externo conjunto. Las variantes ajustan sus hiperparámetros con el mismo presupuesto interno.

La importancia individual se calcula retirando cada atributo y reajustando con los hiperparámetros E2 de ese pliegue. Un delta positivo indica que retirarlo aumenta el error. Es importancia predictiva condicional; correlación entre atributos puede repartir u ocultar importancia. Las variables externas son constantes entre empresas de un año: por eso no se permutan filas dentro del año.

Cinco años reutilizados, concentración del error en pocas empresas, disponibilidad temporal y escala monetaria pendientes. No confirma desempeño futuro ni causalidad. La clasificación de mejora sigue el criterio exploratorio del Sprint 08; no es significancia estadística. No se ajustaron rejillas después de observar estos resultados.

## Respuesta a la observación del profesor

Con estos datos y este protocolo, no se acredita una mejora consistente por añadir variables externas. E2 frente a E0 reduce el RMSE en soles un 0,54% con Ridge y un 0,48% con boosting; mejora en 3/5 y 2/5 años, respectivamente. En dólares, E2 aumenta el RMSE un 0,46% con Ridge y un 1,43% con boosting. El resultado no respalda todavía la hipótesis de mejora incremental; no se deben presentar las mejoras de regularización o algoritmo como evidencia del aporte externo.

La importancia de variables y las métricas completas se entregan aunque la hipótesis no resulte respaldada. Ningún cambio de rejilla, exclusión de empresa o redefinición del criterio se realizó para convertir este resultado en favorable.
