# Alineación con el plan de investigación — informe (exploratorio)

**Carácter:** exploratorio.
- Los años externos 2017–2021 ya se examinaron en los Sprints 08 y 09, y la prueba 2022–2025 no se usa.
- El cambio de población **no** se presenta como una mejora confirmada.
- El objetivo es el FCL preliminar t+1 (FCO + CAPEX reportado), que **no** es un FCFF validado ni un valor intrínseco.
- El protocolo ([protocolo.json](protocolo.json), SHA-256 `99fee593…`) se escribió el 30 de octubre de 2026 a las 13:33:30, antes de ejecutar. Como en esta revisión no hubo commits, la evidencia de que se fijó antes es la marca de tiempo y la huella del archivo.

**Diseño:**
- Validación anidada de los Sprints 08 y 09: años externos 2017–2021; 3 años internos con al menos 8 años de historia.
- Ridge y boosting, con las mismas rejillas de 8 configuraciones.
- Media histórica y persistencia como referencias.
- Soles y dólares por separado, con las mismas filas para todas las variantes de cada población.
- Regla: al menos 1 % menos de RMSE anual medio, mejora en al menos 4 de 5 años y MAE no mayor.

## Población

Las 4.221 filas originales se conservan; el filtro se aplica solo a este experimento. Detalle por año, sector y moneda en [poblacion_por_anio_sector_moneda.csv](poblacion_por_anio_sector_moneda.csv), y fila por fila en [clasificacion_filas.csv](clasificacion_filas.csv).

- **Regla principal (no financiera):** se excluyen las filas con `TipoSector` SMV en BANCOS, SEGUROS, FINANCIERAS o A.F.P. Excluir solo BANCOS dejaría dentro seguros, financieras y AFP. Ninguna empresa cambia de sector en el panel.
  - En el panel completo se excluyen 1.076 filas de 74 empresas, todas en soles.
  - En dólares no hay filas financieras: su muestra es idéntica a la del Sprint 09, que se reproduce con diferencias de hasta 5e-15 ([verificacion_reproduccion.json](verificacion_reproduccion.json)).
- **Clasificaciones dudosas,** que se conservan y se listan en [clasificaciones_dudosas.csv](clasificaciones_dudosas.csv): 78 empresas de DIVERSOS, con 460 filas de entrenamiento.
  - 15 empresas tienen CIIU 64–67, una posible actividad financiera o de holding. El CIIU mezcla revisiones y asigna códigos financieros a holdings como AENZA, InRetail y UNACEM Corp, así que no acredita la actividad principal.
  - 63 empresas no tienen CIIU ni actividad documentada.
  - No se asignó ninguna actividad por el nombre de la empresa.
- **Muestras de entrenamiento:**

  | Población | Soles | Dólares |
  |---|---|---|
  | No financiera | 1.913 filas, 200 empresas | 353 filas, 49 empresas |
  | Conservadora (sensibilidad: además excluye DIVERSOS con CIIU 64–67) | 1.811 filas, 190 empresas | 352 filas, 48 empresas |

  Filas externas evaluadas: 547 en soles y 119 en dólares en la población no financiera; 501 y 119 en la conservadora.

  **Corrección del 30 de octubre de 2026:** la población conservadora usa CIIU registrado entre 2023 y 2025 para clasificar ejercicios anteriores. Por eso es una **sensibilidad retrospectiva**, no una población disponible históricamente, y no se usa como población principal en etapas posteriores. La población principal es la regla sectorial SMV, con un límite propio: no está acreditado que `TipoSector` reflejara la actividad vigente en cada año.

## Variables ([auditoria_variables.csv](auditoria_variables.csv))

- **Tamaño** = ln(ActivoTotal(t)): sin faltantes en entrenamiento. La escala monetaria no está acreditada: un cambio entre unidades y miles desplaza el logaritmo en ≈ 6,9.
- **Apalancamiento** = pasivo/activo (el LEV de Ali): ya está en E0.
- **Efectivo y equivalentes:** **no existe** en el panel ni en los XML de SMV, así que no se evaluó. No se sustituye por FCO.
- **Historia de caja:** rezagos y volatilidad de FCO y FCL, ya presentes en E0.

## RMSE anual medio (población no financiera)

| Procedimiento | Dólares | Soles |
|---|---|---|
| Media histórica | 288.696 | 295.516 |
| **Persistencia** | **192.066** | **236.117** |
| Ridge E0 / E1 / E2 / E3 | 246.748 / 248.768 / 247.885 / 246.335 | 290.740 / 290.695 / 290.705 / 290.749 |
| Ridge E0T / E2T (con tamaño) | 246.320 / 247.507 | 291.239 / 291.202 |
| Boosting E0 / E1 / E2 / E3 | 230.788 / 232.885 / 234.081 / 234.770 | 262.279 / 262.544 / 262.520 / 262.107 |
| Boosting E0T / E2T | 236.363 / 234.419 | 265.951 / 265.569 |

Detalle en [resumen_procedimientos.csv](resumen_procedimientos.csv), [metricas_por_anio.csv](metricas_por_anio.csv), [resumen_comparaciones.csv](resumen_comparaciones.csv) y [comparaciones_por_anio.csv](comparaciones_por_anio.csv). Gráficos en [graficos/](graficos/).

## Respuestas

### 1. ¿Alinear la población cambia las conclusiones?

- **Sobre las variables externas: no.** Igual que en la población completa, ninguna comparación de E1, E2 o E3 frente a E0 o E1 cumple la regla: 0 de 16 en la no financiera y 0 de 16 en la conservadora. En soles, los cambios del RMSE quedan entre −0,07 % y +0,10 %.
- **Sobre las referencias: sí, en soles.**
  - En la población completa (Sprint 09), los modelos superaban a la persistencia en soles, cuyo RMSE era de 1.310.531.
  - En la población no financiera, la **persistencia tiene el menor RMSE en ambas monedas**. Ningún modelo la supera: los modelos son mejores solo en 1 de 5 años, y el mejor modelo en soles (boosting E3, 262.107) es un 11 % peor.
  - La ventaja de los modelos sobre la persistencia en soles provenía, por tanto, de las empresas financieras excluidas.
- **Sobre el algoritmo:** en soles no financieros, boosting supera a Ridge de forma consistente con todas las variantes (−8,7 % a −9,9 % de RMSE, 5 de 5 años, MAE −12,6 % a −16,3 %). En dólares no cumple la regla (mejora en 3 de 5 años).
- **Alcance de la comparación:** las poblaciones tienen filas distintas, así que se comparan las conclusiones, no las métricas entre poblaciones.

### 2. ¿Tamaño, apalancamiento y efectivo aportan mejora?

- **Tamaño: no.**
  - E0T frente a E0 no cumple en ninguna combinación: dólares Ridge −0,17 % (4 años, el RMSE no baja el 1 %), dólares boosting +2,42 %, soles Ridge +0,17 %, soles boosting +1,40 %.
  - E2T frente a E2 tampoco cumple en ninguna.
  - Como bloque, el tamaño no aporta de forma estable. En soles con boosting, retirarlo de E2T sube el RMSE un +4,79 % en media, pero solo en 3 de 5 años; además, añadirlo con reajuste empeora (E0T frente a E0). Las dos medidas difieren porque la retirada usa la configuración de E2T congelada.
- **Apalancamiento:** ya estaba en todas las variantes, así que no se evaluó como bloque nuevo. Su importancia individual figura en [importancia_individual.csv](importancia_individual.csv) (`pasivo_activo`), sin aporte estable.
- **Efectivo:** no evaluable; queda pendiente porque requiere estados detallados de SMV.

### 3. ¿Las variables externas ayudan en alguna especificación de forma consistente?

**No.** No cumplen la regla en ninguna comparación de ninguna de las dos poblaciones, ni con Ridge ni con boosting, ni junto al tamaño (E2T frente a E0T). Retirarlas de E2T tampoco muestra aporte estable: el bloque macroeconómico cambia el RMSE entre −0,78 % y +0,02 % en media, y el bursátil entre −0,24 % y +0,23 %.

El aporte estable proviene del **bloque financiero**: retirarlo aumenta el RMSE en dólares un 20–22 % (4–5 de 5 años) y en soles un +18,39 % con boosting y un +1,48 % con Ridge (4 de 5 años). Los atributos individuales con aporte estable son todos financieros:
- Dólares, Ridge: `FCL_preliminar_std3_previa`, `FCO_std3_previa`, `FCO_lag3` y `FCO_lag1`.
- Dólares, boosting: `crecimiento_TotalIngreso`.
- Soles, boosting: `FCO_lag1`, `crecimiento_ActivoTotal` y `fco_ingresos`.

### 4. ¿Qué objetivos e hipótesis originales quedan realmente evaluados?

Ver [matriz_consistencia.md](matriz_consistencia.md).

| Plan | Estado |
|---|---|
| H1 / OE1 (LSTM + Monte Carlo, colas) | **No evaluados.** Solo se evalúa el pronóstico puntual del FCL preliminar t+1 frente a referencias deterministas, y no supera a la persistencia en la población del plan. |
| H2 / OE2 (apalancamiento y efectivo sobre el valor) | **Parcial y desplazado.** El apalancamiento está incluido sin aporte estable; el efectivo no existe en los datos; la variable dependiente no es el valor. |
| H3 / OE3 (incertidumbre global × tamaño sobre el precio) | **No evaluados.** No hay índices de incertidumbre global ni precios por emisor. Se evaluaron el tamaño y los externos agregados para el FCL, sin mejora. |
| H4 / OE4 (XAI y gobernanza) | **No evaluados.** Solo hay importancia por retirada con reajuste; no hay SHAP ni un proceso Human-in-the-Loop. |
| Población no financiera | **Aplicada** (regla SMV), con dudosas documentadas. |

### 5. ¿Qué falta para pasar de predicción del FCL preliminar a valoración probabilística?

Ver [viabilidad_pendientes.md](viabilidad_pendientes.md):
- un flujo económicamente validado (FCFF), con EBIT, impuestos, depreciación, capital de trabajo y deuda financiera, que no están en el panel;
- precios y acciones por emisor;
- tasa libre de riesgo, riesgo país, betas y costo de deuda locales;
- supuestos de valor terminal;
- historia suficiente para la LSTM (series anuales de 5 a 15 pasos por empresa);
- una evaluación probabilística fuera de muestra (cobertura de intervalos, CRPS y pinball, excedencias de colas) antes de atribuir cualquier mejora a una simulación.

## Importancia: interpretación

- Es una importancia predictiva condicional al modelo y a los demás atributos; **no implica causalidad**.
- La redundancia (por ejemplo, entre rezagos de FCO y FCL, o entre tamaño y niveles monetarios) puede repartir u ocultar aportes.
- Los externos no se permutaron entre empresas del mismo año: se retiraron y se reajustó el modelo.

Detalle en [importancia_individual_por_anio.csv](importancia_individual_por_anio.csv), [importancia_bloques_por_anio.csv](importancia_bloques_por_anio.csv) y [los gráficos de importancia](graficos/).

## Limitaciones

- Cinco años externos reutilizados, que no constituyen confirmación independiente.
- En soles no financieros, entre el 84 % y el 88 % del error cuadrático se concentra en 3 empresas; la empresa dominante es CM0004 ([concentracion_error.csv](concentracion_error.csv)).
- La disponibilidad temporal de los datos al pronosticar y sus versiones históricas no están acreditadas.
- La escala monetaria no está acreditada.
- Las clasificaciones dudosas siguen pendientes de verificación documental.
- Las conclusiones se limitan a Ridge y HistGradientBoosting con estas rejillas.

## Antecedentes

Ver [antecedentes.md](antecedentes.md):
- **Ali (2026)** y **Pham (2026):** verificados en el texto original; ambos predicen valor de mercado, no flujos.
- **Lu y Zhao (2025):** solo metadatos y resumen.
