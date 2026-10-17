# Revisión de la entrega de Semana 5 antes de publicación

Commit revisado: `52b66a31d5ddaad0a6a345469ccfa6cdfbdedf35`.
Rama: `feature-engineering`. Esta revisión solo inspecciona, prueba y documenta;
no agrega archivos al índice, crea commits, publica ni modifica credenciales.
La evidencia estructurada está en [verificacion_semana5.json](verificacion_semana5.json).

## Resultado

El Feature Engineering puede reproducirse desde el panel entregado. Se verifican
4.221 filas en ambos CSV, 57 columnas en la salida y 22 predictores, preservando
fuentes, NaN y banderas. No se acredita todavía la reconstrucción del panel desde
los datos oficiales de detalle. La correspondencia con los XML verifica los
resúmenes, no la extracción de FCO/CAPEX ni el uso histórico de un archivo.

## Matriz del procedimiento: fuente hasta resultado

| Etapa | Entrada / fuente | Procedimiento y artefacto | Evidencia / estado |
| --- | --- | --- | --- |
| SMV → descarga de resumen | Servicio oficial `WebServiceInfoFinanciera.asmx`, `obtener_InfoFinanciera`, Ejercicio 2005–2025, Periodo A, Tipo I | `src/ingestion/ingest_smv.py`; POST SOAP, validación de respuesta, guardado y log prospectivo | Código disponible; no se descargó nuevamente la serie ni se acredita la fecha/versión de la ingesta histórica |
| Respuesta → datos originales | `data/raw/smv/*.xml` | 22 XML SOAP con JSON interno; 21 ejercicios, 2.559.277 bytes | Incluidos en el commit; SHA-256 e inventario en `trazabilidad_smv.json`; las dos copias de 2025 son idénticas |
| XML → tabla de resúmenes | Los 22 archivos | `scripts/trace_smv.py`: extracción XML/JSON; deduplicación de archivos por SHA-256 | 5.997 claves RPJ/ejercicio distintas; ninguna clave duplicada después de retirar el archivo idéntico; no crea FCO/CAPEX |
| SMV de detalle → FCO/CAPEX | Fuente declarada: `obtener_FlujoEfectivo`; no se conservan aquí respuestas históricas de esa operación | Faltan el extractor histórico y las reglas por cuenta, formato, método y monto | **Pendiente**: los 16 campos de los XML disponibles no contienen FCO, CAPEX ni sus códigos |
| Resúmenes + FCO/CAPEX → panel | 5.997 registros de resúmenes más detalle de flujos ausente | `data/processed/panel_fcl_preliminar.csv`, 4.221 filas | **Consolidación histórica pendiente**. Las 4.221 claves y sus 16 campos compartidos coinciden sin discrepancias; hay 1.776 claves adicionales en los XML |
| Panel → FCL fuente | FCO y CAPEX_reportado con signo | Identidad `FCL_preliminar = FCO + CAPEX_reportado`, comprobada en 3.898 filas con los tres valores observados | El constructor preserva el FCL original; esta identidad no reconstruye su ingesta ni valida un FCFF |
| Panel → 22 características | Panel, empresa, año, moneda y columnas financieras | `src/feature_engineering.py::build_features`; 8 ratios, 4 variaciones, 10 temporales | Fórmulas y dependencias en la tabla siguiente; reglas completas en `trazabilidad_variables.md`; 15 pruebas aprobadas |
| FCL validado → objetivo futuro | FCL fuente, CAPEX, RPJ, ejercicio y moneda | Unión exacta al año t+1; invalida FCL para derivaciones si CAPEX de su año >0; controla moneda futura | Etiqueta y controles separados de X; faltantes preservados; no se sustituye t+1 por la siguiente fila |
| Características → resultados | 4.221 filas calculadas | `scripts/reproduce_features.py`, notebook y `features_financieras.csv` | 57 columnas; regeneración idéntica byte a byte; tablas, gráficos, interpretación y diagnósticos en notebook e informes |

Las fichas oficiales específicas de [resúmenes](https://mvnet.smv.gob.pe/SMV.OpenData.Web/Views/Datasets/CtasPrinc.aspx)
y [flujos](https://mvnet.smv.gob.pe/SMV.OpenData.Web/Views/Datasets/FluEfe.aspx)
indican ODbL. La atribución y el alcance de licencia están en `data/README.md`.
Esto no demuestra que los valores de detalle del panel se hayan extraído con las
reglas adecuadas ni permite extender permisos al Excel de procedencia desconocida.

## Revisión del Excel, preservado localmente

Archivo: `data/raw/base_de_datos.xlsx`, 86.183 bytes.
SHA-256: `d2d72e7d7874ba93f22d689f1d799315507095ba1a692e29006f0a75053df79c`.
Se inspeccionaron valores, etiquetas, fórmulas, cachés, hojas visibles, nombres
definidos y enlaces externos. No se modificó ni se excluyó por ser XLSX.

| Hoja | Contenido identificado | Alcance de celdas cargadas / contenido | Fórmulas |
| --- | --- | --- | --- |
| ESF - Evaluacion Vertical y hor | Situación financiera de Aceros Arequipa; encabezados 2016–2025; montos rotulados S/ miles; análisis vertical y horizontal | A1:AF59; 56 filas y 1.421 celdas no vacías | 874; 48 sin resultado en caché |
| Evaluacion vertical y horizonta | Situación financiera y estado de resultados de Agroindustrias AIB; encabezados 2017–2025; análisis vertical y horizontal | A1:AB199; 147 filas y 2.804 celdas no vacías | 1.602; todas con caché |

Los rangos declarados por el XML del libro son A1:AF999 y A1:AB1000: no son
999/1.000 observaciones. No hay hojas ocultas, enlaces externos ni nombres definidos.
Las fórmulas revisadas incluyen cocientes por activos e ingresos y variaciones
interanuales; no son una implementación de las 22 características del panel.
Hay 40 filas no vacías desde la 109 de la segunda hoja sin etiquetas de texto;
no se atribuyen esos números a FCO/CAPEX ni se infieren unidades o periodos no
rotulados. Un caché ausente no implica dato cero; openpyxl no evalúa fórmulas.

No se encontraron etiquetas explícitas que documenten extracción de FCO/CAPEX.
El notebook no lee el Excel; el ejecutor solo lo protege si existe. Se ejecutó
el notebook completo en una copia de los archivos versionados **sin el Excel**:
el CSV resultante fue idéntico. Por ello no es necesario para reproducir los
cálculos actuales. Es material académico complementario que se conserva local,
pendiente de acreditar su origen y permiso de redistribución. No se considera
irrelevante para toda la tesis ni se intenta reconstruir el panel a partir de él.

## Reglas históricas pendientes de reconstrucción

1. Recuperar respuestas de `obtener_FlujoEfectivo`, parámetros por ejercicio,
   fecha y versión de descarga, formato de respuesta y método directo/indirecto.
   Los archivos actuales son de `obtener_InfoFinanciera`, otra operación.
2. Validar el significado y la selección de cuentas por formato/sector. El panel
   contiene FCO con códigos `3D01ST`, `3F0501`, `3E0301`, `3A01ST` y CAPEX con
   `3D0206`, `3F0625`, `3E0405`, `3A0206`. No asumir un único mapeo industrial.
3. Definir uso de Monto 1 frente a Monto 2, selección de ejercicio corriente o
   comparativo y resolución de diferencias entre reportes sucesivos. Falta el
   algoritmo que creó las 1.271 banderas `revision_interanual=True`.
4. Documentar filtros que redujeron los 5.997 registros de resumen a las 4.221
   filas, tipos de entidad incluidos, claves de unión y resolución de duplicados.
5. Acreditar unidad/escala, convenciones de signos, tratamiento de cambios de
   moneda y si una cuenta ausente significa NaN o cero; validar CAPEX para cada
   formato y no convertir una inversión no equivalente en CAPEX por su nombre.
6. Documentar las reglas de FCL y calidad que generaron 3.898 `PRELIMINAR`,
   301 `INCOMPLETO` y 22 `REVISAR_CAPEX_POSITIVO`. Hay 90 FCO, 247 CAPEX y 323 FCL
   faltantes. Son estados observados, no una especificación histórica inferida.
7. Recuperar el script de extracción, combinación y escritura del panel; aportar
   pruebas por clave, cuenta y valor contra los originales oficiales. Comparar
   nuevos datos oficiales debe admitir revisiones sin afirmar igualdad histórica.

No se implementa un extractor de detalle hipotético en esta revisión. Las reglas
actuales de derivación están documentadas: cocientes con denominadores positivos,
segmentos anuales continuos por moneda, ventanas estrictamente previas y objetivo
por año exacto. Persisten limitaciones: escala no acreditada, fechas de publicación
ausentes, moneda deteriorada en una etiqueta y formatos financieros heterogéneos.

## Verificación de archivos y pruebas

Están versionados ambos CSV, 22 XML y sus avisos, notebook ejecutado, EDA previo,
módulos, scripts, diccionario, trazabilidad individual, dependencias, instrucciones,
informes académicos y validaciones. La lista completa de los archivos del commit
está en `verificacion_semana5.json` (`archivos_versionados`); los cuatro documentos
nuevos/modificados de esta revisión se enumeran al final.

Comprobaciones ejecutadas durante esta revisión:

- `python -m unittest discover -s tests -v`: **15 pruebas aprobadas**, incluida
  referencia manual de las 22 variables y preservación de todas las filas y NaN.
- `python scripts/reproduce_features.py --check`: igualdad byte a byte, fuentes
  preservadas y máscara NaN idéntica.
- `python scripts/trace_smv.py --report /tmp/revision-semana5-traza.json`:
  inventario y contraste de 4.221 claves y 16 campos, sin discrepancias.
- Ejecutor del notebook y comprobación posterior del CSV en una copia temporal
  de los archivos versionados: **11 celdas ejecutadas, cero errores**, sin Excel
  ni informe interno. Git se consultó solo para el nombre de rama mediante
  `GIT_DIR`; no se inicializó un repositorio ni se modificaron referencias.

Se utilizó el entorno existente `tesis-fcl`, Python 3.12. No se instaló un entorno
nuevo ni se hizo descarga masiva SMV. Notebook y evidencias se generaron en la
copia temporal para no alterar los entregables revisados. Los CSV y XML locales
permanecen intactos. Las instrucciones de reproducción están en README y
`procedimiento_smv.md`; las fórmulas completas y casos de dominio están en
`trazabilidad_variables.md`.

## Contenido excluido y revisión del índice

| Archivo o grupo | Decisión y motivo |
| --- | --- |
| `data/raw/base_de_datos.xlsx` | Preservado localmente; permisos/origen no verificados; no requerido por el cálculo comprobado |
| `reports/auditoria_feature_engineering.md` | Informe interno de Antigravity: ignorado, no presente en el árbol ni historial de esta rama |
| Logs de descarga, extracción opcional, cachés y runtime | Ignorados; no necesarios para la entrega versionada |
| Credenciales | Ningún archivo de credenciales forma parte de la lista versionada o de la propuesta de esta revisión |

La documentación de correcciones académicas (`correcciones_antigravity.md`) es
un archivo distinto del informe interno. No se publica este último con otro nombre.
El informe interno existía en otra rama de presentación: no se elimina ni modifica
historial ajeno en esta revisión.

## Estado de Git y comandos para ejecución personal

Al comenzar, árbol limpio; rama `feature-engineering`, HEAD `52b66a31...`; sin
upstream configurado y sin cambios preparados en el índice. La consulta de solo
lectura `git ls-remote --heads origin feature-engineering` terminó correctamente
sin devolver referencias: la rama no estaba publicada al consultar. No se ejecutó
fetch, add, commit, push, merge, reset ni modificación de credenciales.

Pendiente de incorporar: solo esta revisión documental:

- `README.md`: enlace a esta revisión.
- `reports/procedimiento_smv.md`: inspección ampliada/corrección del alcance del Excel.
- `reports/revision_entrega_semana5.md`: matriz y revisión completa (nuevo).
- `reports/verificacion_semana5.json`: evidencia de revisión (nuevo).

Los cálculos, fuentes autorizadas y scripts ya están dentro del commit existente;
no necesitan volver a agregarse. Después de revisar y aprobar esos cuatro cambios,
ejecutar personalmente en Ubuntu:

```bash
cd /home/ricardo/proyectos/tesis-flujo-caja-ia
test "$(git branch --show-current)" = "feature-engineering" || exit 1
git status --short --branch
git diff -- README.md reports/procedimiento_smv.md
less reports/revision_entrega_semana5.md
less reports/verificacion_semana5.json
git add -- README.md reports/procedimiento_smv.md reports/revision_entrega_semana5.md reports/verificacion_semana5.json
git diff --cached --check
git diff --cached --stat
git commit -m "Documenta revisión final y matriz de trazabilidad de Semana 5"
git push -u origin feature-engineering
```

Si hace falta autenticación, realizarla personalmente antes del push, con una
cuenta con escritura en el repositorio. En Ubuntu con GitHub CLI instalado:

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
```

No se ejecutaron esos comandos de autenticación. Si no está instalado `gh`, seguir
las instrucciones oficiales enlazadas en `entrega_semana5.md`; no introducir tokens
en archivos del proyecto ni en el chat. Si el remoto rechaza el avance, revisar
su estado antes de continuar, sin usar `--force` ni hacer merge automático.

## Matriz de las 22 características

Todas las expresiones siguientes se calculan por empresa y moneda con las reglas
de `trazabilidad_variables.md`. FCL en las derivaciones es la versión invalidada
cuando CAPEX de su año es positivo; el FCL fuente exportado se preserva. Las cuentas
y fórmulas de esta tabla describen lo ejecutado, no acreditan el extractor histórico.

| Característica | Columnas financieras fuente | Fórmula | Observados / NaN |
| --- | --- | --- | --- |
| pasivo_activo | PasivoTotal, ActivoTotal | 1 × PasivoTotal(t) / ActivoTotal(t), denominador > 0 | 4221 / 0 |
| margen_neto | UtilidadNeta, TotalIngreso | 1 × UtilidadNeta(t) / TotalIngreso(t), denominador > 0 | 3950 / 271 |
| rentabilidad_activo_cierre | UtilidadNeta, ActivoTotal | 1 × UtilidadNeta(t) / ActivoTotal(t), denominador > 0 | 4221 / 0 |
| rotacion_activo_cierre | TotalIngreso, ActivoTotal | 1 × TotalIngreso(t) / ActivoTotal(t), denominador > 0; ingreso actual > 0 | 3950 / 271 |
| fco_activo | FCO, ActivoTotal | 1 × FCO(t) / ActivoTotal(t), denominador > 0 | 4131 / 90 |
| fco_ingresos | FCO, TotalIngreso | 1 × FCO(t) / TotalIngreso(t), denominador > 0 | 3865 / 356 |
| inversion_capex_activo | CAPEX_reportado, ActivoTotal | -1 × CAPEX_reportado(t) / ActivoTotal(t), denominador > 0; solo CAPEX_reportado <= 0 | 3952 / 269 |
| fcl_activo | FCL_preliminar, ActivoTotal, CAPEX_reportado | 1 × FCL_preliminar(t) / ActivoTotal(t), denominador > 0; FCL fuente invalidado si CAPEX de su año > 0 | 3898 / 323 |
| crecimiento_ActivoTotal | ActivoTotal | (ActivoTotal(t) - ActivoTotal(t-1)) / ActivoTotal(t-1), base > 0 | 3822 / 399 |
| crecimiento_TotalIngreso | TotalIngreso | (TotalIngreso(t) - TotalIngreso(t-1)) / TotalIngreso(t-1), base > 0; ingreso actual > 0 | 3568 / 653 |
| cambio_FCO_activo_previo | FCO, ActivoTotal | (FCO(t)-FCO(t-1))/ActivoTotal(t-1) | 3701 / 520 |
| FCO_lag1 | FCO | FCO(t-1) | 3734 / 487 |
| FCO_lag2 | FCO | FCO(t-2) | 3392 / 829 |
| FCO_lag3 | FCO | FCO(t-3) | 3073 / 1148 |
| FCO_mean3_previa | FCO | mean de FCO(t-3), FCO(t-2), FCO(t-1) | 3013 / 1208 |
| FCO_std3_previa | FCO | std de FCO(t-3), FCO(t-2), FCO(t-1); ddof=1 | 3013 / 1208 |
| cambio_FCL_preliminar_activo_previo | FCL_preliminar, ActivoTotal, CAPEX_reportado | (FCL_preliminar(t)-FCL_preliminar(t-1))/ActivoTotal(t-1); FCL fuente invalidado si CAPEX de su año > 0 | 3456 / 765 |
| FCL_preliminar_lag1 | FCL_preliminar, CAPEX_reportado | FCL_preliminar(t-1); FCL fuente invalidado si CAPEX de su año > 0 | 3506 / 715 |
| FCL_preliminar_lag2 | FCL_preliminar, CAPEX_reportado | FCL_preliminar(t-2); FCL fuente invalidado si CAPEX de su año > 0 | 3169 / 1052 |
| FCL_preliminar_lag3 | FCL_preliminar, CAPEX_reportado | FCL_preliminar(t-3); FCL fuente invalidado si CAPEX de su año > 0 | 2854 / 1367 |
| FCL_preliminar_mean3_previa | FCL_preliminar, CAPEX_reportado | mean de FCL_preliminar(t-3), FCL_preliminar(t-2), FCL_preliminar(t-1); FCL fuente invalidado si CAPEX de su año > 0 | 2766 / 1455 |
| FCL_preliminar_std3_previa | FCL_preliminar, CAPEX_reportado | std de FCL_preliminar(t-3), FCL_preliminar(t-2), FCL_preliminar(t-1); ddof=1; FCL fuente invalidado si CAPEX de su año > 0 | 2766 / 1455 |
