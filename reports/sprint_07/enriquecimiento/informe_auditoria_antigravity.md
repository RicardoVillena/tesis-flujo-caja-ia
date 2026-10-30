# Sprint 07 — Corrección de cobertura: entrega para Antigravity

La ampliación conserva las 336 empresas y 4.221 observaciones. Añade 355 asignaciones respaldadas sin sustituir ninguna de las 87 anteriores. El resultado queda listo para revisión independiente; no constituye aprobación de Antigravity ni clasificación exhaustiva de todas las empresas.

| Indicador | Entrega anterior | Ampliación | Diferencia |
|---|---:|---:|---:|
| Empresas con alguna observación clasificada | 7 | 49 | +42 |
| Empresas con todas sus observaciones clasificadas | 6 | 12 | +6 |
| Empresas parcialmente clasificadas | 1 | 37 | +36 |
| Empresas sin observaciones clasificadas | 329 | 287 | −42 |
| Observaciones clasificadas | 87 | 442 | +355 |
| Observaciones pendientes | 4.134 | 3.779 | −355 |
| Industrias presentes en observaciones | 2 | 13 | +11 |

La cobertura de observaciones pasa de 2,06% a 10,47%; la de empresas con alguna asignación, de 2,08% a 14,58%. Los tres estados empresariales son disjuntos: 12 + 37 + 287 = 336. «Empresas con registros pendientes» suma parciales y pendientes: 324 ahora frente a 330 antes.

## Evidencia obtenida y alcance real

Se revisaron los XML primarios SMV locales para los 336 RPJ. La documentación específica cubre 56 empresas: 37 mediante memorias, estados financieros o documentos corporativos y 24 mediante series MINEM, con cinco empresas presentes en ambas fuentes. Se registran 64 evidencias y 35 documentos utilizados, con PDF completos o XLSX, SHA-256, pasajes, páginas, hojas y celdas. El inventario también identifica documentos conservados pero no utilizados y cinco intentos de descarga fallidos.

Las 40 evidencias PDF y 24 evidencias de series eléctricas alimentan reglas adicionales. D03 exige actividad principal identificada, entidad verificable, correspondencia unívoca y años explícitos. D04 combina actividad eléctrica MINEM, inversión anual positiva y sector SMV de servicios públicos del mismo ejercicio. D01/D02 y los controles anteriores no cambian.

La industria eléctrica concentra gran parte del aumento: `Power` reúne 24 empresas y 329 observaciones. Esta concentración refleja la disponibilidad de una serie primaria histórica; no demuestra que el resto del universo sea menos importante ni habilita comparaciones predictivas.

En años de referencia documentales se proponen industrias para 46 empresas, con 15 industrias distintas en esas evidencias. Esa métrica no equivale a cobertura histórica del panel. Cuatro empresas —Supermercados Peruanos, Ferreyros, Negocios e Inmuebles y Colegios Peruanos— tienen industria documentada pero ningún registro coincidente respaldado dentro del panel. Se mantienen pendientes sus observaciones históricas y se conserva la información empresarial para auditoría.

La búsqueda externa específica todavía no es exhaustiva para todas las empresas. El maestro expone esa limitación por RPJ; no presenta la revisión de metadatos SMV como sustituto de una memoria que describa suficientemente la actividad principal.

## Catálogos que debe revisar Antigravity

- [Maestro de las 336 empresas](catalogo_maestro_empresas.csv): identidad, RUC formalmente válido, actividad, fuente, año de referencia, industria propuesta, certeza y cobertura histórica.
- [Clasificación empresa-año](catalogo_empresa_anio.csv): 4.221 filas con industria anterior, nueva, regla y evidencia.
- [Evidencias de actividad](evidencias_actividad.csv) e [inventario de fuentes](fuentes_documentales.csv): permiten localizar cada pasaje y distinguir actividad documentada de industria pendiente.
- [Correspondencia actividad–CIIU–industria](correspondencia_actividad_ciiu_industria.csv): CIIU original, transcripción SMV del mismo año y códigos documentales separados.
- [Evidencia estadística por empresa-año](evidencias_estadisticas_empresa_anio.csv): reproduce cada celda MINEM y su encabezado anual. La vinculación manual de identidades está en `data/raw/sectorial_documental/correspondencias_minem.csv`.
- [Clasificadas](empresas_clasificadas.csv), [parciales](empresas_parcialmente_clasificadas.csv) y [pendientes](empresas_pendientes.csv): partición empresarial completa para revisión.
- [Observaciones pendientes](observaciones_pendientes.csv), [evidencias fuera del panel](evidencias_sin_observacion_panel.csv) y [señales de cambios de actividad](cambios_actividad_revision.csv).
- [Comparativo de cobertura](comparacion_cobertura.csv), [auditoría JSON](auditoria_enriquecimiento.json) y [pruebas](resultados_pruebas.txt).

El [documento metodológico](metodologia_documental.md) desarrolla reglas, límites y reproducción. El notebook `notebooks/08_clasificacion_sectorial.ipynb` contiene ambas pasadas ejecutadas y sus interpretaciones.

## Puntos que requieren juicio independiente

La regla MINEM usa inversiones como evidencia de actividad, no como medida de producción o participación en ingresos. Antigravity debe revisar su combinación con sector SMV, el enlace de denominaciones históricas y la correspondencia de generación, transmisión y distribución con `Power`. Las filas agrícolas o mineras que generan energía para uso propio no se incorporan por esa vía. Los años con cero, faltante o sin observación coincidente quedan pendientes.

Los holdings AENZA, UNACEM Corp, Ferreycorp e InRetail no heredan automáticamente la industria de subsidiarias; Nexa consolidado no resuelve su perímetro individual. Los bancos múltiples documentados siguen pendientes entre las dos industrias bancarias oficiales. Se mantienen también fronteras ambiguas de desarrollo inmobiliario, textiles y refinación. La Positiva Vida sí tiene evidencia específica de su rama para los años respaldados.

Hay una señal reportada de reorganización de UNACEM en 2022. La descarga del hecho de importancia devuelve HTTP 403: se distingue de un cambio confirmado mediante copia local verificable y no habilita asignaciones históricas. Los documentos locales de 2023/2024 sí acreditan la función de holding. No se interpreta todo cambio de nombre, accionista o CIIU como cambio económico.

Los 330 RUC válidos solo superan controles formales; no se certifica su estado SUNAT. Los seis `0` son valores originales de entidades extranjeras, no un RUC válido compartido. CIIU faltante sigue faltante: ni el nombre ni una actividad descrita se convierten en un código inventado.

## Verificación y siguiente trabajo

Se ejecutaron 35 pruebas: las 23 anteriores, sin modificaciones, y 12 nuevas. Se verificaron conservación exacta de finanzas y particiones, uniones sin pérdidas, reglas anteriores, ausencia de extrapolación, rechazo de evidencia contradictoria, identidad documental, códigos no transcritos y fuentes alteradas. Los CSV y el JSON se reproducen byte a byte. El notebook se ejecutó sin errores.

Se conservan los 3.560 casos elegibles: 2.869 de entrenamiento y 691 de prueba. No se entrenaron modelos, recalculó FCL ni alteraron E0–E2. Todo permanece en la rama local `sprint-07-clasificacion-sectorial`, sin commit, push ni cambios en main.

La siguiente ampliación debe priorizar notas históricas individuales de minería, construcción, retail y manufactura para los años aún no respaldados, y resolver subindustrias y perímetros financieros. Conviene revisar primero las reglas nuevas y sus identidades antes de ampliar automáticamente el catálogo. La escala monetaria del FCL y la disponibilidad histórica en tiempo real continúan sin acreditarse; esta clasificación retrospectiva no certifica un backtest point-in-time.
