# Originales BCRPData, 2005–2025

Respuestas JSON conservadas sin modificar desde la [API oficial del BCRP](https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/api).
El manifiesto registra URL, fecha de consulta UTC y SHA-256 de cada respuesta.
Las cifras son la versión consultada; el BCRP puede revisarlas.

| Código | Serie | Periodo original |
| --- | --- | --- |
| PM04863AA | Crecimiento porcentual anual oficial del PBI real | 2005–2025 |
| PM04860AA | PBI real, millones de S/ de 2007 | 2005–2025 |
| PN38705PM | IPC Lima Metropolitana, diciembre 2021 = 100 | diciembre 2004–diciembre 2025 |
| PN01206PM | Cambio interbancario venta, promedio mensual, S/ por US$ | enero 2005–diciembre 2025 |
| PD04722MM | Tasa de referencia de política monetaria, % | enero 2005–diciembre 2025 |

BCRPData distribuye las series; las fuentes originales se detallan en el
`reports/diccionario_macroeconomia_bcrp.csv` y las fichas oficiales enlazadas allí.
El IPC corresponde a Lima Metropolitana, no al IPC nacional.
Ver las [condiciones de uso del BCRP](https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/condiciones-de-uso).

Reproducción: abrir `notebooks/03_extraccion_macroeconomica.ipynb` con el kernel
`tesis-fcl` y ejecutar todas las celdas. Requiere pandas, NumPy, Matplotlib,
requests, nbformat, nbclient e ipykernel. Las versiones verificadas se registran
en `reports/validacion_macroeconomia_bcrp.json`.
Con `ACTUALIZAR = False` se usan los originales verificando sus hashes;
con `True` se vuelve a consultar la API y se conservan en `versiones/` los originales
y manifiestos anteriores que sean reemplazados.
Si falta un original o su manifiesto, se requiere acceso a Internet.

El notebook conserva el PBI anual y su crecimiento oficial, calcula inflación diciembre/diciembre y
promedia los 12 registros mensuales de cambio y tasa, con igual peso por mes.
No imputa datos ni elimina extremos. El dataset se guarda en `data/processed/`
y los diagnósticos en `reports/`; las celdas vacías representan datos ausentes.
El RIQ utiliza solo 2005–2021 y analiza el crecimiento del PBI, no su nivel.
Los datos son revisados a la fecha de consulta, no versiones históricas en tiempo real.
