# Sprint 08 — Informe final consolidado

Rama local `sprint-08-auditoria-calidad`, sin commits del Sprint 08. Cierre documental: 29 de octubre de 2026.
Este informe resume y enlaza la evidencia; los informes de cada etapa contienen el detalle.
Estado de las pruebas: [estado_verificacion.md](estado_verificacion.md). Punto de entrada: [README.md](README.md).

## 1. Objetivo y alcance final

**Objetivo:** auditar la calidad de los 26 atributos del experimento E2 y comprobar, solo con entrenamiento, si retirar atributos o cambiar de algoritmo mejora la predicción del FCL preliminar del año siguiente.

**Alcance:** la planificación escrita disponible ([instrucciones_claude.md](instrucciones_claude.md)) cubre solo la Etapa 1, que excluía entrenar modelos nuevos. Las etapas siguientes se añadieron por encargos posteriores dentro del mismo sprint:

| Etapa | Contenido | Estado en este informe | Evidencia |
|---|---|---|---|
| 1 | Auditoría descriptiva de calidad de los 26 atributos | Resultado final | [resumen_auditoria.md](resumen_auditoria.md) |
| 2a | Ablación individual (Ridge con alpha = 1) y primera validación anidada | Antecedente trazable | [ablacion/informe_ablacion.md](ablacion/informe_ablacion.md) |
| 2b | Revisión de la validación anidada: elección entre retiradas admisibles, rejilla de alpha ampliada, referencias simples | **Resultado final de selección de variables** | [ablacion_revision/informe_revision.md](ablacion_revision/informe_revision.md) |
| 3 | Comparación acotada: media histórica, persistencia, Ridge, Elastic Net y boosting, con la decisión corregida | **Resultado final de modelado** | [comparacion_modelos/informe_comparacion.md](comparacion_modelos/informe_comparacion.md) |

En todas las etapas se cumplió lo siguiente:
- No se modificaron fuentes, objetivo, elegibilidad, particiones ni E0/E1/E2.
- No se usaron filas, objetivos, predicciones ni métricas de prueba 2022–2025.
- No hubo commits ni despliegues.

## 2. Datos, objetivo, monedas y particiones

- **Panel:** `data/processed/panel_financiero_macro_bursatil.csv`, con 4.221 filas empresa-ejercicio, de las que 3.560 son elegibles.
  - Entrenamiento: 2.869 filas, años objetivo 2006–2021 (ejercicios 2005–2020).
  - Prueba: 691 filas, años objetivo 2022–2025.
  - Sprint 08 usa **solo entrenamiento**.
- **Objetivo:** `objetivo_fcl_t1` = FCL_preliminar(t+1) = FCO(t+1) + CAPEX_reportado(t+1) de la misma empresa (RPJ).
  - Se une por Ejercicio + 1 exacto, nunca por la fila siguiente.
  - Queda inválido si CAPEX(t+1) > 0.
  - Es elegible solo si el objetivo no falta y la moneda es la misma en t y t+1.
  - Es un **FCL preliminar, no un FCFF validado**.
- **Monedas:** soles (2.516 filas de entrenamiento, 269 empresas) y dólares (353 filas, 49 empresas; etiqueta original `D lares`). Siempre se modelan y evalúan por separado; nunca se suman errores entre monedas.
- **Atributos E2 (26):** 19 financieros, 4 macroeconómicos y 3 bursátiles. Su orden se verificó contra el código literal del notebook 07 y [especificacion_e2.json](especificacion_e2.json).

## 3. Auditoría de calidad de los 26 atributos (problemas del dato)

Fuente: [resumen_auditoria.md](resumen_auditoria.md), [hallazgos_calidad.csv](hallazgos_calidad.csv) y [tabla_26_atributos.csv](tabla_26_atributos.csv).

- **Controles superados:**
  - Las variables financieras y el objetivo se reconstruyen exactamente desde la fuente.
  - Las 8.285 celdas faltantes de entrenamiento tienen causa identificada (estructural por rezago, regla de cálculo o fuente ausente); ninguna queda sin explicar.
  - No hay constantes, infinitos, duplicados ni dependencias lineales exactas.
- **Hallazgos:** 21 en total, 16 comprobados y 5 sospechas pendientes. Por ejemplo:
  - Una correlación de Pearson de 0,9996 (soles) se debe a un solo caso: FOSSAL 2017, cuyo ActivoTotal de 2016 vale 1.
  - El número de condición de la matriz E2 en soles baja de 221,43 a 18,39 al excluir tres casos.
  - CD0009 2016 muestra un salto de aproximadamente ×1000 que revierte al año siguiente. Es una sospecha de escala, no un error declarado.
- **Disponibilidad temporal:**

  | Categoría | Atributos |
  |---|---|
  | Disponibilidad verificada | 0 |
  | Disponibilidad no verificada | 14 |
  | Posible fuga temporal | 12 |

  No hay fechas de publicación ni versiones históricas (vintages); `revision_interanual` no tiene algoritmo documentado.
- **Alcance:** estos son problemas de **calidad del dato**. No demuestran que un atributo perjudique la predicción.

## 4. Ablación y validación temporal anidada (evidencia sobre retirar variables)

- **Antecedente, ablación individual** ([ablacion/resumen_ablacion.csv](ablacion/resumen_ablacion.csv)):
  - Con Ridge y alpha = 1, en los pliegues de Sprint 06, hubo 6 candidatas en dólares y 3 en soles.
  - Solo `FCO_lag1` y `FCL_preliminar_std3_previa` (dólares) resistieron al excluir los casos dominantes.
  - Es un diagnóstico condicionado a alpha = 1, no una selección.
- **Antecedente, primera validación anidada** ([ablacion/anidada_resumen.csv](ablacion/anidada_resumen.csv)): el cambio de RMSE del procedimiento reducido fue −2,74 % en dólares ("evidencia insuficiente") y +0,71 % en soles ("conservar el modelo completo"). La revisión detectó dos problemas:
  - `seleccionar()` se detenía si la retirada de menor RMSE no era estable, aunque otra sí lo fuera.
  - Alpha quedaba en el máximo de la rejilla en soles.
- **Resultado final, revisión** ([ablacion_revision/decision_final.csv](ablacion_revision/decision_final.csv), [ablacion_revision/resumen.csv](ablacion_revision/resumen.csv)):
  - Años externos 2017–2021; 3 años internos con al menos 8 años de historia.
  - La revisión corrigió la elección, que ahora toma la mejor entre las retiradas admisibles, y amplió la rejilla de alpha hasta 1.000.000.
  - **Dólares:** el reducido baja el RMSE anual medio un −2,73 %, pero mejora en 1 año y empeora en 3. Decisión: conservar los 26 atributos.
  - **Soles:** el reducido es idéntico al completo (0,00 %; no retira nada en ningún año). Decisión: conservar los 26 atributos.
  - La lista que propone el procedimiento ajustado con todo el entrenamiento (`crecimiento_pbi_real_pct` en dólares) **no se adopta**: no tiene métricas externas propias.
- **Conclusión sobre variables:** se conservan provisionalmente los 26 atributos. No se encontró una reducción consistentemente mejor, lo que no implica que todos sean útiles para cualquier modelo.

## 5. Comparación de modelos (desempeño predictivo)

Fuente: [comparacion_modelos/resumen_procedimientos.csv](comparacion_modelos/resumen_procedimientos.csv), [comparacion_modelos/resumen_comparaciones.csv](comparacion_modelos/resumen_comparaciones.csv) y [comparacion_modelos/decision.csv](comparacion_modelos/decision.csv).

Validación anidada con las mismas filas externas para todos los procedimientos (119 en dólares, 829 en soles). Las rejillas se fijaron antes de ejecutar:
- Ridge: 8 configuraciones.
- Elastic Net, con objetivo estandarizado en cada entrenamiento: 12 configuraciones.
- HistGradientBoosting, con `early_stopping=False` y semilla 0: 8 configuraciones.

Las 280 búsquedas internas convergieron. La media histórica, la persistencia y Ridge reproducen exactamente la revisión anterior (diferencia relativa ≤ 5e-15).

RMSE anual medio (promedio simple de 5 años, en la unidad monetaria reportada):

| Moneda | Media histórica | Persistencia | Ridge | Elastic Net | Boosting |
|---|---|---|---|---|---|
| Dólares | 288.696 | **192.066** | 247.885 | 259.556 | 234.081 |
| Soles | 933.387 | 1.310.531 | 919.862 | 943.622 | **911.069** |

**Regla para recomendar un cambio** (predefinida y exploratoria, no es significancia estadística): reducir el RMSE anual medio al menos un 1 %, tener menor RMSE en al menos 4 de 5 años y no empeorar el MAE anual medio, frente a cada comparador.

**Menor error observado frente a recomendación:** que un procedimiento tenga el menor RMSE no significa que tenga superioridad consistente. `decision.csv` registra por separado el menor RMSE observado, la superioridad consistente, el modelo vigente y el cambio recomendado.

- **Dólares:**
  - La persistencia cumple la regla frente a los otros cuatro procedimientos; por ejemplo, frente a Ridge su RMSE es un −22,52 % menor y su MAE un −30,53 %, mejor en 4 de 5 años.
  - Boosting mejora a Ridge un −5,57 % en RMSE, pero solo en 3 de 5 años.
  - Ni Elastic Net ni boosting superan a la persistencia.
- **Soles:**
  - Boosting tiene el menor RMSE observado. Frente a Ridge mejora el RMSE un **0,956 %** y el MAE un **9,80 %**, con menor RMSE en 4 de 5 años, pero no alcanza el umbral del 1 % de RMSE.
  - Ningún procedimiento tiene superioridad consistente frente a todos.
  - Ridge supera de forma consistente a la media histórica (−1,45 %) y a la persistencia (−29,81 %).
- **Concentración del error:** las 3 empresas con más error concentran entre el 81,5 % y el 89,5 % del error cuadrático externo.
  - Al excluir a CM0006 en dólares, la persistencia sigue siendo la mejor.
  - Al excluir a B80004 en soles, Ridge pasa a tener el menor RMSE.
  - Esta sensibilidad es descriptiva y posterior al análisis; no modifica la decisión.

## 6. Conclusiones por moneda

| | Selección de variables | Menor RMSE observado | Superioridad consistente | Modelo vigente tras la comparación | Cambio recomendado |
|---|---|---|---|---|---|
| Dólares | Conservar los 26 atributos | Persistencia | Persistencia | Persistencia | Sustituir Ridge por persistencia (exploratorio; requiere confirmación en datos no examinados) |
| Soles | Conservar los 26 atributos | Boosting | Ninguna | Ridge | Conservar Ridge; no se recomienda sustituirlo |

- En dólares, ningún modelo con atributos supera a la persistencia simple. Esto indica que el modelo **no aporta una mejora consistente** frente a esa referencia en estos años.
- En soles, mantener Ridge **no demuestra** que supere a boosting, ni que ambos sean equivalentes, ni que boosting sea inútil. Significa que la evidencia no cumple el criterio predefinido para cambiar.
- **Todas las decisiones son exploratorias.** Los años externos 2017–2021 ya se usaron en la ablación y en su revisión, y elegir un ganador con ellos lo favorece. Estas conclusiones no son una confirmación independiente, ni un despliegue, ni una superioridad general.

## 7. Verificaciones, limitaciones y pendientes

**Verificaciones:**
- Pruebas por etapa, ejecutadas en el cierre (29 de octubre de 2026):
  - Etapa 1: 15 de 16 aprobadas; falla la prueba de integridad de archivos previos.
  - Ablación y revisión: 21 de 21 aprobadas.
  - Comparación: 15 de 15 aprobadas.
- La suite completa **no está totalmente aprobada**: 96 pruebas, 3 fallos de integridad causados por archivos modificados ajenos al modelado. La evidencia está en [estado_verificacion.md](estado_verificacion.md).

**Limitaciones:**
- Hay solo 5 años externos por moneda, y en dólares cada año tiene entre 21 y 26 filas.
- El error se concentra en pocas empresas, que además no son independientes entre años.
- No hay fechas de publicación ni vintages.
- La escala monetaria no está acreditada.
- Algunas búsquedas eligieron el extremo de su rejilla, que no se amplió después de ver resultados:
  - Elastic Net elige su alpha máximo en 5 de 5 años en dólares y en 4 de 5 en soles.
  - Ridge alcanza alpha = 1.000.000 en 3 de 5 años en soles.

### Pendientes fuera del sprint

**Ya documentados como limitación** en informes anteriores, pero no resueltos:

| Pendiente | Evidencia existente | Qué falta comprobar |
|---|---|---|
| Uso previo de la partición de prueba 2022–2025 | Sprint 06 calculó métricas de prueba (`reports/sprint_06/resultados_experimentos.csv` tiene 18 filas con `particion = prueba`). El notebook 08 de Sprint 06 declara que la prueba "ya fue analizada por 07… no es una prueba virgen". | Inventario completo de qué notebooks, informes y decisiones consultaron prueba, antes de diseñar una confirmación. Sprint 08 no la usó (verificado por pruebas). |
| Cómo evaluar en datos no examinados | Todas las decisiones del Sprint 08 se declaran exploratorias. | Definir el conjunto de confirmación, por ejemplo años futuros o una prueba no consultada, el protocolo congelado y quién lo ejecuta. |
| Disponibilidad real de estados financieros y variables externas al pronosticar | Auditoría temporal: 0 atributos verificados y 12 con posible fuga. La persistencia también usa FCL(t). | Fechas de presentación SMV por empresa y ejercicio, fechas de publicación BCRP/INEI y una fecha de pronóstico operativa. |
| Revisiones históricas y ausencia de versiones originales | `revision_interanual` sin algoritmo documentado; series BCRP consultadas en 2026 (versión revisada). | Recuperar reportes originales y vintages; medir el efecto de las reexpresiones. |
| Escala monetaria | `data/README.md` y la Etapa 1 declaran la escala no acreditada; hay saltos de magnitud por conciliar (por ejemplo, CD0009 2016). | Acreditar unidades o miles por emisor y ejercicio. |
| Validación económica del FCL preliminar | El objetivo es FCO + CAPEX reportado, no FCFF; la extracción histórica de FCO y CAPEX no es reproducible (`reports/procedimiento_smv.md`). | Validar el mapeo de cuentas por sector y formato, y la pertinencia para bancos y seguros. No presentarlo como FCFF validado. |

**Comprobaciones no realizadas en este sprint:**
- Consulta a fuentes originales SMV o BCRP.
- Conciliación documental de los casos extremos.
- Evaluación en prueba.
- Análisis de significancia estadística.
