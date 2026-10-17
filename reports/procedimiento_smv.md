# Trazabilidad SMV y publicación de Semana 5

Revisión: 16 de octubre de 2026. El inventario verificable por archivo está en
[trazabilidad_smv.json](trazabilidad_smv.json): nombres, SHA-256, bytes, ejercicios,
campos, registros y contraste con el panel. No incluye los originales.

## Evidencia local

Se conservan 22 XML SOAP 1.1 con una lista JSON embebida en
`obtener_InfoFinancieraResult`: 2.559.277 bytes, ejercicios anuales 2005–2025,
tipo individual (A/I según nombre y contenido). La copia de 2025 con sufijo
`20261002_213002` tiene el mismo SHA-256 que la de nombre canónico. Ese sufijo no
acredita por sí solo una fecha real de descarga. Hay 5.997 registros al excluir
el archivo duplicado. Tamaños individuales: 97.732–130.107 bytes.

Los 16 campos son identificadores corporativos (RPJ/RUC), razón social,
clasificaciones, ejercicio, frecuencia, moneda, método de flujo y cinco agregados
financieros. No hay FCO, CAPEX, códigos de cuentas ni revisiones interanuales.
No se observaron correos, teléfonos, domicilios, credenciales ni nombres de
personas naturales como campos independientes. Los identificadores de empresas
se preservan como texto; esta revisión de estructura no constituye una
certificación de ausencia de datos personales en cualquier texto libre.

Las 4.221 claves RPJ/ejercicio del panel tienen correspondencia y coinciden en
todos los campos compartidos. Los XML incluyen 1.776 registros adicionales.
No existe evidencia de ejecución que demuestre cuáles de estos archivos se
utilizaron: ambos XML de 2025 son indistinguibles por contenido. No atribuir uso
histórico a un archivo por una mera coincidencia. No hay procedimiento registrado
para explicar la selección de 4.221 registros de los 5.997 disponibles.

## Procedimiento que sí permite ejecutar el repositorio

Desde la raíz, Python 3.12 (descarga/extracción usan solo biblioteca estándar):

```bash
# Consulta oficial; conserva los archivos existentes, no los sobrescribe.
python src/ingestion/ingest_smv.py --start 2005 --end 2025
# Inventario, extracción SOAP -> JSON, contraste de valores y metadatos públicos.
python scripts/trace_smv.py
# Extracción tabular opcional local, deduplicando archivos por SHA-256.
python scripts/trace_smv.py --extract data/processed/smv_infofinanciera_extraida.csv
# Con el entorno de Semana 5 disponible:
conda activate tesis-fcl
python -m unittest discover -s tests -v
python scripts/execute_feature_engineering.py
```

La descarga usa POST SOAP a
https://mvnet.smv.gob.pe/ws_od_eeff/WebServiceInfoFinanciera.asmx,
operación `obtener_InfoFinanciera`, Ejercicio, Periodo=A y Tipo=I. Comprueba HTTP,
XML y lista JSON, guarda bytes originales y genera `descargas.jsonl` con fecha
UTC, parámetros, estado, hash y número de registros; espera un segundo entre
consultas. Los logs son prospectivos: no existían para acreditar los originales.
Los errores producen salida no exitosa y se registran. Para comparar una descarga
nueva sin alterar los originales, usar `--output /tmp/smv-nueva` y luego
`trace_smv.py --raw-dir /tmp/smv-nueva --report /tmp/traza-nueva.json`.
No se ejecutó una descarga masiva durante esta revisión.

La extracción nueva conserva valores y etiquetas (incluido `D lares`), no
homologa monedas ni unidades, y no genera un panel FCL. El contraste usa
RPJ/ejercicio y todos los campos compartidos; no imputa ni rellena registros.
El panel existente se toma como entrada del notebook de Semana 5. Su código
reproducible aplica las reglas del diccionario, calcula ratios, variaciones,
rezagos, ventanas y objetivo t+1; genera `features_financieras.csv` local y
resultados del notebook. Las pruebas verifican, entre otras propiedades, ausencia
de influencia futura, huecos temporales, moneda y CAPEX positivo.

## Tramos faltantes: reproducción integral NO acreditada

No se halló código ni respuestas originales de `obtener_FlujoEfectivo` que
permitan recuperar FCO y CAPEX; tampoco el mapeo validado de `3D01ST`/`3D0206`,
la selección de empresas, la resolución de revisiones interanuales, las reglas de
consolidación y el script que escribió `panel_fcl_preliminar.csv`. El EDA lo lee,
no lo construye. FCL_preliminar = FCO + CAPEX_reportado es una identidad del
panel, no prueba su procedencia ni un FCFF validado. No se inventó una ingesta de
balance/resultados/flujo ni una arquitectura BRONZE/SILVER/GOLD ya implementada.
La descripción metodológica general del README es una propuesta.

Para cerrar la brecha se necesitan las respuestas oficiales de detalle, parámetros
y versiones históricas, el código de selección y combinación, reglas contables
y pruebas contra el panel por clave y valor. Una consulta actual puede devolver
revisiones; no garantiza recuperar los mismos bytes o valores históricos.

## Derechos y alcance de publicación

La fuente es la Superintendencia del Mercado de Valores del Perú (SMV).
El [portal oficial](https://mvnet.smv.gob.pe/SMV.OpenData.Web/Views/Inicio/Inicio.aspx)
presenta información financiera como datos abiertos. La ficha de
[Estado de Resultados](https://mvnet.smv.gob.pe/SMV.OpenData.Web/Views/Datasets/EstResult.aspx)
y la de [Empresas Inscritas](https://www.smv.gob.pe/SMV.OpenData.Web/Views/Datasets/Empresas_Inscritas.aspx)
indican Open Data Commons Open Database License (ODbL). Consulta: 2026-10-16.
Esa evidencia no verifica por sí sola la licencia aplicable a cada respuesta local
de `obtener_InfoFinanciera` ni a las fuentes ausentes de FCO/CAPEX. No se asigna
una licencia nueva a esos archivos ni se presume que acceso público equivale a
redistribución sin condiciones. Se mantiene la exclusión conservadora solicitada.

Se publican código, notebook, pruebas, diccionario, documentación y metadatos de
trazabilidad. El panel de entrada ya estaba en la historia pública y se conserva
sin cambios: **su presencia previa no verifica sus derechos ni su linaje completo**.
No se añade otro dataset financiero: `features_financieras.csv` sigue local,
pendiente de verificar las fuentes heredadas. Los originales XML y su extracción
opcional quedan ignorados; el Excel complementario, de procedencia y permisos no
acreditados, deja de figurar en el árbol de esta entrega y se conserva local.

El informe interno de Antigravity queda local y fuera del árbol e historia nueva
de `feature-engineering`. Existía en la rama de presentación ya registrada en
`origin`; esta publicación no elimina exposiciones previas ni reescribe ramas.
No se hace merge ni push forzado. Los hashes de ejecución documentan una ejecución
concreta anterior; la validación actual se distingue de esa evidencia.

## Validación de esta entrega

13 pruebas unitarias aprobadas; notebook ejecutado con 11 celdas de código sin
errores y 26 archivos protegidos intactos. Evidencia de esta ejecución en
`validacion_ejecucion.json`. No se verificó una descarga nueva de extremo a extremo.
