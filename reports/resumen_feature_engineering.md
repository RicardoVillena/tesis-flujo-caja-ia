# Semana 5 — Resultados de Feature Engineering

| indicador | valor |
| --- | --- |
| registros_entrada | 4221 |
| registros_exportados | 4221 |
| columnas_entrada | 23 |
| columnas_exportadas | 57 |
| empresas_observadas | 336 |
| anio_min | 2005 |
| anio_max | 2025 |
| predictores | 22 |
| fcl_actual_disponible | 3898 |
| registros_elegibles | 3560 |
| empresas_elegibles | 309 |
| casos_completos_elegibles | 2251 |
| train | 2869 |
| test | 691 |
| sin_etiqueta_elegible | 661 |
| pruebas_unitarias | 11 |

## Diseño y ejecución

Objetivo: FCL_preliminar(t+1), aproximación FCO + CAPEX reportado con signo, no FCFF validado. 22 predictores: 8 ratios, 4 variaciones, 6 rezagos y 4 estadísticas móviles. Se preservan filas, ceros y faltantes; no se imputan objetivos. Entrenamiento por año objetivo hasta 2021; prueba 2022–2025. Imputación mediana y RobustScaler en Pipeline ilustrativos por moneda ajustados solo en entrenamiento; CSV sin imputar ni escalar. No se entrenaron modelos.

| moneda | train | test | columnas_preparadas | celdas_extremas_train | IQR_crecimiento_activos_robusto |
| --- | --- | --- | --- | --- | --- |
| Dólares | 353 | 92 | 22 | 565 | 1.0 |
| Soles | 2516 | 599 | 22 | 5431 | 1.0 |

Disponibilidad de predictores en toda la exportación:

| predictor | disponibles |
| --- | --- |
| pasivo_activo | 4221 |
| margen_neto | 3950 |
| rentabilidad_activo_cierre | 4221 |
| rotacion_activo_cierre | 3950 |
| fco_activo | 4131 |
| fco_ingresos | 3865 |
| inversion_capex_activo | 3952 |
| fcl_activo | 3898 |
| crecimiento_ActivoTotal | 3822 |
| crecimiento_TotalIngreso | 3568 |
| cambio_FCO_activo_previo | 3701 |
| FCO_lag1 | 3734 |
| FCO_lag2 | 3392 |
| FCO_lag3 | 3073 |
| FCO_mean3_previa | 3013 |
| FCO_std3_previa | 3013 |
| cambio_FCL_preliminar_activo_previo | 3456 |
| FCL_preliminar_lag1 | 3506 |
| FCL_preliminar_lag2 | 3169 |
| FCL_preliminar_lag3 | 2854 |
| FCL_preliminar_mean3_previa | 2766 |
| FCL_preliminar_std3_previa | 2766 |

## Validación y límites

Se ejecutaron 11 pruebas unitarias sin fallos ni errores y aserciones sobre el panel y la exportación. La ejecución del notebook se comprueba adicionalmente mediante nbclient. La invariancia ante cambios futuros prueba el cálculo, no la disponibilidad histórica de la fuente. Faltan fechas de publicación, vintages de revisión, escala monetaria acreditada y validación de códigos FCO/CAPEX. Antes del modelado se debe purgar la frontera temporal usando fechas reales de publicación. No se mezclan monedas ni se usan tipos de cambio inventados. No hay ajuste por inflación. La moneda futura solo define elegibilidad retrospectiva. Panel desbalanceado: máximo 21 años por empresa, insuficiente para justificar por sí solo redes recurrentes y sin observaciones para estacionalidad intraanual. Sectores financieros requieren validación económica independiente. El Excel no se integró por falta de homologación.

## Reproducción

Entorno tesis-fcl, Python 3.12.x (ejecución verificada en 3.12.15). Dependencias en requirements-feature-engineering.txt. Ejecutar desde la raíz: `python -m unittest discover -s tests -v`; después ejecutar todas las celdas de notebooks/02_feature_engineering.ipynb con el kernel tesis-fcl, o ejecutar `python scripts/execute_feature_engineering.py`. El notebook genera únicamente los derivados autorizados; no ejecuta la ingesta ni instala paquetes.



## Correcciones Antigravity y diagnósticos

Se conservan 22 características y se define un subconjunto de 19 sin las tres redundancias lineales exactas. Las identidades se verifican solo en entrenamiento; las dependencias DuPont son multiplicativas. Los casos completos se usan únicamente en diagnósticos; queda prohibido descartar filas mediante dropna sobre predictores en modelado. La inferencia Mann-Whitney es exploratoria: observaciones de una empresa no son independientes. RobustScaler preserva la escala intercuartílica, pero no elimina ni acota extremos. Las versiones normalizadas por ActivoTotal(t) son una sensibilidad en memoria, no nuevos predictores exportados ni un cambio del objetivo principal. La reconstrucción monetaria requiere activos y moneda de origen. La bandera revision_interanual permite estratificar, pero no demuestra por sí sola fecha o causa de una reexpresión; tampoco su ausencia garantiza datos point-in-time. La Semana 6 deberá comparar resultados por esta bandera y por moneda, auditando también las fuentes históricas de los rezagos. La imputación y el escalado deben clonarse y ajustarse dentro de cada pliegue temporal por moneda.

### Rango: solo entrenamiento completo

| moneda | conjunto | filas | columnas | rango |
| --- | --- | --- | --- | --- |
| Dólares | original_22 | 176 | 22 | 19 |
| Dólares | reducido_19 | 176 | 19 | 19 |
| Soles | original_22 | 1498 | 22 | 19 |
| Soles | reducido_19 | 1498 | 19 | 19 |

### VIF por predictor, solo entrenamiento

| moneda | conjunto | predictor | VIF |
| --- | --- | --- | --- |
| Dólares | original_22 | pasivo_activo | 1.4255337876074803 |
| Dólares | original_22 | margen_neto | 2.9492476811433894 |
| Dólares | original_22 | rentabilidad_activo_cierre | 3.4829528760547337 |
| Dólares | original_22 | rotacion_activo_cierre | 1.4598996531572896 |
| Dólares | original_22 | fco_activo | inf |
| Dólares | original_22 | fco_ingresos | 2.2229872155477794 |
| Dólares | original_22 | inversion_capex_activo | inf |
| Dólares | original_22 | fcl_activo | inf |
| Dólares | original_22 | crecimiento_ActivoTotal | 1.3536590786395648 |
| Dólares | original_22 | crecimiento_TotalIngreso | 1.3076704007211688 |
| Dólares | original_22 | cambio_FCO_activo_previo | 12.353068320415428 |
| Dólares | original_22 | FCO_lag1 | inf |
| Dólares | original_22 | FCO_lag2 | inf |
| Dólares | original_22 | FCO_lag3 | inf |
| Dólares | original_22 | FCO_mean3_previa | inf |
| Dólares | original_22 | FCO_std3_previa | 10.449021698015288 |
| Dólares | original_22 | cambio_FCL_preliminar_activo_previo | 13.440508310117808 |
| Dólares | original_22 | FCL_preliminar_lag1 | inf |
| Dólares | original_22 | FCL_preliminar_lag2 | inf |
| Dólares | original_22 | FCL_preliminar_lag3 | inf |
| Dólares | original_22 | FCL_preliminar_mean3_previa | inf |
| Dólares | original_22 | FCL_preliminar_std3_previa | 12.880885529720853 |
| Dólares | reducido_19 | pasivo_activo | 1.4255337876074805 |
| Dólares | reducido_19 | margen_neto | 2.9492476811433894 |
| Dólares | reducido_19 | rentabilidad_activo_cierre | 3.482952876054735 |
| Dólares | reducido_19 | rotacion_activo_cierre | 1.4598996531572894 |
| Dólares | reducido_19 | fco_activo | 2.745926319675634 |
| Dólares | reducido_19 | fco_ingresos | 2.22298721554778 |
| Dólares | reducido_19 | inversion_capex_activo | 2.1716631829051343 |
| Dólares | reducido_19 | crecimiento_ActivoTotal | 1.3536590786395646 |
| Dólares | reducido_19 | crecimiento_TotalIngreso | 1.3076704007211688 |
| Dólares | reducido_19 | cambio_FCO_activo_previo | 12.353068320415428 |
| Dólares | reducido_19 | FCO_lag1 | 13.728349972035973 |
| Dólares | reducido_19 | FCO_lag2 | 14.187349095833627 |
| Dólares | reducido_19 | FCO_lag3 | 19.44675768545094 |
| Dólares | reducido_19 | FCO_std3_previa | 10.449021698015292 |
| Dólares | reducido_19 | cambio_FCL_preliminar_activo_previo | 13.440508310117808 |
| Dólares | reducido_19 | FCL_preliminar_lag1 | 6.349243642628301 |
| Dólares | reducido_19 | FCL_preliminar_lag2 | 9.825391476918774 |
| Dólares | reducido_19 | FCL_preliminar_lag3 | 15.991446526652556 |
| Dólares | reducido_19 | FCL_preliminar_std3_previa | 12.880885529720853 |
| Soles | original_22 | pasivo_activo | 1.1904403434796043 |
| Soles | original_22 | margen_neto | 6.421831926912425 |
| Soles | original_22 | rentabilidad_activo_cierre | 1.7951247797434726 |
| Soles | original_22 | rotacion_activo_cierre | 1.4050677194919916 |
| Soles | original_22 | fco_activo | inf |
| Soles | original_22 | fco_ingresos | 6.36111915734027 |
| Soles | original_22 | inversion_capex_activo | inf |
| Soles | original_22 | fcl_activo | inf |
| Soles | original_22 | crecimiento_ActivoTotal | 1.1726750961002037 |
| Soles | original_22 | crecimiento_TotalIngreso | 1.0093358089602957 |
| Soles | original_22 | cambio_FCO_activo_previo | 14.708568290800674 |
| Soles | original_22 | FCO_lag1 | inf |
| Soles | original_22 | FCO_lag2 | inf |
| Soles | original_22 | FCO_lag3 | inf |
| Soles | original_22 | FCO_mean3_previa | inf |
| Soles | original_22 | FCO_std3_previa | 110.4750721513892 |
| Soles | original_22 | cambio_FCL_preliminar_activo_previo | 15.08190797334256 |
| Soles | original_22 | FCL_preliminar_lag1 | inf |
| Soles | original_22 | FCL_preliminar_lag2 | inf |
| Soles | original_22 | FCL_preliminar_lag3 | inf |
| Soles | original_22 | FCL_preliminar_mean3_previa | inf |
| Soles | original_22 | FCL_preliminar_std3_previa | 110.3291049628177 |
| Soles | reducido_19 | pasivo_activo | 1.190440343479604 |
| Soles | reducido_19 | margen_neto | 6.421831926912425 |
| Soles | reducido_19 | rentabilidad_activo_cierre | 1.7951247797434728 |
| Soles | reducido_19 | rotacion_activo_cierre | 1.4050677194919918 |
| Soles | reducido_19 | fco_activo | 2.6964217401363655 |
| Soles | reducido_19 | fco_ingresos | 6.361119157340268 |
| Soles | reducido_19 | inversion_capex_activo | 2.177293111800355 |
| Soles | reducido_19 | crecimiento_ActivoTotal | 1.172675096100204 |
| Soles | reducido_19 | crecimiento_TotalIngreso | 1.0093358089602957 |
| Soles | reducido_19 | cambio_FCO_activo_previo | 14.70856829080067 |
| Soles | reducido_19 | FCO_lag1 | 54.41725154757407 |
| Soles | reducido_19 | FCO_lag2 | 97.59638706889109 |
| Soles | reducido_19 | FCO_lag3 | 76.06139087500304 |
| Soles | reducido_19 | FCO_std3_previa | 110.4750721513892 |
| Soles | reducido_19 | cambio_FCL_preliminar_activo_previo | 15.081907973342561 |
| Soles | reducido_19 | FCL_preliminar_lag1 | 47.142814907575975 |
| Soles | reducido_19 | FCL_preliminar_lag2 | 83.83470588064345 |
| Soles | reducido_19 | FCL_preliminar_lag3 | 65.56412920348846 |
| Soles | reducido_19 | FCL_preliminar_std3_previa | 110.3291049628177 |

### Casos completos versus incompletos

| Moneda | caso_completo | registros | empresas | activo_mediano | historial_mediano | ingresos_no_positivos |
| --- | --- | --- | --- | --- | --- | --- |
| Dólares | False | 200 | 51 | 296382.5 | 1.0 | 38 |
| Dólares | True | 245 | 30 | 717540.0 | 8.0 | 0 |
| Soles | False | 1109 | 275 | 320575.0 | 2.0 | 185 |
| Soles | True | 2006 | 216 | 585942.5 | 10.0 | 0 |

### Mann-Whitney por moneda (completos frente a incompletos)

| moneda | completos | incompletos | U | p_exploratorio |
| --- | --- | --- | --- | --- |
| Dólares | 245 | 200 | 32093.0 | 1.8429462490148043e-08 |
| Soles | 2006 | 1109 | 1370249.0 | 7.264817557675887e-27 |

### Revisión interanual: estratificación, sin entrenar

| particion | Moneda | revision_interanual | registros | empresas | proporcion_en_particion_moneda |
| --- | --- | --- | --- | --- | --- |
| entrenamiento | Dólares | False | 229 | 48 | 0.6487252124645893 |
| entrenamiento | Dólares | True | 124 | 39 | 0.35127478753541075 |
| entrenamiento | Soles | False | 1634 | 257 | 0.6494435612082671 |
| entrenamiento | Soles | True | 882 | 240 | 0.3505564387917329 |
| prueba | Dólares | False | 74 | 25 | 0.8043478260869565 |
| prueba | Dólares | True | 18 | 13 | 0.1956521739130435 |
| prueba | Soles | False | 472 | 156 | 0.7879799666110183 |
| prueba | Soles | True | 127 | 84 | 0.21202003338898165 |

### Disponibilidad por año origen

| Ejercicio | elegibles | completos |
| --- | --- | --- |
| 2005 | 147 | 0 |
| 2006 | 160 | 0 |
| 2007 | 164 | 0 |
| 2008 | 170 | 113 |
| 2009 | 151 | 115 |
| 2010 | 142 | 105 |
| 2011 | 168 | 103 |
| 2012 | 207 | 105 |
| 2013 | 204 | 107 |
| 2014 | 207 | 115 |
| 2015 | 201 | 135 |
| 2016 | 198 | 159 |
| 2017 | 194 | 159 |
| 2018 | 188 | 153 |
| 2019 | 185 | 153 |
| 2020 | 183 | 152 |
| 2021 | 174 | 147 |
| 2022 | 175 | 145 |
| 2023 | 174 | 146 |
| 2024 | 168 | 139 |

Subconjunto recomendado de 19: `pasivo_activo`, `margen_neto`, `rentabilidad_activo_cierre`, `rotacion_activo_cierre`, `fco_activo`, `fco_ingresos`, `inversion_capex_activo`, `crecimiento_ActivoTotal`, `crecimiento_TotalIngreso`, `cambio_FCO_activo_previo`, `FCO_lag1`, `FCO_lag2`, `FCO_lag3`, `FCO_std3_previa`, `cambio_FCL_preliminar_activo_previo`, `FCL_preliminar_lag1`, `FCL_preliminar_lag2`, `FCL_preliminar_lag3`, `FCL_preliminar_std3_previa`.
SHA256 del CSV fuente: `5e27fa02d209b571c4e4e5da26137d6f12a3d7b8c2c1125f6de2d982a6ac8008`.
