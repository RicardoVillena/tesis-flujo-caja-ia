# Informe de Auditoría Técnica, Estadística, Financiera y Metodológica — Clasificación Sectorial e Intrasectorial (`Sprint 07`)

- **Proyecto:** `tesis-flujo-caja-ia`
- **Rama auditada:** `sprint-07-clasificacion-sectorial`
- **Notebook auditado:** [`notebooks/08_clasificacion_sectorial.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/08_clasificacion_sectorial.ipynb) (`604,846` bytes; `44` celdas: `30` Markdown y `14` de código con `execution_count = 1..14`)
- **Módulos y pruebas auditadas:**
  - Primera pasada (reglas base `M01/M02`, `D01/D02`, `P01/P02/P03`): [`src/clasificacion_sectorial.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/clasificacion_sectorial.py), [`scripts/reproduce_clasificacion_sectorial.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/scripts/reproduce_clasificacion_sectorial.py) y [`tests/test_clasificacion_sectorial.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_clasificacion_sectorial.py) (`8` tests)
  - Segunda pasada (ampliación documental `D03/D04`): [`src/enriquecimiento_sectorial.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/enriquecimiento_sectorial.py), [`scripts/reproduce_enriquecimiento_sectorial.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/scripts/reproduce_enriquecimiento_sectorial.py), [`scripts/descargar_evidencia_sectorial.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/scripts/descargar_evidencia_sectorial.py) y [`tests/test_enriquecimiento_sectorial.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_enriquecimiento_sectorial.py) (`12` tests)
- **Entregables verificados:**
  - Insumos Damodaran: [`data/raw/damodaran/betas_2026.html`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/raw/damodaran/betas_2026.html), [`data/raw/damodaran/industrias_2026.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/raw/damodaran/industrias_2026.csv) (`94` industrias) y [`data/raw/damodaran/fuente_2026.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/raw/damodaran/fuente_2026.json)
  - Corpus documental primario: `data/raw/sectorial_documental/` ([`evidencias_actividad.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/raw/sectorial_documental/evidencias_actividad.csv), [`correspondencias_minem.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/raw/sectorial_documental/correspondencias_minem.csv), [`descargas.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/raw/sectorial_documental/descargas.json), [`fuentes_estadisticas.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/raw/sectorial_documental/fuentes_estadisticas.json), PDFs, transcripciones `.txt` y libros `.xlsx` del MINEM)
  - Reportes de primera pasada (`reports/sprint_07/`): [`auditoria_sectorial.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_07/auditoria_sectorial.json), [`metodologia_clasificacion_sectorial.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_07/metodologia_clasificacion_sectorial.md), `9` tablas CSV y `6` gráficos PNG
  - Reportes de enriquecimiento documental (`reports/sprint_07/enriquecimiento/`): [`auditoria_enriquecimiento.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_07/enriquecimiento/auditoria_enriquecimiento.json), [`metodologia_documental.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_07/enriquecimiento/metodologia_documental.md), [`informe_auditoria_antigravity.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_07/enriquecimiento/informe_auditoria_antigravity.md) y `15` tablas CSV
- **Entorno de verificación:** Conda `tesis-fcl` (`Python 3.12.15`, `pandas 3.0.6`, `numpy 2.5.4`, `openpyxl`, `matplotlib 3.11.2`)
- **Rol:** Auditor independiente (sin modificación de notebooks, datasets, scripts ni catálogos existentes)

---

## 1. Resumen Ejecutivo

Se realizó una auditoría independiente integral sobre las dos capas del **Sprint 07**: (1) la clasificación base sobre variables observadas en el panel (`sprint07-v1`) y (2) la ampliación mediante evidencia documental primaria SMV y series estadísticas del MINEM (`sprint07-documental-v1`).

| Dimensión Auditada | Estado | Resumen de Verificación |
| :--- | :---: | :--- |
| **1. Conservación del panel, particiones y archivos previos** | **APROBADO** | Conservación exacta (`check_exact=True`) de las `4,221` observaciones, `336` empresas (`RPJ`), `68` columnas de [`panel_financiero_macro_bursatil.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/panel_financiero_macro_bursatil.csv) y las `3,560` observaciones elegibles (`2,869` en `entrenamiento` `2006–2021` y `691` en `prueba` `2022–2025`). Hashes SHA-256 intactos para los `55` archivos previos del proyecto y los `20` archivos de la primera entrega del Sprint 07. |
| **2. Fuente oficial Damodaran y vocabulario (`94` industrias)** | **APROBADO** | Se conserva el HTML congelado de NYU Stern (*Betas by Sector (US)*, January 2026, SHA-256 `10993bab71504e2449ccdd9e3d67fa4da983bed380b2f4486e5200a7b258616b`) y la extracción exacta de las `94` industrias oficiales (excluyendo las filas agregadas de *Total Market*). Todas las etiquetas asignadas pertenecen estrictamente a este vocabulario. |
| **3. Trazabilidad documental (`64` evidencias / `35` fuentes)** | **APROBADO** | Se verificaron independientemente las `40` evidencias PDF (`E001`–`E040`) contra sus archivos `.pdf`/`.txt` locales (hashes SHA-256, página exacta, ancla y extracto literal, `CIIU` documental transcrito e identidad `RPJ`/`RUC`/`NombreEmpresa`) y las `24` evidencias estadísticas MINEM (`M001`–`M024`, `328` celdas empresa-año en `minem24_cap10.xlsx`). |
| **4. Ausencia de fuga temporal, interpolación o clasificación por nombre** | **APROBADO** | Ninguna regla clasifica por coincidencias de texto en `NombreEmpresa`. No se extrapolan códigos `CIIU` de `2023–2025` hacia `2005–2022`, no se interpolan años intermedios sin respaldo documental (`000355` *Cosapi* solo en `2020` y `2024`; `003058` *Enel Generación Piura* deja `2021–2022` pendientes) y las `4` empresas con evidencia en años fuera de su presencia en el panel (`014819`, `000432`, `OE5506`, `B80136`) no transfieren su industria a otros ejercicios. |
| **5. Tratamiento de holdings, banca, RUC y perímetros consolidados** | **APROBADO** | Se valida formalmente el dígito verificador SUNAT en `330` empresas con `RUC` de 11 dígitos sin inventar `RUC` para los `6` emisores extranjeros con centinela `"0"`. Holdings (`UNACEM Corp`, `AENZA`, `Ferreycorp`, `InRetail`), bancos múltiples (`BBVA`, `Interbank`) y estados consolidados (`Nexa Resources Perú`) se mantienen correctamente pendientes de asignación industrial. |
| **6. Cobertura alcanzada y representatividad intrasectorial** | **OBSERVADO** | La cobertura documentada sube de `87` a `442` observaciones (`10.47 %` del panel) y de `7` a `49` empresas (`14.58 %`: `12` completas y `37` parciales) en `13` industrias Damodaran (`15` incluyendo años de referencia fuera del panel). No obstante, el `74.43 %` de las observaciones clasificadas (`329 / 442`) se concentra en `Power` (`24` empresas) y solo `2` industrias en `Soles` (`Power` e `Investments & Asset Management`) superan el umbral mínimo de tamaño muestral para modelado (`muestra_insuficiente == False`). |
| **7. Reproducibilidad, pruebas (`35 / 35`) y formato del notebook** | **APROBADO** | Las `35` pruebas automatizadas (`8` en `test_clasificacion_sectorial.py`, `12` en `test_enriquecimiento_sectorial.py` y `15` previas) se ejecutan en `tesis-fcl` con resultado `OK`. El notebook [`08_clasificacion_sectorial.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/08_clasificacion_sectorial.ipynb) (`44` celdas, `14` de código) cumple las reglas de formato y no ejecuta ningún `.fit(`. |

**Dictamen Final:** **APROBADO CON OBSERVACIONES** *(la arquitectura de dos capas, la verificación criptográfica y textual de fuentes primarias, la disciplina contra la extrapolación temporal y los 35 tests unitarios son técnicamente impecables; las observaciones se refieren al alcance económico de la regla de inversión eléctrica MINEM, un detalle de ordenamiento en el catálogo maestro y la asimetría de cobertura muestral entre industrias que condiciona el diseño del siguiente sprint).*

---

## 2. Verificaciones de Integridad, Datos y Trazabilidad Documental

### 2.1. Conservación del panel y de la primera entrega del Sprint 07
1. **Invarianza del panel integrado y de las particiones del Sprint 06:**
   - La unión de [`catalogo_correspondencias.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_07/catalogo_correspondencias.csv) y de [`catalogo_empresa_anio.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_07/enriquecimiento/catalogo_empresa_anio.csv) con [`panel_financiero_macro_bursatil.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/panel_financiero_macro_bursatil.csv) conserva exactamente las `4,221` filas, `336` empresas (`RPJ`), `68` columnas originales, `3,560` observaciones elegibles (`utilizable_supervisado == True`) y la partición temporal (`2,869` en `entrenamiento` `2006–2021` y `691` en `prueba` `2022–2025`), coincidiendo exactamente con las claves de [`predicciones_baseline.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/predicciones_baseline.csv) (`E0_financiero`).
2. **Preservación bit a bit de archivos previos y de la primera pasada:**
   - Se verificaron los hashes SHA-256 de los `55` archivos protegidos del repositorio (`hashes_bases_previas`), los `20` archivos de la primera entrega (`hashes_primera_entrega`), los `150` archivos de insumo (`hashes_insumos`: PDFs, TXTs, JSONs, XLSXs y XMLs SMV `2005–2025`) y las `15` tablas de salida (`hashes_salidas`) en [`auditoria_enriquecimiento.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_07/enriquecimiento/auditoria_enriquecimiento.json), con `0` discrepancias.
   - Las `87` observaciones clasificadas en la primera entrega (`85` por `D01` en `A.F.P.` y `2` por `D02` en `CIIU 5510`) conservan idénticos valores en las `20` columnas originales dentro de [`catalogo_empresa_anio.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_07/enriquecimiento/catalogo_empresa_anio.csv).

### 2.2. Auditoría de las reglas de clasificación y del corpus primario (`D01`–`D04`, `P01`–`P03`)
| Código de Regla | Descripción y Condición de Aplicación | Observaciones en Panel (`4,221`) | Empresas Únicas (`RPJ`) | Estado |
| :--- | :--- | :---: | :---: | :---: |
| **`D01`** | `TipoSector == 'A.F.P.'` $\rightarrow$ `Investments & Asset Management` (respaldo normativo SBS) | `85` | `6` | **APROBADO** |
| **`D02`** | `ciiu_normalizado == '5510'` y `TipoSector == 'DIVERSOS'` $\rightarrow$ `Hotel/Gaming` (compatible en CIIU Rev. 3.1 y Rev. 4) | `2` | `1` | **APROBADO** |
| **`D03`** | Actividad principal documentada en nota de EE.FF. / memoria anual con entidad, página, pasaje y año explícitos (`certeza == 'Alta'`) | `34` *(incluye `7` con respaldo simultáneo `D04`)* | `19` *(en panel)* + `4` *(fuera de panel)* | **APROBADO** |
| **`D04`** | Actividad eléctrica en cuadro 10.17 del Anuario MINEM 2024 con inversión ejecutada $> 0$ + `TipoSector == 'SERVICIOS PUBLICOS'` en el mismo ejercicio $\rightarrow$ `Power` | `321` *(+ `7` asignadas bajo `D03` = `328` celdas MINEM)* | `24` | **OBSERVADO** |
| **`P01`** | `CIIU` ausente en el panel y `TipoSector` insuficiente sin evidencia documental para ese ejercicio | `3,475` | `314` | **APROBADO** |
| **`P02`** | `CIIU` informado en el panel pero sin revisión declarada o con correspondencia múltiple y sin evidencia documental para ese ejercicio | `304` | `164` | **APROBADO** |
| **`P03`** | Bloqueo preventivo ante cambio de `TipoSector` o múltiples `RUC` en un mismo `RPJ` (`0` casos activos en el panel, verificado por prueba unitaria) | `0` | `0` | **APROBADO** |

### 2.3. Comparación de cobertura entre entregas e industrias identificadas
La tabla [`comparacion_cobertura.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_07/enriquecimiento/comparacion_cobertura.csv) refleja con exactitud el avance de la segunda pasada:

| Indicador | Primera Pasada (`sprint07-v1`) | Ampliación Documental (`sprint07-documental-v1`) | Diferencia |
| :--- | :---: | :---: | :---: |
| Empresas totales (`RPJ`) | `336` | `336` | `0` |
| Observaciones totales (`2005–2025`) | `4,221` | `4,221` | `0` |
| Empresas completamente clasificadas | `6` (`1.79 %`) | `12` (`3.57 %`) | `+6` |
| Empresas parcialmente clasificadas | `1` (`0.30 %`) | `37` (`11.01 %`) | `+36` |
| Empresas sin observaciones clasificadas (`Pendiente`) | `329` (`97.92 %`) | `287` (`85.42 %`) | `-42` |
| Empresas con alguna observación clasificada | `7` (`2.08 %`) | `49` (`14.58 %`) | `+42` |
| Observaciones clasificadas | `87` (`2.06 %`) | `442` (`10.47 %`) | `+355` |
| Observaciones pendientes | `4,134` (`97.94 %`) | `3,779` (`89.53 %`) | `-355` |
| Industrias Damodaran presentes en observaciones del panel | `2` | `13` *(+ `2` en años fuera de panel = `15`)* | `+11` |

Detalle de las **`13` industrias Damodaran** con observaciones clasificadas en el panel ([`distribucion_industria.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_07/enriquecimiento/distribucion_industria.csv)):

| Industria Damodaran | Moneda | Empresas (`RPJ`) | Obs. Panel | Años Cubiertos | Train Elegible | Test Elegible | Mediana `FCL_preliminar` | Muestra Insuficiente |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `Power` | `Soles` | 21 | 261 | 20 (`2005–2024`) | 202 | 48 | `33,429.5` | **No (`False`)** |
| `Power` | `D lares` | 7 | 68 | 20 (`2005–2024`) | 55 | 5 | `41,840.5` | Sí (`test < 10`) |
| `Investments & Asset Management` | `Soles` | 6 | 85 | 21 (`2005–2025`) | 63 | 16 | `102,031.0` | **No (`False`)** |
| `Metals & Mining` | `D lares` | 4 | 5 | 2 (`2024–2025`) | 0 | 3 | `110,108.0` | Sí |
| `Metals & Mining` | `Soles` | 1 | 2 | 2 (`2023–2024`) | 0 | 2 | `66,624.5` | Sí |
| `Food Processing` | `Soles` | 3 | 4 | 2 (`2023–2024`) | 0 | 4 | `60,706.5` | Sí |
| `Food Processing` | `D lares` | 1 | 2 | 2 (`2023–2024`) | 0 | 2 | `-5,371.5` | Sí |
| `Building Materials` | `Soles` | 1 | 2 | 2 (`2023–2024`) | 0 | 2 | `132,461.5` | Sí |
| `Engineering/Construction` | `Soles` | 1 | 2 | 2 (`2020, 2024`) | 1 | 0 | `-62,194.5` | Sí |
| `Financial Svcs. (Non-bank & Insurance)` | `Soles` | 2 | 2 | 1 (`2024`) | 0 | 2 | `207,039.0` | Sí |
| `Hotel/Gaming` | `Soles` | 1 | 2 | 2 (`2024–2025`) | 0 | 1 | `2,090.0` | Sí |
| `Insurance (Life)` | `Soles` | 1 | 2 | 2 (`2024–2025`) | 0 | 1 | `345,900.0` | Sí |
| `Retail (General)` | `Soles` | 1 | 2 | 2 (`2023–2024`) | 0 | 2 | `401,288.0` | Sí |
| `Machinery` | `Soles` | 1 | 1 | 1 (`2024`) | 0 | 1 | `-3,611.0` | Sí |
| `Precious Metals` | `Soles` | 1 | 1 | 1 (`2024`) | 0 | 1 | `612,578.0` | Sí |
| `Steel` | `Soles` | 1 | 1 | 1 (`2024`) | 0 | 1 | `33,720.0` | Sí |
| `Pendiente de revisión` | `D lares` | 51 | 449 | 21 (`2005–2025`) | 298 | 82 | `18,659.0` | No (categoría pendiente) |
| `Pendiente de revisión` | `Soles` | 305 | 3,330 | 21 (`2005–2025`) | 2,250 | 518 | `6,313.0` | No (categoría pendiente) |

---

## 3. Errores Críticos

**Ninguno (`0` errores críticos).**
No existen pérdidas de filas, duplicaciones `(RPJ, Ejercicio)`, alteraciones de importes financieros o de particiones de entrenamiento/prueba, invenciones de códigos `CIIU` o `RUC`, clasificaciones por nombre ni extrapolaciones de evidencia contemporánea hacia años no respaldados.

---

## 4. Errores Importantes

**Ninguno (`0` errores importantes).**
Todos los controles de integridad, trazabilidad de pasajes PDF y celdas XLSX, preservación de archivos anteriores y pruebas unitarias (`35 / 35`) se cumplen rigurosamente.

---

## 5. Observaciones Menores y Puntos de Juicio Metodológico

1. **Naturaleza de la regla `D04` (inversión ejecutada positiva en el cuadro 10.17 del MINEM) y huecos intermedios (`OBSERVADO`):**
   - La regla `D04` explica `321` de las `355` nuevas observaciones clasificadas (`90.4 %` del aumento) exigiendo simultáneamente `TipoSector == 'SERVICIOS PUBLICOS'` e inversión ejecutada estrictamente positiva (`> 0`) en el cuadro 10.17 del Anuario Estadístico de Electricidad 2024 del MINEM.
   - Si bien esta condición evita asignar empresas que solo figuran nominalmente sin actividad en ese año, tiene dos consecuencias metodológicas importantes:
     - Empresas eléctricas en operación continua quedan como `Pendiente` en ejercicios puntuales donde su inversión reportada en el cuadro 10.17 fue `0` o nula (p. ej., `SP0008` *Red de Energía del Perú* tiene `19 / 21` años clasificados porque `2022` no registra inversión positiva en la celda correspondiente; `B40002` *Hidrandina* tiene `19 / 21` años porque `2015` está vacío; `003058` *Enel Generación Piura* queda sin asignar en `2021–2022`).
     - Ninguna de las `24` empresas eléctricas recibe clasificación por `D04` en el ejercicio `2025` porque la serie del Anuario MINEM 2024 termina en `2024` (por ello `002829` *ENGIE*, `B40008` *Luz del Sur* y `B40013` *Electro Dunas* tienen `20 / 21` observaciones clasificadas `2005–2024` y `1` observación pendiente en `2025`).
2. **Criterio de selección de la evidencia de referencia y etiqueta de `estado_temporal` en [`master_catalog`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/enriquecimiento_sectorial.py#L273-L317) (`OBSERVADO`):**
   - En [`src/enriquecimiento_sectorial.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/enriquecimiento_sectorial.py#L280), cuando una empresa posee múltiples evidencias en `evidencias_actividad.csv`, la fila de resumen del catálogo maestro se elige con `current = e.sort_values(['anio_referencia', 'evidencia_id']).iloc[-1]`.
   - Para las `5` empresas eléctricas que cuentan tanto con estados financieros auditados PDF en `2024` (`E007`, `E008`, `E009`, `E010`, `E039`) como con serie MINEM hasta `2024` (`M001`, `M016`, `M014`, `M013`, `M002`), el orden alfabético `'M...' > 'E...'` hace que `catalogo_maestro_empresas.csv` muestre como `actividad_principal_documentada` y `fuente_actividad` la descripción genérica del XLSX MINEM en lugar de la nota de los EE.FF. auditados (mientras que en `catalogo_empresa_anio.csv` sí se prioriza correctamente `D03` sobre `D04`).
   - Asimismo, en la línea 305 (`e.actividad_principal.nunique() == 1`), dado que el texto de `actividad_principal` del PDF y el del XLSX difieren en redacción aunque ambos mapean a `Power`, esas `5` empresas reciben `estado_temporal = 'Actividades compatibles en ejercicios documentados; huecos pendientes'` incluso cuando `2005–2024` es un bloque continuo sin huecos intermedios (`002829`, `B40008`, `B40013`).
3. **Fila inactiva duplicada de `B40002` (*Hidrandina*) en [`correspondencias_minem.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/raw/sectorial_documental/correspondencias_minem.csv) (`OBSERVADO`):**
   - El archivo `correspondencias_minem.csv` contiene `25` filas para `24` `RPJ` únicos porque `B40002` (*Hidrandina*) está listado tanto en la hoja `10.17.2 Inversion Privada` (fila `161`, donde solo tuvo datos antes de `2005`) como en `10.17.3 y 4 Publica y Gub` (fila `35`, que genera la evidencia `M023` para `2005–2024`). Aunque [`regulatory_evidence`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/enriquecimiento_sectorial.py#L143-L144) descarta limpiamente la fila sin celdas positivas en `2005–2025`, se recomienda documentar o depurar ese registro inactivo en futuras versiones del manifiesto.
4. **Coexistencia de dos notebooks con prefijo `08_` en `notebooks/` (`OBSERVADO`):**
   - El notebook [`notebooks/08_clasificacion_sectorial.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/08_clasificacion_sectorial.ipynb) coexiste con [`notebooks/08_mejoras_baseline.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/08_mejoras_baseline.ipynb) del Sprint 06 para cumplir literalmente el nombre solicitado sin destruir entregables previos. Se deja constancia de que [`notebooks/09_informe_sprint_06.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/09_informe_sprint_06.ipynb) (Celda 1) buscaba `p.name[:2] in ["02","03","04","05","06","07","08"]` esperando `7` archivos `.ipynb` al cierre del Sprint 06.
5. **Archivo residual sin seguimiento en la raíz del repositorio (`OBSERVADO`):**
   - Permanece en la raíz del proyecto el archivo no rastreado `"pace=-blank-at-eol diff --cached --check"` (`15,915` bytes, del 21 de octubre) y el directorio vacío `reports/sectorial/`, ajenos a los entregables formales del Sprint 07.

---

## 6. Auditoría de Reproducibilidad y Pruebas Automatizadas

1. **Ejecución de la suite completa de pruebas en `tesis-fcl`:**
   - Se ejecutaron las `35` pruebas automatizadas del repositorio mediante `/home/ricardo/miniconda3/envs/tesis-fcl/bin/python -m unittest discover -s tests -p "test_*.py" -v`:
     - `8` pruebas de [`tests/test_clasificacion_sectorial.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_clasificacion_sectorial.py) (`SectorialTest`)
     - `12` pruebas de [`tests/test_enriquecimiento_sectorial.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_enriquecimiento_sectorial.py) (`DocumentaryTest`)
     - `15` pruebas previas (`DeliveryTest`, `FeaturesTest`, `TraceTest`)
   - Resultado: **`Ran 35 tests — OK`**, verificando reproducción byte a byte en directorio temporal sin conexión de red ni dependencia de `pypdf`.
2. **Verificación del notebook [`notebooks/08_clasificacion_sectorial.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/08_clasificacion_sectorial.ipynb):**
   - Contiene `44` celdas (`14` celdas de código con `execution_count = 1..14` y `30` celdas Markdown), todas ejecutadas sin errores ni advertencias, sin encabezados `#`, sin numeración en los títulos en negrita y sin llamadas a `.fit(`.

---

## 7. Recomendaciones para el Siguiente Sprint

1. **Estrategia de modelado jerárquico por Macrosector / Sector SMV antes que por industria Damodaran aislada:**
   - Dado que `11` de las `13` industrias Damodaran presentes en el panel tienen entre `1` y `7` observaciones (`0` a `4` observaciones en prueba) y `3,779` observaciones (`89.53 %`) siguen en `Pendiente de revisión`, **no es estadísticamente viable entrenar modelos independientes por industria Damodaran** salvo, de forma exploratoria en `Soles`, para `Power` (`n_train = 202`, `n_test = 48`) e `Investments & Asset Management` (`n_train = 63`, `n_test = 16`).
   - Para el universo corporativo no financiero, se recomienda utilizar en el siguiente sprint la jerarquía de **Macrosector enriquecido** (`Industrial`, `Servicios públicos`, `Agroindustrial`, `Extractivo`, manteniendo `DIVERSOS`/pendientes separados y excluyendo `Financiero` del proxy `FCL = FCO + CAPEX`).
2. **Priorización documental para ampliar cobertura histórica en `2006–2021`:**
   - Dado que las notas de EE.FF. de `2023–2025` (`D03`) solo cubren ejercicios recientes (que caen mayoritariamente en la partición `prueba` `2022–2025`), para que una clasificación industrial alimente el entrenamiento supervisado (`2006–2021`) sin fuga temporal se requieren series sectoriales históricas oficiales adicionales (p. ej., anuarios históricos MINEM de minería metálica/no metálica, estadísticas de producción industrial PRODUCE o memorias SMV de ejercicios `2006–2021`).

---

## 8. Dictamen Final

- **Estado de la auditoría del Sprint 07:** **APROBADO CON OBSERVACIONES**
- **Justificación:** La implementación del Sprint 07 y su capa de enriquecimiento documental cumplen rigurosamente todos los controles de integridad, trazabilidad hacia documentos primarios (PDFs SMV y series XLSX MINEM), invarianza de datos financieros y particiones temporales, reproducción determinista byte a byte y validación mediante `35` pruebas automatizadas. Las observaciones documentadas son de carácter metodológico y de cobertura muestral, y están explícitamente reconocidas en los entregables del sprint.

