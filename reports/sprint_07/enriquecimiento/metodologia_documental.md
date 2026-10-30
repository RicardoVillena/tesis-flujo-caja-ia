# Enriquecimiento documental del Sprint 07

## Entrega y fuentes

La primera entrega se conserva completa. `src/clasificacion_sectorial.py`, sus ocho pruebas y sus reportes no se modifican. La nueva capa reside en `src/enriquecimiento_sectorial.py` y sus resultados en este directorio. El notebook distingue ambas pasadas.

El maestro contiene los 336 RPJ del panel, sin excluir empresas por problemas de identidad o documentación. Se revisaron los registros primarios SMV locales para todo el universo mediante el parser SOAP existente de `scripts/trace_smv.py`. Esa revisión acredita nombres, RUC declarados, sector, CIIU cuando existe y ejercicio; no demuestra por sí sola una actividad principal suficientemente específica. `revision_smv_empresa_anio.csv` conserva archivo, hash y posición del objeto JSON para localizar cada registro.

La investigación específica añade memorias, notas de estados financieros individuales y consolidados, documentación corporativa y estadísticas primarias del MINEM. Los documentos utilizados, sus pasajes, páginas o celdas y decisiones están en `evidencias_actividad.csv`. El corpus congelado, las respuestas fallidas y los metadatos están en `data/raw/sectorial_documental`. Se conservan los PDF completos y una transcripción de apoyo; algunas transcripciones cubren solo las primeras 35 páginas. Los PDF no se sustituyen por las transcripciones.

La fuente estadística es el [Anuario Estadístico de Electricidad 2024 del MINEM](https://www.gob.pe/institucion/minem/informes-publicaciones/7324144-anuario-estadistico-de-electricidad-2024), cuadro 10.17, hojas `10.17.2 Inversion Privada` y `10.17.3 y 4 Publica y Gub`. Se conservan los libros oficiales, sus URL y SHA-256. El libro incluye series históricas 1995–2024; se emplean solo celdas de los ejercicios observados del panel 2005–2025. El índice y algunos archivos tienen actualizaciones posteriores al ejercicio de referencia: la clasificación es retrospectiva, sin afirmar disponibilidad histórica en tiempo real. Algunos encabezados/notas del libro son preliminares; se conserva la versión descargada sin corregir cifras.

El vocabulario industrial sigue siendo [Damodaran, enero de 2026](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/Betas.html). Ninguna correspondencia se presenta como clasificación empresarial oficial de NYU. Las categorías, macrosectores y grados de certeza son decisiones analíticas auditables del proyecto.

## Identidad empresarial

RPJ sigue siendo la clave de empresa. Se preservan todos los RUC originales; `RUC_valido_formal` exige 11 dígitos, prefijo admisible y control aritmético del dígito verificador. Esto no certifica inscripción, estado, condición de domicilio ni actividad SUNAT: no se realizó consulta registral SUNAT individual ni se utilizaron directorios secundarios como sustituto de la fuente primaria.

Hay 330 empresas con RUC formalmente válido y seis entidades extranjeras con valor original `0`. El maestro conserva ese valor y deja vacío el RUC validado; no lo rellena. El indicador anterior de un «RUC compartido» correspondía al centinela `0`: al considerar solo RUC válidos no hay RUC compartidos entre RPJ. La auditoría anterior permanece intacta y esta precisión se registra en la nueva.

Las vinculaciones documentales se revisaron manualmente por entidad jurídica y RPJ, conservando el nombre y los alias observados. La relación entre el listado MINEM y el maestro figura en `correspondencias_minem.csv`. El MINEM no proporciona RUC en esas hojas: sus RUC asociados provienen del maestro SMV, no de una consulta MINEM o SUNAT. No existe unión difusa ni regla de industria basada únicamente en palabras del nombre.

## Reglas nuevas y límites temporales

D03 asigna una industria a una observación antes pendiente cuando una fuente primaria identifica la actividad de esa entidad, la correspondencia es unívoca dentro del vocabulario adoptado, y el ejercicio aparece expresamente en `anios_respaldados`. Certeza alta de actividad y correspondencia son condiciones necesarias. No se sobrescribe una regla original; una contradicción detiene la reproducción para revisión.

Un informe de 2024 no clasifica automáticamente los ejercicios anteriores. Los comparativos se usan únicamente cuando el pasaje respalda ambas actividades: por ejemplo, tiendas de Saga Falabella en 2023/2024, plantas y flotas pesqueras en ambos ejercicios o potencia eléctrica explícita de Enel Generación Piura en 2019/2020 y 2023/2024. La fecha de constitución, el objeto estatutario genérico o la mera ausencia de noticias de cambio no prueban estabilidad de toda la historia.

D04 combina tres evidencias: correspondencia manual de entidad con el cuadro primario MINEM; inversión ejecutada estrictamente positiva en una celda anual de generación, transmisión o distribución eléctrica; y TipoSector SMV `SERVICIOS PUBLICOS` en ese mismo ejercicio. Se asigna `Power` como industria analítica de electricidad. Una fila nominal sin dato, un cero o una cifra de otro ejercicio no habilitan asignación. Tampoco se aplica a productores eléctricos de uso propio de sectores agrícolas, industriales o mineros: la generación accesoria no demuestra su actividad principal. No se interpolan los años sin evidencia ni se asigna 2025 desde la serie que acaba en 2024.

La inversión eléctrica es evidencia de actividad sectorial durante el ejercicio, no una medida de producción, ingresos principales, rentabilidad ni entrada efectiva en operación comercial de cada proyecto. El enlace con el sector SMV y la identidad de empresas eléctricas acota la regla; su validez económica debe revisarse independientemente antes de usarla en modelos. No se afirma que un importe positivo por sí solo pruebe la actividad principal de cualquier empresa.

La asignación `Power` comprende la actividad eléctrica identificada de generación, transmisión y distribución; no implica que todos sean generadores. `Food Processing` se propone para la transformación industrial integrada de pescado, manteniendo esa categoría explícita. Los casos de hilandería frente a `Apparel`, refinación frente a `Oil/Gas (Integrated)`, desarrollo inmobiliario frente a `Homebuilding`, bancos múltiples y holdings permanecen pendientes cuando la frontera no es unívoca.

La certeza alta expresa la evaluación documental del curador; no es una probabilidad calibrada ni reemplaza la revisión de Antigravity. Los documentos consolidados solo se usan para una subsidiaria si la fuente describe a esa entidad específicamente. Por eso Nexa consolidado no resuelve automáticamente Nexa individual, mientras la tabla específica de Ferreyros permite documentar su distribución de maquinaria.

## Actividad, CIIU e industria

`CIIU` y `ciiu_normalizado` son las columnas de la primera entrega. `ciiu_smv_documental` transcribe el XML SMV del mismo RPJ y ejercicio; `ciiu_documental` conserva los códigos que un documento empresarial declara literalmente. No se deducen códigos desde una descripción de actividad, no se rellenan faltantes y no se traslada el código de otro año. Se exige que cada código documental esté presente en el pasaje localizado.

Ejemplos: Laive declara 1010, 1050 y 4690 en revisión 4, sin identificar uno de esos tres como única actividad principal; Aceros Arequipa declara 2410; Cosapi declara 4390 con una descripción que requiere cotejo de edición. Los códigos se conservan tal como se reportan y la industria se sustenta en la actividad y las operaciones documentadas, sin «corregir» unilateralmente la fuente. Una industria puede documentarse aunque el CIIU siga vacío: la tabla hace visible esa brecha en la cadena de evidencia.

`macrosector_enriquecido` y `sector_enriquecido` complementan la jerarquía sin alterar las columnas originales. Solo se completa el macrosector original pendiente cuando hay industria respaldada. Los códigos SMV originales y las reglas M01/M02 se conservan.

## Dos niveles de cobertura y cambios

Los estados Clasificada, Parcialmente clasificada y Pendiente del maestro son mutuamente excluyentes y dependen de la cobertura de las observaciones históricas del panel: todas, algunas o ninguna con industria asignada. No deben confundirse con disponer de una actividad empresarial documentada en un año de referencia.

Cuatro empresas tienen una industria documental respaldada en años sin observación coincidente en el panel: Supermercados Peruanos, Ferreyros, Negocios e Inmuebles y Colegios Peruanos. Se conserva la actividad en el maestro y las evidencias, pero no se usa para clasificar sus registros de otros ejercicios. `evidencias_sin_observacion_panel.csv` permite auditar estas situaciones, incluyendo otras evidencias fuera de la muestra anual.

«Estable» significa compatible solo en los ejercicios documentados; no certifica los huecos ni el intervalo completo. `cambios_actividad_revision.csv` distingue una señal de reorganización de UNACEM hacia estructura holding. El hecho de importancia fue localizado en el índice primario, pero la descarga original devuelve HTTP 403: la fecha reportada de 2022 queda pendiente de verificación de la copia original y no habilita asignaciones. Los estados separados de 2023/2024 sí describen directamente el rol de holding y evitan atribuir a la matriz la producción de sus subsidiarias. No se confunden cambios de nombre, de RUC, de revisión CIIU o de accionista con cambios de actividad.

## Integridad y reproducción

```bash
conda run -n tesis-fcl python scripts/reproduce_enriquecimiento_sectorial.py
conda run -n tesis-fcl python -m unittest discover -s tests -v
```

La reproducción no usa red ni parser PDF; lee las evidencias congeladas y verifica sus hashes, pasajes y celdas. `scripts/descargar_evidencia_sectorial.py` es una herramienta opcional de adquisición para los PDF del manifiesto. La extracción original se realizó con pypdf 6.21.2 instalado solo en `/tmp`, sin modificar el entorno ni los archivos de dependencias del proyecto. Los XLSX se conservan con URL de descarga en `fuentes_estadisticas.json` y se leen con openpyxl, ya disponible.

Se verifican 4.221 registros, 336 RPJ, ausencia de duplicados, conservación exacta de todas las columnas del panel, elegibilidad y particiones: 2.869 casos de entrenamiento y 691 de prueba. El FCL no se recalcula. Los hashes comprueban fuentes, experimentos y reportes de la primera entrega. Los 23 tests anteriores se mantienen; se añaden pruebas de períodos, evidencia, conflictos, alteración de fuente, RUC y datos MINEM sin inversión positiva. Los CSV y el JSON se reproducen byte a byte.

## Limitaciones pendientes

La revisión SMV local cubre todo el universo; la documentación específica externa cubre solo el subconjunto reportado en la auditoría. Para el resto no se ha completado una búsqueda externa exhaustiva por emisor y ejercicio: quedan explícitamente pendientes, sin simular investigación individual suficiente. Una actividad documentada fuera de los años presentes en el panel tampoco mejora la cobertura histórica.

La actualización es una ampliación verificable, no una taxonomía empresarial final ni una base lista para modelar todos los sectores. Persisten incertidumbre de edición CIIU, actividad principal frente a secundaria, identidad de algunas denominaciones históricas, perímetros de holding y subindustrias financieras. FCL sigue siendo una aproximación contable con escala monetaria no acreditada. No se entrenaron modelos ni se tocaron datos financieros, particiones, main, commits, push o PR.
