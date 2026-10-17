# Trazabilidad de las 22 características y los objetivos


Generado por `scripts/reproduce_features.py` a partir del código y del panel incluido.


Implementación: `src/feature_engineering.py::build_features`. `divide` acepta solo denominador positivo.


`d` está ordenado por RPJ/ejercicio; `groups` agrupa RPJ y segmento_temporal. Un hueco anual o cambio de moneda rompe el segmento, incluso si vuelve la moneda original.


No se eliminan filas ni imputan valores; NaN se serializa como campo vacío. Escala monetaria no acreditada. Los predictores son retrospectivos según ejercicio, sin fechas de publicación verificadas.


Cada validación de exportación compara todas las filas y la máscara de NaN contra una regeneración independiente del notebook; no acredita el origen contable de las fuentes. Las pruebas sintéticas cubren ceros, faltantes, límites temporales, moneda y ausencia de influencia futura.


## pasivo_activo


- Definición: Proporción de activos financiados con pasivos; no equivale a deuda financiera.

- Fórmula: 1 × PasivoTotal(t) / ActivoTotal(t), denominador > 0.

- Unidad: adimensional.

- Columnas originales: PasivoTotal, ActivoTotal.

- Python: `divide(d.PasivoTotal * (1), d.ActivoTotal)`.

- Faltantes: Propaga NaN; no imputa. Numerador cero se conserva.

- Ceros/dominio: Denominador > 0; cero, negativo o faltante produce NaN; infinito se convierte en NaN.

- Continuidad/moneda: En t y moneda de la fila; no combina ejercicios ni monedas.

- Validación: 4221 observados, 0 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## margen_neto


- Definición: Resultado neto por unidad de ingreso total; no equivale a margen operativo.

- Fórmula: 1 × UtilidadNeta(t) / TotalIngreso(t), denominador > 0.

- Unidad: adimensional.

- Columnas originales: UtilidadNeta, TotalIngreso.

- Python: `divide(d.UtilidadNeta * (1), d.TotalIngreso)`.

- Faltantes: Propaga NaN; no imputa. Numerador cero se conserva.

- Ceros/dominio: Denominador > 0; cero, negativo o faltante produce NaN; infinito se convierte en NaN.

- Continuidad/moneda: En t y moneda de la fila; no combina ejercicios ni monedas.

- Validación: 3950 observados, 271 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## rentabilidad_activo_cierre


- Definición: Rentabilidad contable respecto al activo al cierre, no activo promedio.

- Fórmula: 1 × UtilidadNeta(t) / ActivoTotal(t), denominador > 0.

- Unidad: adimensional.

- Columnas originales: UtilidadNeta, ActivoTotal.

- Python: `divide(d.UtilidadNeta * (1), d.ActivoTotal)`.

- Faltantes: Propaga NaN; no imputa. Numerador cero se conserva.

- Ceros/dominio: Denominador > 0; cero, negativo o faltante produce NaN; infinito se convierte en NaN.

- Continuidad/moneda: En t y moneda de la fila; no combina ejercicios ni monedas.

- Validación: 4221 observados, 0 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## rotacion_activo_cierre


- Definición: Ingreso total generado por unidad de activo al cierre.

- Fórmula: 1 × TotalIngreso(t) / ActivoTotal(t), denominador > 0; ingreso actual > 0.

- Unidad: adimensional.

- Columnas originales: TotalIngreso, ActivoTotal.

- Python: `divide(d.TotalIngreso.where(d.TotalIngreso > 0), d.ActivoTotal)`.

- Faltantes: Propaga NaN; no imputa. Numerador cero se conserva.

- Ceros/dominio: Denominador > 0; cero, negativo o faltante produce NaN; infinito se convierte en NaN. Ingreso actual <= 0 se invalida.

- Continuidad/moneda: En t y moneda de la fila; no combina ejercicios ni monedas.

- Validación: 3950 observados, 271 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## fco_activo


- Definición: Generación operativa de efectivo relativa al tamaño.

- Fórmula: 1 × FCO(t) / ActivoTotal(t), denominador > 0.

- Unidad: adimensional.

- Columnas originales: FCO, ActivoTotal.

- Python: `divide(d.FCO * (1), d.ActivoTotal)`.

- Faltantes: Propaga NaN; no imputa. Numerador cero se conserva.

- Ceros/dominio: Denominador > 0; cero, negativo o faltante produce NaN; infinito se convierte en NaN.

- Continuidad/moneda: En t y moneda de la fila; no combina ejercicios ni monedas.

- Validación: 4131 observados, 90 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## fco_ingresos


- Definición: Conversión de ingresos en flujo operativo.

- Fórmula: 1 × FCO(t) / TotalIngreso(t), denominador > 0.

- Unidad: adimensional.

- Columnas originales: FCO, TotalIngreso.

- Python: `divide(d.FCO * (1), d.TotalIngreso)`.

- Faltantes: Propaga NaN; no imputa. Numerador cero se conserva.

- Ceros/dominio: Denominador > 0; cero, negativo o faltante produce NaN; infinito se convierte en NaN.

- Continuidad/moneda: En t y moneda de la fila; no combina ejercicios ni monedas.

- Validación: 3865 observados, 356 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## inversion_capex_activo


- Definición: Esfuerzo inversor reportado relativo al activo; excluye CAPEX positivo.

- Fórmula: -1 × CAPEX_reportado(t) / ActivoTotal(t), denominador > 0; solo CAPEX_reportado <= 0.

- Unidad: adimensional.

- Columnas originales: CAPEX_reportado, ActivoTotal.

- Python: `divide((-d.CAPEX_reportado).where(d.CAPEX_reportado <= 0), d.ActivoTotal)`.

- Faltantes: Propaga NaN; no imputa. Numerador cero se conserva.

- Ceros/dominio: Denominador > 0; cero, negativo o faltante produce NaN; infinito se convierte en NaN. CAPEX positivo se invalida.

- Continuidad/moneda: En t y moneda de la fila; no combina ejercicios ni monedas.

- Validación: 3952 observados, 269 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## fcl_activo


- Definición: Flujo libre preliminar relativo al tamaño; no FCFF validado; redundante exacta: excluir del subconjunto lineal de 19.

- Fórmula: 1 × FCL_preliminar(t) / ActivoTotal(t), denominador > 0; FCL fuente invalidado si CAPEX de su año > 0.

- Unidad: adimensional.

- Columnas originales: FCL_preliminar, ActivoTotal, CAPEX_reportado.

- Python: `divide(d.FCL_preliminar * (1), d.ActivoTotal)`.

- Faltantes: Propaga NaN; no imputa. Numerador cero se conserva. Todas las derivaciones usan FCL validado: NaN cuando CAPEX de su año > 0; no altera FCL fuente.

- Ceros/dominio: Denominador > 0; cero, negativo o faltante produce NaN; infinito se convierte en NaN.

- Continuidad/moneda: En t y moneda de la fila; no combina ejercicios ni monedas.

- Validación: 3898 observados, 323 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## crecimiento_ActivoTotal


- Definición: Expansión anual con continuidad y moneda constante.

- Fórmula: (ActivoTotal(t) - ActivoTotal(t-1)) / ActivoTotal(t-1), base > 0.

- Unidad: adimensional.

- Columnas originales: ActivoTotal, RPJ, Ejercicio, Moneda.

- Python: `prev = groups['ActivoTotal'].shift(1); divide(d.ActivoTotal - prev, prev)`.

- Faltantes: Propaga NaN; no imputa. Numerador cero se conserva.

- Ceros/dominio: Denominador > 0; cero, negativo o faltante produce NaN; infinito se convierte en NaN.

- Continuidad/moneda: Requiere t-1 exacto en el mismo segmento anual de empresa y moneda.

- Validación: 3822 observados, 399 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## crecimiento_TotalIngreso


- Definición: Expansión anual con continuidad y moneda constante.

- Fórmula: (TotalIngreso(t) - TotalIngreso(t-1)) / TotalIngreso(t-1), base > 0; ingreso actual > 0.

- Unidad: adimensional.

- Columnas originales: TotalIngreso, RPJ, Ejercicio, Moneda.

- Python: `prev = groups['TotalIngreso'].shift(1); divide(d.TotalIngreso.where(d.TotalIngreso > 0) - prev, prev)`.

- Faltantes: Propaga NaN; no imputa. Numerador cero se conserva.

- Ceros/dominio: Denominador > 0; cero, negativo o faltante produce NaN; infinito se convierte en NaN. Ingreso actual <= 0 se invalida.

- Continuidad/moneda: Requiere t-1 exacto en el mismo segmento anual de empresa y moneda.

- Validación: 3568 observados, 653 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## cambio_FCO_activo_previo


- Definición: Cambio de efectivo relativo al tamaño anterior; admite flujos negativos.

- Fórmula: (FCO(t)-FCO(t-1))/ActivoTotal(t-1).

- Unidad: adimensional.

- Columnas originales: FCO, ActivoTotal, RPJ, Ejercicio, Moneda.

- Python: `divide(d['FCO'] - groups['FCO'].shift(1), groups.ActivoTotal.shift(1))`.

- Faltantes: Propaga NaN; no imputa. Numerador cero se conserva.

- Ceros/dominio: Denominador > 0; cero, negativo o faltante produce NaN; infinito se convierte en NaN.

- Continuidad/moneda: Requiere t-1 exacto en el mismo segmento anual de empresa y moneda.

- Validación: 3701 observados, 520 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## FCO_lag1


- Definición: Persistencia histórica por empresa y segmento.

- Fórmula: FCO(t-1).

- Unidad: unidad monetaria reportada, escala no acreditada.

- Columnas originales: FCO, RPJ, Ejercicio, Moneda.

- Python: `groups['FCO'].shift(1)`.

- Faltantes: NaN si falta el valor desplazado o la historia suficiente; sin imputación.

- Ceros/dominio: No hay denominador financiero; ceros y flujos negativos son válidos.

- Continuidad/moneda: Requiere 1 filas anuales anteriores del mismo segmento, sin huecos ni cambios de moneda.

- Validación: 3734 observados, 487 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## FCO_lag2


- Definición: Persistencia histórica por empresa y segmento.

- Fórmula: FCO(t-2).

- Unidad: unidad monetaria reportada, escala no acreditada.

- Columnas originales: FCO, RPJ, Ejercicio, Moneda.

- Python: `groups['FCO'].shift(2)`.

- Faltantes: NaN si falta el valor desplazado o la historia suficiente; sin imputación.

- Ceros/dominio: No hay denominador financiero; ceros y flujos negativos son válidos.

- Continuidad/moneda: Requiere 2 filas anuales anteriores del mismo segmento, sin huecos ni cambios de moneda.

- Validación: 3392 observados, 829 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## FCO_lag3


- Definición: Persistencia histórica por empresa y segmento.

- Fórmula: FCO(t-3).

- Unidad: unidad monetaria reportada, escala no acreditada.

- Columnas originales: FCO, RPJ, Ejercicio, Moneda.

- Python: `groups['FCO'].shift(3)`.

- Faltantes: NaN si falta el valor desplazado o la historia suficiente; sin imputación.

- Ceros/dominio: No hay denominador financiero; ceros y flujos negativos son válidos.

- Continuidad/moneda: Requiere 3 filas anuales anteriores del mismo segmento, sin huecos ni cambios de moneda.

- Validación: 3073 observados, 1148 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## FCO_mean3_previa


- Definición: Nivel o volatilidad de tres años estrictamente anteriores; redundante exacta: excluir del subconjunto lineal de 19.

- Fórmula: mean de FCO(t-3), FCO(t-2), FCO(t-1).

- Unidad: unidad monetaria reportada, escala no acreditada.

- Columnas originales: FCO, RPJ, Ejercicio, Moneda.

- Python: `groups['FCO'].transform(lambda s: s.shift(1).rolling(3, min_periods=3).mean())`.

- Faltantes: Los tres valores previos deben estar observados; cualquier NaN invalida la ventana.

- Ceros/dominio: No hay denominador financiero; ceros y flujos negativos son válidos.

- Continuidad/moneda: Requiere t-3, t-2 y t-1 contiguos en la misma empresa y moneda; excluye t.

- Validación: 3013 observados, 1208 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## FCO_std3_previa


- Definición: Nivel o volatilidad de tres años estrictamente anteriores.

- Fórmula: std de FCO(t-3), FCO(t-2), FCO(t-1); ddof=1.

- Unidad: unidad monetaria reportada, escala no acreditada.

- Columnas originales: FCO, RPJ, Ejercicio, Moneda.

- Python: `groups['FCO'].transform(lambda s: s.shift(1).rolling(3, min_periods=3).std())`.

- Faltantes: Los tres valores previos deben estar observados; cualquier NaN invalida la ventana.

- Ceros/dominio: No hay denominador financiero; ceros y flujos negativos son válidos. Desviación muestral ddof=1 (divide por 3-1).

- Continuidad/moneda: Requiere t-3, t-2 y t-1 contiguos en la misma empresa y moneda; excluye t.

- Validación: 3013 observados, 1208 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## cambio_FCL_preliminar_activo_previo


- Definición: Cambio de efectivo relativo al tamaño anterior; admite flujos negativos.

- Fórmula: (FCL_preliminar(t)-FCL_preliminar(t-1))/ActivoTotal(t-1); FCL fuente invalidado si CAPEX de su año > 0.

- Unidad: adimensional.

- Columnas originales: FCL_preliminar, ActivoTotal, RPJ, Ejercicio, Moneda, CAPEX_reportado.

- Python: `divide(d['FCL_preliminar'] - groups['FCL_preliminar'].shift(1), groups.ActivoTotal.shift(1))`.

- Faltantes: Propaga NaN; no imputa. Numerador cero se conserva. Todas las derivaciones usan FCL validado: NaN cuando CAPEX de su año > 0; no altera FCL fuente.

- Ceros/dominio: Denominador > 0; cero, negativo o faltante produce NaN; infinito se convierte en NaN.

- Continuidad/moneda: Requiere t-1 exacto en el mismo segmento anual de empresa y moneda.

- Validación: 3456 observados, 765 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## FCL_preliminar_lag1


- Definición: Persistencia histórica por empresa y segmento.

- Fórmula: FCL_preliminar(t-1); FCL fuente invalidado si CAPEX de su año > 0.

- Unidad: unidad monetaria reportada, escala no acreditada.

- Columnas originales: FCL_preliminar, RPJ, Ejercicio, Moneda, CAPEX_reportado.

- Python: `groups['FCL_preliminar'].shift(1)`.

- Faltantes: NaN si falta el valor desplazado o la historia suficiente; sin imputación. Todas las derivaciones usan FCL validado: NaN cuando CAPEX de su año > 0; no altera FCL fuente.

- Ceros/dominio: No hay denominador financiero; ceros y flujos negativos son válidos.

- Continuidad/moneda: Requiere 1 filas anuales anteriores del mismo segmento, sin huecos ni cambios de moneda.

- Validación: 3506 observados, 715 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## FCL_preliminar_lag2


- Definición: Persistencia histórica por empresa y segmento.

- Fórmula: FCL_preliminar(t-2); FCL fuente invalidado si CAPEX de su año > 0.

- Unidad: unidad monetaria reportada, escala no acreditada.

- Columnas originales: FCL_preliminar, RPJ, Ejercicio, Moneda, CAPEX_reportado.

- Python: `groups['FCL_preliminar'].shift(2)`.

- Faltantes: NaN si falta el valor desplazado o la historia suficiente; sin imputación. Todas las derivaciones usan FCL validado: NaN cuando CAPEX de su año > 0; no altera FCL fuente.

- Ceros/dominio: No hay denominador financiero; ceros y flujos negativos son válidos.

- Continuidad/moneda: Requiere 2 filas anuales anteriores del mismo segmento, sin huecos ni cambios de moneda.

- Validación: 3169 observados, 1052 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## FCL_preliminar_lag3


- Definición: Persistencia histórica por empresa y segmento.

- Fórmula: FCL_preliminar(t-3); FCL fuente invalidado si CAPEX de su año > 0.

- Unidad: unidad monetaria reportada, escala no acreditada.

- Columnas originales: FCL_preliminar, RPJ, Ejercicio, Moneda, CAPEX_reportado.

- Python: `groups['FCL_preliminar'].shift(3)`.

- Faltantes: NaN si falta el valor desplazado o la historia suficiente; sin imputación. Todas las derivaciones usan FCL validado: NaN cuando CAPEX de su año > 0; no altera FCL fuente.

- Ceros/dominio: No hay denominador financiero; ceros y flujos negativos son válidos.

- Continuidad/moneda: Requiere 3 filas anuales anteriores del mismo segmento, sin huecos ni cambios de moneda.

- Validación: 2854 observados, 1367 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## FCL_preliminar_mean3_previa


- Definición: Nivel o volatilidad de tres años estrictamente anteriores; redundante exacta: excluir del subconjunto lineal de 19.

- Fórmula: mean de FCL_preliminar(t-3), FCL_preliminar(t-2), FCL_preliminar(t-1); FCL fuente invalidado si CAPEX de su año > 0.

- Unidad: unidad monetaria reportada, escala no acreditada.

- Columnas originales: FCL_preliminar, RPJ, Ejercicio, Moneda, CAPEX_reportado.

- Python: `groups['FCL_preliminar'].transform(lambda s: s.shift(1).rolling(3, min_periods=3).mean())`.

- Faltantes: Los tres valores previos deben estar observados; cualquier NaN invalida la ventana. Todas las derivaciones usan FCL validado: NaN cuando CAPEX de su año > 0; no altera FCL fuente.

- Ceros/dominio: No hay denominador financiero; ceros y flujos negativos son válidos.

- Continuidad/moneda: Requiere t-3, t-2 y t-1 contiguos en la misma empresa y moneda; excluye t.

- Validación: 2766 observados, 1455 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## FCL_preliminar_std3_previa


- Definición: Nivel o volatilidad de tres años estrictamente anteriores.

- Fórmula: std de FCL_preliminar(t-3), FCL_preliminar(t-2), FCL_preliminar(t-1); ddof=1; FCL fuente invalidado si CAPEX de su año > 0.

- Unidad: unidad monetaria reportada, escala no acreditada.

- Columnas originales: FCL_preliminar, RPJ, Ejercicio, Moneda, CAPEX_reportado.

- Python: `groups['FCL_preliminar'].transform(lambda s: s.shift(1).rolling(3, min_periods=3).std())`.

- Faltantes: Los tres valores previos deben estar observados; cualquier NaN invalida la ventana. Todas las derivaciones usan FCL validado: NaN cuando CAPEX de su año > 0; no altera FCL fuente.

- Ceros/dominio: No hay denominador financiero; ceros y flujos negativos son válidos. Desviación muestral ddof=1 (divide por 3-1).

- Continuidad/moneda: Requiere t-3, t-2 y t-1 contiguos en la misma empresa y moneda; excluye t.

- Validación: 2766 observados, 1455 NaN, 0 infinitos; todas las filas y NaN coinciden con el CSV.


## FCL_preliminar (fuente y objetivo contemporáneo)


`FCL_preliminar = FCO + CAPEX_reportado`, respetando el signo original de CAPEX. No es FCFF económicamente validado. Se verifica la identidad exacta en las 3898 filas con los tres componentes observados.


El constructor conserva la columna fuente, incluidos sus NaN; no reconstruye ni rellena FCL. Una suma con componente faltante no permitiría calcular un nuevo FCL. Para derivaciones y objetivo futuro, usa `raw.FCL_preliminar.where(~raw.CAPEX_reportado.gt(0))`: CAPEX positivo invalida; CAPEX faltante no activa esa bandera (limitación explícita).


No hay denominador. Cero y flujos negativos son válidos; se conserva moneda de la fila. Código de extracción histórica de FCO/CAPEX, filtros y revisiones ausente; no se presenta este control aritmético como prueba de origen.


## objetivo_fcl_t1


Etiqueta: FCL validado de la misma empresa en el año calendario exacto t+1, sin imputar. Se copia `(RPJ, Ejercicio, Moneda, FCL_validado)`, se resta 1 a Ejercicio y se une por RPJ/ejercicio (`left`, `validate="one_to_one"`). Nunca se usa la siguiente fila como sustituto del siguiente año.


Si falta t+1 o su FCL, la etiqueta es NaN. No tiene denominador; cero y valores negativos son válidos. Si cambia moneda, se conserva la etiqueta reportada y `moneda_objetivo`, pero `objetivo_moneda_consistente=False` y `utilizable_supervisado=False`. No se convierte moneda. CAPEX positivo en t+1 invalida su etiqueta.


`anio_objetivo = Ejercicio + 1`. Elegibilidad exige etiqueta observada y moneda consistente. Entrenamiento: año objetivo <=2021; prueba: 2022–2025; resto sin etiqueta elegible. Objetivo y controles futuros se excluyen de X.


Validación: 3607 etiquetas observadas; 614 NaN; 3560 elegibles. Pruebas: unión anual exacta, cambios de moneda, faltantes y CAPEX positivo; coincidencia completa de la etiqueta exportada.
