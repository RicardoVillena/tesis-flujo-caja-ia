# Correcciones de la auditoría macroeconómica

Fecha: 21 de octubre de 2026. Informe de origen: [auditoría independiente](auditoria_extraccion_macroeconomica.md).
Entrega corregida: [notebook ejecutado](../notebooks/03_extraccion_macroeconomica.ipynb).
El informe original se conserva sin editar; este documento registra la respuesta técnica, no un nuevo dictamen independiente.

| Hallazgo | Corrección o aclaración |
| --- | --- |
| CRIT-01 | RIQ ajustado exclusivamente con 2005–2021 y aplicado sin reajuste a 2022–2025. Se exportan los límites y su ventana en `umbrales_macroeconomia_bcrp.csv`. Se verifica que perturbar 2022–2025 no cambia los cuartiles. Son diagnósticos al corte de 2021, no señales disponibles en cada fecha histórica. |
| CRIT-02 | Se incorpora `crecimiento_pbi_real_pct` desde la serie oficial PM04863AA, conservando el nivel. El RIQ del PBI se aplica al crecimiento. Se contrasta la serie oficial con las variaciones del nivel desde 2006, con tolerancia absoluta de 0,02 puntos porcentuales. El crecimiento de 2005 procede directamente de la API. |
| IMP-01 | El JSON de validación, incluida su sección de ejecución, se produce íntegramente en la última celda. Usa rutas relativas y verifica hashes de archivos preexistentes. El README ya estaba modificado al comenzar el trabajo original: se conserva, sin restaurarlo contra HEAD ni atribuirle cambios de esta entrega. |
| IMP-02 | Diez bloques uniformes: título numerado en negrita y descripción breve, código, interpretación en celda Markdown independiente. El título general ocupa su propia celda. |
| IMP-03 | Se documentan los distintos conceptos: inflación diciembre/diciembre, cambio promedio mensual y tasa media mensual. Se explica que la inflación de cierre difiere de la variación de IPC medios, y que la media de diciembre no es una cotización del último día. No se amplía el dataset con otras medidas ni se integra información empresarial. |
| IMP-04 | Errores de red, JSON, codificación y estructura identifican serie y URL; la sesión se cierra incluso si falla. Se admiten sep/set/sept. Se registra Content-Type, pero se valida el cuerpo: la consulta real de crecimiento devolvió JSON válido bajo `text/html`. Una respuesta HTML real se rechaza. |
| IMP-05 | El dataset permanece en `data/processed/`; los seis reportes anteriores se regeneran en `reports/`, junto con los umbrales. Se retiran las copias obsoletas de `data/processed/`. |
| IMP-06 | El diccionario incluye disponibilidad y regla futura `anio = Ejercicio`, nunca `anio_objetivo`. Advierte que esa regla no basta: deben respetarse publicación y revisiones. No se presenta el PBI anual como disponible al cierre del mismo año. |
| OBS-01 | En reproducción completa desde caché no se escribe ningún archivo de raw, incluido el manifiesto. Las actualizaciones archivan versiones anteriores y reemplazan archivos mediante temporales. |
| OBS-02 | Exportación sin redondeo de 12 cifras; relectura con `float_precision="round_trip"` e igualdad exacta de los valores. Los originales no se redondean. |
| OBS-03 | Ponderación mensual igual a 1/12 indicada en el diccionario; no se equipara al promedio de cotizaciones diarias. |
| OBS-04 | Consulta HTTP real verificada para la nueva serie PM04863AA. Los cuatro originales anteriores se reutilizan con hashes verificados; no se afirma haberlos vuelto a descargar durante esta corrección. |

## Resultados verificados

- Dataset: 21 filas (2005–2025), cinco variables, cero faltantes y cero años duplicados.
- Extremos conservados: crecimiento del PBI de 2020 (-10,9333 %), inflación de 2022 (8,4592 %) y tasa de referencia promedio de 2023 (7,5417 %).
- El rebote del PBI de 2021 (+13,4166 %) está dentro del límite superior histórico RIQ (+15,0437 %); no se fuerza su clasificación como extremo.
- Las tasas de referencia de 2020 y 2021 quedan dentro del límite inferior histórico (0,6354 %).
- Diez celdas de código ejecutadas sin errores, desde `notebooks/` y desde la raíz. Estructura del notebook validada con nbformat.
- Reejecución con HTTP bloqueado: originales y manifiesto mantienen contenido y fecha de modificación; CSV idénticos byte a byte y JSON idéntico salvo `verificado_utc`.
- Cuatro pruebas simuladas sobre el código de extracción del notebook: timeout, HTML real, JSON incompleto y codificación inválida. Todas generan un error con serie y URL, cierran la sesión y no escriben originales. No se crearon scripts Python ni archivos de pruebas adicionales.
- Hashes del README y los dos notebooks anteriores preservados. Sin entrenamiento, integración empresarial, commit ni push.

## Límites metodológicos

Agregar crecimiento no demuestra estacionariedad ni garantiza mejorar un modelo; no se realizaron pruebas de raíz unitaria ni evaluación predictiva. El RIQ es una regla descriptiva y no una prueba econométrica de valores atípicos. La inspección exploratoria original no había entrenado modelos ni alterado valores; la corrección evita reutilizar umbrales calculados con el futuro en etapas posteriores.

Los datos son cifras revisadas a la fecha de consulta. Un backtest en tiempo real requiere las versiones disponibles y fechas efectivas de publicación de cada dato; fijar el corte del RIQ no resuelve por sí solo ese problema. Las restricciones quedan registradas en el diccionario.
