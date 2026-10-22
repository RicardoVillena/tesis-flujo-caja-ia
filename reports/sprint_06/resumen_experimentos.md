Sprint 6: Ridge Baseline y variantes

3560 observaciones: 2869 entrenamiento y 691 prueba. Se preservan 309 empresas elegibles y las particiones.
19/23/26 predictores; alpha=1.0. Mediana + StandardScaler ajustados solo con entrenamiento. Modelos separados por moneda; unidades reportadas, escala no acreditada.

Resultados principales de prueba:

moneda | experimento | n | MAE | RMSE | R2 | error medio
--- | --- | --- | --- | --- | --- | ---
D lares | E0_financiero | 92 | 228054.3656 | 804755.4557 | -2.030466 | 95644.0230
D lares | E1_macroeconomico | 92 | 317991.4029 | 1343050.2916 | -7.440459 | 247181.6748
D lares | E2_bursatil | 92 | 237509.5735 | 759493.1253 | -1.699164 | 136772.5790
Soles | E0_financiero | 599 | 379977.4371 | 1424709.0675 | -1.490134 | 157975.7289
Soles | E1_macroeconomico | 599 | 442301.8671 | 1445744.7461 | -1.564210 | 209324.9153
Soles | E2_bursatil | 599 | 426780.0103 | 1438296.5594 | -1.537858 | 205267.8683

Menor error por moneda y criterio:
D lares: MAE, E0_financiero, 228054.3656.
D lares: RMSE, E2_bursatil, 759493.1253.
Soles: MAE, E0_financiero, 379977.4371.
Soles: RMSE, E0_financiero, 1424709.0675.

Sensibilidades: externos t-1 y RobustScaler, mismos casos y Ridge; resultados completos en comparacion_variantes.csv. Mejora porcentual positiva significa reduccion del error respecto a E0; denominador cero queda vacio.

Limites:
Objetivo: FCO + CAPEX reportado en t+1; FCL preliminar, no FCFF validado. Linaje historico detallado de FCO/CAPEX y escala monetaria no acreditados.
La etiqueta de moneda de dolares aparece como 'D lares' en el original. Se conserva; no se convierten monedas ni se agregan errores monetarios entre ellas.
Dentro de cada moneda no se certifica homogeneidad de escala entre emisores; los valores absolutos y extremos pueden dominar MAE/RMSE. No se ajusta por tamaño ni se convierte el objetivo en ratio en esta entrega.
No hay fechas efectivas de prediccion/publicacion ni vintages historicos de estados financieros o agregados. Las tres variantes principales son retrospectivas y condicionadas a disponibilidad; no se certifica backtest point-in-time.
La sensibilidad externa t-1 mitiga simultaneidad, pero no elimina revisiones ni acredita disponibilidad del PBI u otros datos. La base externa 2004 incompleta se imputa solo con entrenamiento; no se descartan casos.
Las particiones se conservan por anio_objetivo: entrenamiento hasta 2021 y prueba 2022–2025; no se optimizan alpha ni transformaciones con prueba. No hay validacion cruzada o estimacion de incertidumbre en esta etapa.
Hay solo 16 años externos de entrenamiento y cuatro de prueba, con dependencia entre observaciones de una empresa. No se afirma significancia de diferencias ni superioridad generalizable.
Bursatil: transicion metodologica de mayo 2015, discrepancias entre frecuencias y calendario diario no certificado; se conserva la definicion publicada, sin factores de correccion aprendidos.
RobustScaler es sensibilidad predefinida de la penalizacion; no se usa prueba para sustituir la configuracion principal. No se eliminan ni winsorizan extremos.
Los ratios/rezagos de FCL hasta t no usan la etiqueta t+1, pero sus fuentes pueden estar reexpresadas. Las revisiones no se resuelven mediante una verificacion algebraica.
