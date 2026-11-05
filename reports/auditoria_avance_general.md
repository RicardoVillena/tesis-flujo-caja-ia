# Informe Consolidado de Auditoría Independiente — Avance General (Sprint 07 Fase 3, Sprint 08, Sprint 09 e IA07)

**Fecha de auditoría:** 4 de noviembre de 2026  
**Proyecto:** `tesis-flujo-caja-ia`  
**Rama evaluada:** `sprint-09-variantes-importancia` (`HEAD` en `c6bb6df` + cambios locales en `src/optimizacion_hiperparametros.py` y `tests/test_optimizacion_hiperparametros.py`)

---

## 1. Índice de Informes de Auditoría Grabados en Local

| Etapa / Sprint | Informe de Auditoría Local | Dictamen |
|---|---|---|
| **Sprint 06 (Baseline, Mejoras e Informe)** | [`reports/sprint_06/auditoria_baseline_variantes.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/auditoria_baseline_variantes.md), [`reports/sprint_06/auditoria_mejoras_baseline.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/auditoria_mejoras_baseline.md), [`reports/sprint_06/auditoria_informe_sprint_06.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_06/auditoria_informe_sprint_06.md) | **APROBADO CON OBSERVACIONES** |
| **Sprint 07 (Clasificación y Enriquecimiento Sectorial Damodaran)** | [`reports/auditoria_clasificacion_sectorial.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/auditoria_clasificacion_sectorial.md) | **APROBADO** |
| **Sprint 08 (Auditoría de Calidad, Ablación y Comparación de Modelos)** | [`reports/sprint_08/auditoria_sprint_08.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/auditoria_sprint_08.md) | **APROBADO CON OBSERVACIONES** |
| **Sprint 09 (Variantes E0–E4, Importancia, Alineación y Experimento Final)** | [`reports/sprint_09/auditoria_sprint_09.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/auditoria_sprint_09.md) | **APROBADO CON OBSERVACIONES** |
| **Sesión IA07 (Random Search vs. Optuna TPE en Ridge)** | [`reports/ia07/auditoria_optimizacion_hiperparametros.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/auditoria_optimizacion_hiperparametros.md) | **APROBADO CON OBSERVACIONES** |

---

## 2. Síntesis de Verificaciones Transversales

1. **Inmutabilidad del panel integrado y particiones (APROBADO):**
   - [`data/processed/panel_financiero_macro_bursatil.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/data/processed/panel_financiero_macro_bursatil.csv) conserva sus `4,221` observaciones, `68` columnas, `3,560` filas supervisadas (`2,869` de entrenamiento con `anio_objetivo <= 2021` y `691` de prueba con `anio_objetivo` en `2022–2025`) y su hash SHA-256 `c0a116958c422ffc93daa218b5cc1f47e85831a7137e029f312fee5b6d0b4b2c`.
2. **Protocolos pre-registrados con hash SHA-256 (APROBADO):**
   - [`reports/sprint_09/protocolo.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/protocolo.json): `5b69af836d7400d0…`
   - [`reports/sprint_09/alineacion_investigacion/protocolo.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/alineacion_investigacion/protocolo.json): `99fee593141b0a38…`
   - [`reports/sprint_09/experimento_final/protocolo.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/experimento_final/protocolo.json): `c2430bd4105ac528…`
   - [`reports/ia07/protocolo.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/protocolo.json): `27433742dcd1b9e1…`
   - [`reports/ia07/seleccion_congelada.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/seleccion_congelada.csv): `9ee2e553a717bd57…` (congelada antes de evaluar la partición de prueba).
3. **Ausencia de fuga de información temporal y de prueba (APROBADO):**
   - En los Sprints 08 y 09 no se utiliza la partición de prueba `2022–2025`.
   - En todas las etapas con validación temporal (`Sprint 08`, `Sprint 09`, `IA07`), la imputación por mediana, el recorte por cuantiles (`ClipRatios`), el escalado (`StandardScaler` / `RobustScaler`) y las transformaciones del objetivo se ajustan exclusivamente sobre el subconjunto de entrenamiento de cada ventana temporal.
4. **Exactitud matemática de métricas y determinismo (APROBADO):**
   - Todas las tablas de métricas en [`reports/sprint_08/`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_08/), [`reports/sprint_09/`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/) y [`reports/ia07/`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/) fueron recalculadas independientemente a partir de los archivos `predicciones*.csv`, coincidiendo hasta precisión de punto flotante ($\le 6.33 \times 10^{-8}$ en RMSE/MAE y $\le 1.15 \times 10^{-14}$ en $R^2$).
5. **Ejecución de los Notebooks 10 al 15 (APROBADO CON OBSERVACIONES MENORES):**
   - Los 6 notebooks ([`10`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/sprint_07/10_clasificacion_sectorial.ipynb), [`11`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/sprint_08/11_auditoria_calidad_atributos.ipynb), [`12`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/sprint_08/12_ablacion_variables.ipynb), [`13`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/sprint_08/13_comparacion_modelos.ipynb), [`14`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/sprint_09/14_presentacion_resultados.ipynb) y [`15`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/ia07/15_optimizacion_hiperparametros.ipynb)) tienen todas sus celdas ejecutadas en orden consecutivo `1..N` y `0` errores en sus salidas.

---

## 3. Pendientes Puntuales Identificados

1. **En Sesión IA07:** Reejecutar `--analizar` (`~/.venvs/tesis-fcl-ia07/bin/python scripts/reproduce_optimizacion_hiperparametros.py --analizar`) para que [`reports/ia07/comparacion_metodos.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/comparacion_metodos.csv) y [`reports/ia07/comparacion_metodos_agregada.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/comparacion_metodos_agregada.csv) incorporen en disco las nuevas columnas `p_wilcoxon` y `p_wilcoxon_holm` ya añadidas en [`src/optimizacion_hiperparametros.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/optimizacion_hiperparametros.py#L334-L377), y actualizar [`informe_resultados.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/informe_resultados.md), [`15_optimizacion_hiperparametros.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/ia07/15_optimizacion_hiperparametros.ipynb) y [`registro_pruebas.txt`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/registro_pruebas.txt) (`30` pruebas).
2. **En Índice de Notebooks:** Agregar la entrada de [`notebooks/sprint_09/14_presentacion_resultados.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/sprint_09/14_presentacion_resultados.ipynb) en [`notebooks/README.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/README.md).
3. **En Pruebas de Integridad Histórica:** Definir antes del cierre final si se actualizan las huellas de referencia en los 3 tests históricos que detectan la edición posterior de [`notebooks/03_extraccion_macroeconomica.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/03_extraccion_macroeconomica.ipynb) y [`notebooks/README.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/README.md).

---

## 4. Dictamen General

**DICTAMEN GENERAL: APROBADO CON OBSERVACIONES**

