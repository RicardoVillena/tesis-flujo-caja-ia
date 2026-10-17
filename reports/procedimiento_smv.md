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

## Derechos y alcance de publicación (revisión ampliada)

La revisión ampliada del 16 de octubre de 2026 encontró las fichas específicas de
[obtener_InfoFinanciera](https://mvnet.smv.gob.pe/SMV.OpenData.Web/Views/Datasets/CtasPrinc.aspx)
y [obtener_FlujoEfectivo](https://mvnet.smv.gob.pe/SMV.OpenData.Web/Views/Datasets/FluEfe.aspx).
Ambas declaran ODbL. La primera corresponde a la operación, parámetros y esquema
de los 22 XML locales: se incluyen sin modificar. El inventario conserva la copia
idéntica de 2025 y no la cuenta dos veces al extraer.

Se incluye `features_financieras.csv` como adaptación calculada desde el panel
SMV declarado, con las 4.221 filas y 57 columnas, incluidas 22 características,
fuentes y controles. Se respetan atribución, aviso de licencia y compartir bajo
ODbL: ver [data/README.md](../data/README.md). La fuente de FCO/CAPEX es declarada,
no se ha acreditado su cadena de extracción histórica. No se confunde permiso
sobre el dataset oficial con validación contable de los valores del panel.
El panel se conserva sin cambios. La anterior exclusión conservadora del CSV y
XML se sustituye con esta evidencia específica, sin añadir el Excel.

El Excel (86.183 bytes) contiene dos hojas de análisis financieros complementarios:
`ESF - Evaluacion Vertical y hor` y `Evaluacion vertical y horizonta`. El XML interno
declara rangos A1:AF999 y A1:AB1000; la carga normal identifica celdas hasta AF59 y
AB199, respectivamente. No confundir dimensiones declaradas con filas de datos.
La primera hoja contiene situación financiera y análisis vertical/horizontal de
Aceros Arequipa, con encabezados 2016–2025 y unidad rotulada S/ miles; la segunda
contiene situación financiera y resultados de Agroindustrias AIB, con encabezados
2017–2025. Hay 2.476 fórmulas en conjunto. Esos análisis no son las 22 características
del panel; no hay dependencia del Excel en el cálculo ejecutado. Sus etiquetas y
fórmulas se revisaron, no se descartó por ser XLSX. Hay valores sin etiquetas en
40 filas desde la 109 de la segunda hoja: no se les atribuye FCO/CAPEX sin evidencia.
No es una respuesta original del servicio y no tiene fuente/licencia documentada:
queda local, preservado. Una revisión de permisos podría permitir una entrega
complementaria posterior. Ver [revisión completa](revision_entrega_semana5.md). El directorio `data/raw` no contiene otras fuentes
además de ese Excel y los XML inventariados.

El informe interno de Antigravity permanece local y fuera del árbol e historia
nueva de `feature-engineering`. Existía en la rama de presentación registrada en
`origin`; esta entrega no elimina exposiciones previas ni reescribe ramas.
No se hace merge ni push forzado.

## Reproducción completa de Feature Engineering desde el panel

El Excel no es necesario: el ejecutor omite archivos protegidos opcionales ausentes.
Desde un clon de la rama `feature-engineering`:

```bash
conda env create -f environment-feature-engineering.yml
conda activate tesis-fcl
python -m ipykernel install --user --name tesis-fcl --display-name tesis-fcl
python -m unittest discover -s tests -v
python scripts/reproduce_features.py --check
python scripts/execute_feature_engineering.py
python scripts/reproduce_features.py --check
```

Para regenerar solo el dataset sin kernel: `python scripts/reproduce_features.py`.
Con `--check` se exige igualdad byte a byte frente al CSV entregado, además de
igualdad de las 57 columnas y la máscara completa de NaN. Se verifica también que
las fuentes y las 4.221 filas permanezcan intactas. Los informes
`validacion_calculos.json` y `trazabilidad_variables.md` registran fuentes,
expresiones Python, fórmula, dominio, continuidad y observados/NaN por variable.
La prueba de referencia manual cubre individualmente las 22 características;
las pruebas temporales y de calidad añaden casos adversos.

El notebook vuelve a exportar el CSV y los informes académicos, y el ejecutor
registra sus celdas y hashes en `validacion_ejecucion.json`. Las versiones exactas
verificadas están en `requirements-feature-engineering.txt`. La instalación del
entorno queda documentada; no se simula una instalación nueva ni una descarga masiva
oficial durante esta revisión. Esto reproduce íntegramente Feature Engineering
**desde el panel entregado**, pero no cierra los tramos históricos faltantes para
reconstruir ese panel desde el servicio oficial.
