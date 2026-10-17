# Correcciones de la auditoría independiente — Semana 5

El informe original de auditoría se conserva únicamente de forma local y se excluye de esta rama pública. Las correcciones se implementan en el módulo, notebook, pruebas y documentación; no se entrenan modelos ni se modifican las fuentes.

| Hallazgo | Acción y evidencia | Estado / límite |
| --- | --- | --- |
| HAL-01 | Se verifican las tres identidades lineales y las dos multiplicativas DuPont en entrenamiento. Diagnósticos de rango y VIF por moneda, antes y después de excluir `fcl_activo`, `FCO_mean3_previa` y `FCL_preliminar_mean3_previa`. Lista explícita `PREDICTORS_NO_COLINEALES` de 19. | Rango observado 19/22 y 19/19 en ambas monedas. Persiste dependencia estadística y VIF alto; 19 no garantiza explicaciones SHAP independientes ni estables. |
| HAL-02 | Se invalida internamente FCL cuando el CAPEX de su año es positivo, antes de construir ratios, variaciones, rezagos, ventanas y etiquetas. La columna fuente se preserva en la exportación. Prueba con FCL no pre-anulado y CAPEX positivo. | Corregido y probado; no cambia la elegibilidad del panel real, que ya traía esos FCL anulados. |
| HAL-03 | Se exige ingreso actual positivo en rotación y crecimiento, además de base previa positiva para crecimiento. Pruebas con ingresos actuales cero y negativos, y base previa inválida. | Corregido; las cifras originales de ingresos se conservan. Es una convención de dominio para estos ratios, no evidencia de error en el ingreso reportado. |
| HAL-04 | `Pipeline(SimpleImputer, RobustScaler)` ajustado por moneda solo en entrenamiento. Se prueba conservación de parámetros al transformar prueba y se informa IQR escalado. | IQR de crecimiento de activos = 1 en entrenamiento para ambas monedas. RobustScaler no elimina ni acota los extremos. |
| HAL-05 | Comparación completos/incompletos: tamaño, historial, ingresos, disponibilidad por año y Mann-Whitney bilateral por moneda. Prohibición explícita de usar `dropna()` sobre predictores para modelado. | Se conservan todas las filas elegibles. P-valores exploratorios; la dependencia longitudinal limita la inferencia independiente. |
| HAL-06 | Tabla de revisión por partición y moneda y protocolo de Semana 6 para evaluar grupos y auditar publicación de todas las fuentes históricas de cada ventana. Se explicita selección ex post por moneda y permanencia. | Limitación pendiente de datos: sin fechas/vintages no puede corregirse el sesgo de fuente. La bandera por sí sola no prueba cuándo ni por qué ocurrió una revisión; False tampoco garantiza disponibilidad histórica. No se inventan fechas ni se calculan métricas de modelos. |
| HAL-07 | Sensibilidad en memoria de los diez predictores temporales divididos por ActivoTotal(t), y etiqueta dividida por activos positivos de t solo con moneda consistente. Se documenta reconstrucción y evaluación por tamaño/moneda. | Esquema implementado sin ampliar las 22 características exportadas ni cambiar el objetivo principal. Selección de representación y métricas predictivas pendientes de Semana 6. No corrige inflación ni activos muy pequeños. |
| HAL-08 | Diccionario documenta orden canónico `(RPJ, Ejercicio)`; se conserva unicidad y trazabilidad por clave. | Corregido. No se afirma preservación del orden físico de entrada. |
| HAL-09 | Factory de Pipeline sin ajustar; prueba con `clone` y entrenamiento de un prefijo distinto. Notebook exige crear/clonar y reajustar dentro de cada pliegue temporal por moneda. | Corregido el diseño; validación cruzada predictiva pendiente de Semana 6. Las matrices ilustrativas actuales son solo para el holdout fijo. |
| HAL-10 | Lectura explícita `utf-8-sig`; presentación de `Dólares` y métodos de flujo mediante mapeo de etiquetas. | CSV fuente/exportación conservan etiquetas originales para trazabilidad. |
| HAL-11 | `MaxNLocator(integer=True)` para el gráfico anual; mapas de calor anotados con coeficientes. | Corregido y notebook ejecutado. |
| HAL-12 | Notebook y ejecutor aceptan Python 3.12.x, manteniendo verificación de entorno tesis-fcl y registro de versión exacta usada. | Verificado en Python 3.12.15; no se afirma haber probado otras versiones de parche. |

## Resultado verificado

- 4.221 filas conservadas, 336 empresas, años 2005–2025; 57 columnas exportadas.
- 22 características disponibles y subconjunto lineal de 19; 3.560 pares elegibles de 309 empresas.
- Entrenamiento: 2.869; prueba: 691; casos completos: 2.251 (1.674 entrenamiento, 577 prueba). Los casos completos no son un filtro de modelado.
- 11 pruebas unitarias ejecutadas sin fallos ni errores, incluidas tres pruebas nuevas de regresión para las correcciones.
- Notebook ejecutado completamente con kernel tesis-fcl: 11 celdas de código, sin errores.
- IQR robusto de crecimiento de activos igual a 1 en cada moneda. Exigir casos completos eliminaría por completo 69 empresas y todos los orígenes 2005–2007.
- Mann-Whitney de activos, completos frente a incompletos: p exploratorio 7,2648e-27 en soles y 1,8429e-08 en dólares; no se usa para elegir predictores.
- La evidencia de ejecución y hashes se registra en `reports/validacion_ejecucion.json`; el resumen y diccionario se regeneran desde el notebook corregido.

No se instalaron paquetes ni se realizaron commits, push, merge u operaciones destructivas. El objetivo sigue siendo FCL preliminar de t+1, no FCFF económicamente validado.
