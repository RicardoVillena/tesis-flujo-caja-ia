# Informe de Auditoría Técnica y Metodológica — Integración de Datos Financieros y Macroeconómicos (`04_integracion_datos.ipynb`)

**Proyecto:** `tesis-flujo-caja-ia` — *Tesis de Maestría en Inteligencia Artificial (UNI)*  
**Archivo principal auditado:** `notebooks/04_integracion_datos.ipynb` (`SHA-256: c54c169d0e22a172618a31375eb0a16caa3fcfcb3ad79549bdfa782cf2676bd9`)  
**Entregables auditados:**  
- `data/processed/panel_financiero_macroeconomico.csv` (`4221 × 62`, `SHA-256: 435148cba6e72380fd96ee809bc7cd8a0875ae629b9c12b04254bf71d38bde99`)  
- `reports/diccionario_integracion_datos.csv` (`62 × 20`, `SHA-256: ae8c34447e21feb48a2d1b5b88e8548935915c1eac421cc046fa3e468a2c1abd`)  
- `reports/validacion_integracion_datos.json` (`SHA-256: d6e729eb8f2a973062cac6f88a1214d54bc6ce33406e08f7b3a6f54ec0c1f4ad`)  
**Entradas verificadas:**  
- `data/processed/features_financieras.csv` (`4221 × 57`, `SHA-256: 0a9cafca02a4272210863c01fdd79f7e1a50573099e5779d09955e19adea5702`)  
- `data/processed/macroeconomia_peru_2005_2025.csv` (`21 × 6`, `SHA-256: 7dba8aec32f8eae7086b2cb393f7c22d9741314893bef1f8d081bc8d91b1377e`, generado por `notebooks/03_extraccion_macroeconomica.ipynb`, dictamen vigente: **APROBADO**)  
**Rama Git:** `sprint-06-data-modeling` (`HEAD -> 485d2ce`)  
**Fecha de auditoría (re-evaluación tras levantamiento de observaciones):** 21 de octubre de 2026  
**Rol:** Auditor Senior Independiente (Python, Ciencia de Datos, Econometría y Machine Learning)

---

## 1. Resumen Ejecutivo

Se realizó la re-auditoría integral e independiente del cuaderno `notebooks/04_integracion_datos.ipynb` y de sus tres artefactos exportados (`data/processed/panel_financiero_macroeconomico.csv`, `reports/diccionario_integracion_datos.csv` y `reports/validacion_integracion_datos.json`), comprobando que Codex **subsanó satisfactoriamente la totalidad de los hallazgos importantes y observaciones** reportados en la revisión previa (`IMP-INT-01`, `IMP-INT-02`, `OBS-INT-01` y `OBS-INT-02`):

1. **Subsanación de `IMP-INT-01` (Incorporación de `crecimiento_pbi_real_pct` y separación de roles):** El panel consolidado `data/processed/panel_financiero_macroeconomico.csv` ahora integra las **5 series macroeconómicas** (`4221 × 62`), incluyendo `crecimiento_pbi_real_pct` (`PM04863AA`). Además, excluye formalmente a `pbi_real_millones_soles_2007` de la lista de predictores automáticos (`PREDICTORES_MACRO` contiene únicamente `inflacion_lima_dic_dic_pct`, `tipo_cambio_promedio_soles_usd`, `tasa_referencia_promedio_pct` y `crecimiento_pbi_real_pct`).
2. **Subsanación de `IMP-INT-02` (Catálogo consolidado de las 62 variables):** Se genera y exporta `reports/diccionario_integracion_datos.csv` (`62` variables), que unifica sin reinterpretación el diccionario financiero (`reports/diccionario_features.md`) y el diccionario macroeconómico (`reports/diccionario_macroeconomia_bcrp.csv`), asignando explícitamente `rol_en_dataset = "fuente"`, `predictor_candidato = False` y `funcion_en_panel = "referencia macroeconomica; excluir de seleccion automatica"` a `pbi_real_millones_soles_2007`.
3. **Rigurosidad contra fuga de información (*data leakage*) en estadísticas descriptivas (Celda 23):** Los estadísticos descriptivos macroeconómicos se calculan exclusivamente sobre los **16 años únicos de la partición de entrenamiento (`2005–2020`)** y se incluye una prueba automatizada de perturbación (`perturbado.loc[perturbado.particion.eq("prueba"), MACRO] * 100 + 1000`) que demuestra invariancia exacta (`check_exact=True`) tanto de las estadísticas como de la regla de selección de predictores frente a cualquier cambio en la partición de prueba.
4. **Integridad relacional, precisión numérica y trazabilidad:** Se verificó celda por celda que las **4,221 filas × 57 columnas financieras originales** se preservan con diferencia numérica $0.0$, conservando exactamente los `20,675` valores faltantes financieros de origen, los identificadores `RPJ` (`336` empresas) y `RUC` (documentando sin alterar las 63 filas de 6 empresas con `RUC == "0"` provenientes del archivo de origen), y verificando mediante hashes `SHA-256` que ningún archivo original (XML de SMV, JSON de BCRP, CSV previos ni notebooks `02` y `03`) fue modificado.

**Dictamen Final:** **APROBADO**

---

## 2. Errores Críticos

No se detectaron errores críticos en el cuaderno `notebooks/04_integracion_datos.ipynb` ni en los datos e informes generados.

---

## 3. Errores Importantes

No persisten errores importantes. Los dos hallazgos de la primera revisión fueron resueltos:

- **`IMP-INT-01` (CORREGIDO — APROBADO):** Se incorporó `crecimiento_pbi_real_pct` al panel integrado (`4221 × 62`) y se restringió `PREDICTORES_MACRO` a las 4 series candidatas (`inflacion_lima_dic_dic_pct`, `tipo_cambio_promedio_soles_usd`, `tasa_referencia_promedio_pct`, `crecimiento_pbi_real_pct`), dejando `pbi_real_millones_soles_2007` únicamente como serie de referencia macroeconómica (`predictor_candidato = False`).
- **`IMP-INT-02` (CORREGIDO — APROBADO):** Se exportó el catálogo completo `reports/diccionario_integracion_datos.csv` (`62` filas, exactamente en el mismo orden de columnas que `panel_financiero_macroeconomico.csv`) con las columnas `rol_en_dataset`, `predictor_candidato` y `funcion_en_panel`, garantizando trazabilidad directa hacia el pipeline de modelado.

---

## 4. Observaciones Menores (Documentadas y Controladas)

1. **Limitación histórica de disponibilidad en tiempo real (*real-time vintage*) y rezago de publicación (Celdas 26 y 29):**
   - El cuaderno documenta con total transparencia que unir por `Ejercicio == anio` ($t$) evita utilizar valores del año objetivo ($t+1$), pero no certifica disponibilidad *point-in-time* libre de revisiones posteriores del BCRP/INEI o de desfases de publicación. Por ello, registra `"disponibilidad_real_historica": "NO_VERIFICADA"` en `reports/validacion_integracion_datos.json`.
2. **Conservación de 63 registros con `RUC == "0"` provenientes de `features_financieras.csv` (Celda 8):**
   - En lugar de alterar o imputar identificadores del archivo de entrada, la Celda 8 detecta y documenta las 63 filas correspondientes a 6 empresas (`B60051`, `CD0010`, `J01554`, `OE2305`, `OE3161`, `OE5087`) cuyo `RUC` en `features_financieras.csv` es `"0"`, preservándolas de forma exacta y dejando constancia en `validacion_integracion_datos.json` (motivo por el cual el campo informativo `estado` se reporta como `"COMPLETADO_CON_OBSERVACIONES"`).
3. **Baja dimensión temporal efectiva en entrenamiento ($T_{\text{train}} = 16$ años únicos, `2005–2020`) y desplazamiento de soporte del tipo de cambio:**
   - Queda explícitamente registrado en la lista `limitaciones` de `reports/validacion_integracion_datos.json` (líneas 586–587) para que sea atendido mediante validación temporal por bloques anuales en la etapa de modelado.

---

## 5. Matriz de Verificación de Auditoría

| Categoría | Verificación realizada | Evidencia / Resultado cuantitativo | Estado |
| :--- | :--- | :--- | :---: |
| **1. Trazabilidad e Inmutabilidad de Entradas** | Verificación de hashes `SHA-256` de `features_financieras.csv`, `macroeconomia_peru_2005_2025.csv`, archivos `raw` (SMV y BCRP) y notebooks previos (`02`, `03`, `EDA`) | Hashes `SHA-256` 100% idénticos antes y después de la ejecución (`archivos_preexistentes_preservados: true`). | **APROBADO** |
| **1. Estado del Notebook 03** | Verificación de integridad de `notebooks/03_extraccion_macroeconomica.ipynb` | `SHA-256: 2a892aee84c14282b215f883e8c6fb6f2194dbdfb752830103157fe40b8f3464` (intacto y **APROBADO**). | **APROBADO** |
| **2. Clave de Unión y Cardinalidad** | Unión `left` con `validate="many_to_one"` por `Ejercicio == anio` ($t$) | `4,221` filas de entrada $\to$ `4,221` filas de salida (`62` columnas: `57` financieras + `5` macroeconómicas); `336` empresas (`RPJ`); orden de filas 100% preservado. | **APROBADO** |
| **2. Prevención de Data Leakage** | Ausencia de cruce con `anio_objetivo` ($t+1$), preservación de particiones e invariancia ante perturbación de prueba | `usa_anio_objetivo = False`; `invariancia_ante_perturbacion_prueba = True`; estadísticos calculados solo en `entrenamiento` ($T_{\text{train}} = 16$ años: `2005–2020`). | **APROBADO** |
| **2. Tratamiento de Series Macro y Roles** | Inclusión de `crecimiento_pbi_real_pct` y exclusión de `pbi_real_millones_soles_2007` como predictor automático (`IMP-INT-01` / `IMP-INT-02`) | `PREDICTORES_MACRO` tiene las 4 series candidatas; `pbi_real_millones_soles_2007` queda con `rol_en_dataset = "fuente"` y `predictor_candidato = False` en `diccionario_integracion_datos.csv`. | **APROBADO** |
| **3. Precisión Numérica y Faltantes** | Verificación celda por celda (`4221 × 62`) de valores `float64` (`float_precision="round_trip"`), `RPJ`/`RUC` y conteo de nulos | Diferencia numérica máxima $= 0.0$ en las 57 columnas financieras y en las 5 macroeconómicas; `20,675` faltantes financieros conservados; `0` faltantes macroeconómicos. | **APROBADO** |
| **4. Documentación del Notebook** | Revisión de las 31 celdas (título general + 10 bloques `[Markdown título/desc] -> [Código] -> [Markdown interpretación]`) | Los 10 bloques tienen `execution_count` secuencial (`1..10`), título numerado en negrita (`**1. ...**` a `**10. ...**`), descripción de 2 líneas e interpretación breve posterior. | **APROBADO** |
| **5. Datos y Metadatos Generados** | Verificación de `panel_financiero_macroeconomico.csv`, `diccionario_integracion_datos.csv` y `validacion_integracion_datos.json` | Coherencia 100% verificada entre el panel (`4221 × 62`), el catálogo (`62` variables) y el reporte JSON de validación. | **APROBADO** |
| **6. Arquitectura y Git** | Respeto de estructura del repositorio, rutas relativas compatibles con Linux/WSL y ausencia de credenciales o archivos basura | Rutas relativas limpias mediante `Path`; ningún archivo previo alterado. | **APROBADO** |

---

## 6. Recomendaciones para la Siguiente Etapa (Modelado Supervisado)

No quedan correcciones pendientes sobre `03_extraccion_macroeconomica.ipynb` ni sobre `04_integracion_datos.ipynb`. Para el siguiente cuaderno de modelado predictivo se recomienda:
1. Consumir directamente `reports/diccionario_integracion_datos.csv` filtrando `predictor_candidato == True` para construir la matriz de diseño $X$, asegurando que `pbi_real_millones_soles_2007` permanezca excluido como predictor automático.
2. Utilizar esquemas de validación cruzada temporal por bloques anuales (*expanding window* sobre `Ejercicio`) acordes con los $T_{\text{train}} = 16$ años únicos de entrenamiento (`2005–2020`).

---

## 7. Dictamen Final

**DICTAMEN:** **APROBADO**

Tanto `notebooks/03_extraccion_macroeconomica.ipynb` como `notebooks/04_integracion_datos.ipynb` y sus respectivos datasets y diccionarios exportados cumplen íntegramente con los estándares técnicos, estadísticos, econométricos, de prevención de *data leakage* y de documentación exigidos por la auditoría.
