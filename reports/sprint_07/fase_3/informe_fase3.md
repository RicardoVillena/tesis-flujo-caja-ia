# Sprint 07 — Fase 3: corrección y ampliación sectorial

Rama local `sprint-07-clasificacion-sectorial`. Catálogo: 336 empresas, 4221 observaciones empresa-año. No se entrenaron modelos, modificaron FCL, variables financieras, división temporal ni datos originales; no se realizó commit, push, PR ni cambios en main.

## Resultado comparativo

| Indicador | Fase 2 congelada | Fase 3 |
|---|---:|---:|
| Empresas con alguna observación clasificada | 49 | 58 |
| Empresas completamente clasificadas | 12 | 13 |
| Empresas parcialmente clasificadas | 37 | 45 |
| Empresas sin clasificación | 287 | 278 |
| Observaciones clasificadas | 442 | 463 |
| Observaciones pendientes | 3779 | 3758 |
| Industrias representadas | 13 | 16 |

Se agregaron 21 observaciones en 12 empresas, conservando las 442 asignaciones de Fase 2. La cobertura continúa limitada: 10.97% de las observaciones y 17.26% de las empresas tienen alguna clasificación. Las empresas parcialmente clasificadas conservan sus años pendientes: no se certifica toda su historia.

`comparacion_elegibilidad.csv` separa entrenamiento/prueba de la cobertura total; `observaciones_nuevas.csv` identifica cada incorporación. No se utilizaron resultados de modelos, FCL ni métricas predictivas para priorizar.

## Cinco correcciones auditadas

1. **D04: inversión y actividad separadas.** Cero, vacío y valores no positivos no acreditan ausencia de operación. Se conserva la regla previamente aceptada de inversión positiva como indicio sectorial condicionado al sector SMV; D03 aporta evidencia empresarial independiente. Hidrandina 2015, Piura 2021–2022 y REP 2022 ahora cuentan con pasajes de actividad del ejercicio. `revision_actividad_inversion.csv` conserva todos los localizadores, estado de inversión, estado de actividad y respaldo final; `evidencias_estadisticas_empresa_anio.csv` conserva solo localizadores asignables por la regla original. No rellenar huecos automáticamente.
2. **Maestro documental.** Selección: vigencia en el último ejercicio del panel, certeza de actividad, jerarquía documental y año. Si no hay evidencia vigente, resume la referencia documental más reciente y la identifica explícitamente; no extiende esa actividad a años sin respaldo. Jerarquía: EEFF individual auditado 5, memoria 4, documento empresarial primario aún no normalizado 4, nota individual no auditada 3, descripción de entidad consolidada 2, estadística sectorial 1. Se rechazan industrias contradictorias de igual calidad/vigencia. ID y orden de filas no determinan calidad. El resumen incluye el ID seleccionado y el criterio; los cambios de redacción no crean falsos cambios económicos ni huecos.
3. **Hidrandina.** `correspondencia_minem_canonica.csv` contiene 24 RPJ únicos frente a 25 localizadores originales. Hidrandina conserva sus dos series y sus años de inversión positiva, incluida la historia anterior a 2005, dentro de un solo registro empresarial. Las cinco celdas de los cuatro huecos eléctricos incluyen dos localizadores de Hidrandina, no cinco observaciones. El archivo original se preserva.
4. **Notebook.** Ruta canónica `notebooks/sprint_07/10_clasificacion_sectorial.ipynb`; la ruta anterior `notebooks/08_clasificacion_sectorial.ipynb` es enlace simbólico de compatibilidad. El único notebook físico 08 de raíz sigue siendo `08_mejoras_baseline.ipynb`, sin modificar. `notebooks/README.md` documenta inventario y limitación del glob histórico del notebook 09. El notebook canónico fue ejecutado sin entrenamiento; ambas rutas leen el mismo archivo.
5. **Suficiencia.** Se mantienen umbrales originales por industria y moneda: al menos 5 RPJ, 30 observaciones elegibles de entrenamiento y 10 de prueba. Se agregan conteos de RPJ y años objetivo por partición, y una condición conservadora de 5 RPJ distintos en cada partición para recomendar experimentos. Repetir años de una empresa no crea empresas independientes. Los RPJ son entidades legales distintas: no prueban independencia económica entre miembros de un grupo.

## Ampliación y priorización

`priorizacion_inicial.csv` ordena todas las empresas con años pendientes de la Fase 2 por observaciones elegibles pendientes, presencia en ambas particiones y conteos train/test; `priorizacion_pendientes.csv` actualiza el orden tras la ampliación. Incluyen financieros; no se omiten bancos por el foco no financiero.

La investigación añadió 21 evidencias específicas de 16 empresas y conservó 22 PDF nuevos, además de intentos fallidos y portales. Se revisaron minería (Minsur y Buenaventura), construcción (Cosapi), manufactura (Yura, Siderperú, Creditex), retail (Supermercados Peruanos), agroindustria (Laredo, Cartavio, Casa Grande y Agrícola San Juan), transporte (TGP; Inca Rail pendiente de descarga), electricidad y publicaciones (El Comercio). La bitácora distingue documentos utilizables, fuentes sin asignación y accesos fallidos; Hermes se excluye porque el documento recuperado es de una clasificadora, no de la empresa. No se asignó por nombre ni por un resultado del buscador.

Las nuevas industrias representadas son Farming/Agriculture, Publishing & Newspapers y Retail (Grocery and Food). El incremento documental es deliberadamente acotado a los años acreditados; no elimina la insuficiencia de muestra de estos sectores.

Las fuentes primarias se conservan en `data/raw/sectorial_fase3/`: PDF, texto paginado, URL consultada/final, fecha, huellas SHA-256 y manifiesto de descarga. `evidencias_actividad.csv` incluye identidad RPJ/RUC, razón social documental, actividad, alcance temporal, página, extracto literal, certeza y clase documental. La validación comprueba entidad literal, pasaje en página, identidad exacta del panel, años y vocabulario de 94 industrias. Las memorias y EEFF comparativos acreditan solo períodos explícitos; las notas intermedias son fotografías intraanuales, no prueba de actividad durante cada día del año.

CIIU no se genera desde una actividad ni desde la industria. Se registran códigos explícitos de Cosapi (4390), Creditex (1311) y Agrícola San Juan (0121, 0114, 0122, 0111), separados del original. Laredo requiere cotejo de la llamada de nota que el extractor une al código. No se hizo consulta individual SUNAT: RUC válido significa control formal, no alta/estado registral ni actividad histórica acreditada por SUNAT. La taxonomía 2026 es un instrumento retrospectivo; esta entrega no certifica disponibilidad point-in-time.

## Industrias con muestra para experimentos posteriores

Solo **Power / Soles** supera ambos controles orientativos: 21 empresas del panel, 17 RPJ distintos y 203 filas elegibles en entrenamiento, 14 RPJ distintos y 50 filas en prueba. No se entrenó ningún modelo.

Investments & Asset Management / Soles supera el umbral original (63 filas train, 16 test), pero solo tiene 4 empresas en prueba; queda fuera de la recomendación ampliada. Además exige validación académica del FCL como objetivo financiero. Power en dólares y todas las demás combinaciones industria/moneda siguen con muestra insuficiente. No combinar monedas ni extender períodos para superar umbrales.

## Revisión académica y entrega a Antigravity

`revision_academica.csv` contiene identidades y acciones por caso: frontera minería polimetálica/metales preciosos, predominancia del estaño en Minsur, textiles, transporte por ductos sin etiqueta Midstream oficial, atribución matriz/subsidiarias, documentación inaccesible y CIIU. No se consideran asignaciones las categorías candidatas de revisión. Los 278 RPJ de `empresas_pendientes.csv` y los 45 de `empresas_parcialmente_clasificadas.csv` requieren ampliar documentación en sus ejercicios faltantes.

Auditoría independiente: contrastar fuente y página, vigencia y perímetro, comprobar los SHA-256 del JSON, y reproducir sin red. Fase 2 y sus fuentes permanecen congeladas y verificadas por huella antes de cada ejecución. Los controles de unión preservan exactamente todas las columnas financieras, FCL, elegibilidad y particiones.

## Validación y reproducción

- `python scripts/reproduce_enriquecimiento_sectorial.py`: reproduce catálogos Fase 3 sin red ni lector PDF.
- `python scripts/reporte_sectorial_fase3.py`: genera este informe y los anexos de auditoría.
- `python -m unittest discover -s tests -v`: **44 pruebas aprobadas**, 35 anteriores y 9 nuevas; registro en `pruebas_automatizadas.txt`.
- Notebook canónico: 15 celdas de código ejecutadas, sin errores ni entrenamiento.

Las pruebas cubren inversión cero/vacía, prioridad documental independiente del ID/orden, vigencia, deduplicación histórica, alias del notebook, número de empresas frente a filas, priorización elegible, estabilidad semántica y respaldo anual de toda ampliación. Se conservan las verificaciones anteriores de integridad, CIIU, conflictos y reproducibilidad exacta.
