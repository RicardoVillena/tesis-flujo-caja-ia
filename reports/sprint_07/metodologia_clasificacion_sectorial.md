# Sprint 07 — Auditoría y clasificación sectorial

## Alcance y fuentes

Se examinaron los notebooks 07_baseline_variantes, 08_mejoras_baseline y los módulos de ingeniería financiera e ingestión SMV. La ingeniería existente define la elegibilidad; este sprint utiliza sus columnas publicadas, sin recalcular predictores ni entrenar modelos. El notebook solicitado 08_clasificacion_sectorial coexiste con 08_mejoras_baseline; no lo sustituye.

El panel financiero original es `data/processed/panel_fcl_preliminar.csv`; sus derivados son `features_financieras.csv`, `panel_financiero_macroeconomico.csv` y `panel_financiero_macro_bursatil.csv`. Este último aporta 4.221 filas, 336 RPJ y 68 columnas, con ejercicios 2005–2025. Las claves comprobadas son RPJ y Ejercicio; RUC y NombreEmpresa describen identidad, TipoSector el sector SMV, CIIU la actividad y Moneda la moneda reportada.

La referencia es [Damodaran, Betas by Sector (US), January 2026](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/Betas.html), consultada el 23 de octubre de 2026. Se conserva HTML original, SHA-256, metadatos y un vocabulario de 94 industrias, excluyendo las dos filas de mercado total. El vocabulario se usa sin traducir ni corregir sus nombres. No se utilizan betas ni se afirma que exista una equivalencia oficial NYU–CIIU–SMV. La jerarquía y las correspondencias son propuestas analíticas del proyecto, versión sprint07-v1.

## Reglas trazables

M01 agrupa el TipoSector observado: bancos, financieras, seguros y AFP en Financiero; agrícolas en Agroindustrial; mineras en Extractivo; industriales en Industrial; servicios públicos en Servicios públicos. DIVERSOS e INDUSTRIALES DEL TRABAJO quedan con macrosector pendiente. Estas agrupaciones no resuelven la industria. Cada fila conserva sector SMV y CIIU originales.

D01 asigna A.F.P. a `Investments & Asset Management` por administración de fondos previsionales, actividad sustentada por la [SBS](https://www.sbs.gob.pe/sistema-privado-de-pensiones/temas-de-interes-del-spp/fondo-de-pensiones). Es una correspondencia conceptual del proyecto, no una asignación empresarial publicada por Damodaran.

D02 asigna CIIU normalizado 5510 dentro de DIVERSOS a `Hotel/Gaming`, sector propuesto Alojamiento y macrosector Servicios de consumo (M02). Su alcance de alojamiento es compatible en [ISIC 3.1](https://unstats.un.org/unsd/classifications/Econ/Structure/Detail/EN/17/5510) e [ISIC 4](https://unstats.un.org/unsd/classifications/Econ/Structure/Detail/EN/27/5510). La regla no supone que las empresas desarrollen juegos de azar.

P01 deja pendiente CIIU ausente y sector insuficiente. P02 deja pendiente CIIU con revisión no declarada o correspondencia no unívoca. P03 bloquea asignaciones automáticas si un RPJ tiene múltiples sectores o múltiples RUC. Las candidatas para bancos, seguros y minería orientan revisión; no son asignaciones. MINERAS no permite distinguir metales preciosos, otros metales y carbón; BANCOS no distingue Money Center de Regional; SEGUROS no identifica ramo o reaseguro. No se fuerza `Diversified` a partir de DIVERSOS.

No se usa NombreEmpresa para clasificar. La normalización auxiliar quita `.0` y recupera cuatro posiciones sin cambiar CIIU. El panel integrado serializa CIIU como decimal y pierde ceros iniciales respecto al financiero original; la comparación entre fuentes normaliza solo esta representación. La unión conserva exactamente las 68 columnas del panel integrado.

## Evidencia y cobertura parcial

El CIIU está ausente en 3.872 registros y presente en 349: uno de 2023, 176 de 2024 y 172 de 2025. No se extrapolan códigos recientes al pasado ni se interpreta ausencia de códigos como ausencia de actividad. No se conoce la revisión CIIU de origen: otras reglas requieren verificar edición, actividad principal y posibles cambios de negocio con evidencia empresarial.

Las reglas actuales identifican 7 empresas con alguna observación clasificada, 6 completamente clasificadas y 2 industrias. Hay 330 empresas con registros pendientes; una empresa aparece tanto entre las clasificadas parcialmente como entre las pendientes. `empresas_clasificacion.csv` distingue estos conceptos. `casos_pendientes.csv` conserva una fila por empresa-año pendiente, sin inventar una clasificación empresarial estable.

Los resultados limitados son una consecuencia deliberada de la evidencia disponible. No equivalen a una clasificación exhaustiva del universo. Las filas pendientes se muestran como categoría analítica separada en tablas y gráficos; no constituyen una industria Damodaran.

## Estadística y particiones

La elegibilidad es `objetivo_fcl_t1.notna() & Moneda.eq(moneda_objetivo)`, contrastada contra `utilizable_supervisado`. Se preservan 3.560 casos y 309 empresas: 2.869 de entrenamiento y 691 de prueba. Las claves y particiones se contrastan con las predicciones E0 principales existentes, sin ejecutar el modelo. El corte depende del año objetivo: entrenamiento hasta 2021, prueba 2022–2025; Ejercicio es el año de las variables contemporáneas.

La estadística descriptiva usa FCL_preliminar contemporáneo del panel completo, por industria y moneda. No se confunde con objetivo_fcl_t1. Se reportan mediana, desviación estándar muestral, asimetría muestral, RIQ y conteo fuera de Q1−1,5×RIQ/Q3+1,5×RIQ. Los grupos pequeños pueden producir estadísticos indefinidos y se conservan vacíos. RIQ cero se aplica literalmente. El porcentaje faltante usa como denominador todas las filas del grupo y la participación usa las 4.221 filas. Las participaciones separadas por moneda suman la participación industrial; los conteos de empresas por grupo no son aditivos.

La señal de baja representación es orientativa: menos de 5 empresas, 30 registros elegibles de entrenamiento o 10 de prueba, por industria-moneda. No excluye registros ni acredita suficiencia predictiva si se supera. No se ajustan reglas ni umbrales con resultados de prueba. La visualización usa seis PNG y separa monedas al representar FCL; el eje symlog facilita ver extremos sin recortarlos. Se conserva la etiqueta original `D lares`.

## Integridad y reproducción

Ejecutar desde la raíz con el entorno existente, sin instalar dependencias:

```bash
conda run -n tesis-fcl python scripts/reproduce_clasificacion_sectorial.py
conda run -n tesis-fcl python -m unittest discover -s tests -p 'test_clasificacion_sectorial.py' -v
```

El notebook llama al mismo módulo. Los CSV y el JSON son deterministas con entradas congeladas. Las pruebas contrastan bytes contra una ejecución en directorio temporal; los gráficos se regeneran, pero no se exige igualdad binaria de PNG entre versiones de Matplotlib. La auditoría incluye hashes de paneles, bases XLSX, notebooks anteriores y resultados Sprint 06. Los tests incluyen duplicados, pérdidas, conflictos de identidad, nombres irrelevantes, industria oficial y falta de propagación temporal. No se modifica main ni se realizan commit, push o PR.

## Límites y siguiente sprint

FCL es una aproximación contable, no FCFF acreditado; la escala monetaria entre emisores no está verificada y no se mezclan monedas. El flujo bancario o asegurador requiere un tratamiento económico específico. La clasificación de referencia de 2026 es retrospectiva y no constituye taxonomía disponible históricamente ni garantiza comparabilidad internacional. Los cambios de CIIU pueden reflejar migración de revisión, no cambio económico; múltiples nombres/RUC son señales para revisar, no errores demostrados.

Para el siguiente sprint se propone separar banca, seguros, otras financieras y AFP; en no financieras, evaluar agroindustria, industria, extracción y servicios públicos, manteniendo DIVERSOS en revisión. Antes de modelos intrasectoriales se debe validar la revisión CIIU y documentar actividad principal por emisor, ramo asegurador y subindustria minera. No agrupar automáticamente pendientes ni industrias pequeñas; considerar agrupación por macrosector o modelos con información compartida solo tras resolver la taxonomía y examinar tamaños de entrenamiento por moneda. Cualquier selección predictiva debe usar validación temporal dentro de entrenamiento y una evaluación futura independiente.
