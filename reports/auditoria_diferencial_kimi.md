# Informe de Auditoría Diferencial — Cambios Locales y Correcciones de Kimi

**Fecha:** 5 de noviembre de 2026  
**Rama:** `sprint-09-variantes-importancia`  
**Proyecto:** `tesis-flujo-caja-ia`  
**Tipo de auditoría:** Auditoría diferencial de cambios locales no confirmados (`git diff` vs. `HEAD`).

---

## 1. Resumen de Archivos Auditados

| Archivo | Cambio Realizado | Estado Científico | Dictamen |
|---|---|---|:---:|
| [`src/optimizacion_hiperparametros.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/optimizacion_hiperparametros.py) | Incorpora función [`_wilcoxon_pareada()`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/optimizacion_hiperparametros.py#L334-L339) y emparejamiento por semilla en [`analizar_convergencia()`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/src/optimizacion_hiperparametros.py#L342-L377). Mantiene intacto el algoritmo de búsqueda, congelación y evaluación en prueba. | Sin alteración de modelos ni particiones | **APROBADO** |
| [`tests/test_optimizacion_hiperparametros.py`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/tests/test_optimizacion_hiperparametros.py) | Añade 4 pruebas unitarias dedicadas a Wilcoxon (diferencias nulas, desplazamientos sintéticos, monotonicidad Holm y control de pareja de semillas). | Cobertura exacta de casos límite | **APROBADO** |
| [`reports/ia07/comparacion_metodos.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/comparacion_metodos.csv) | Conserva las 80 claves exactas y los mismos valores numéricos en las 12 columnas originales (0 discrepancias). Añade `p_wilcoxon` y `p_wilcoxon_holm`. | Resultados originales 100% preservados | **APROBADO** |
| [`reports/ia07/comparacion_metodos_agregada.csv`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/comparacion_metodos_agregada.csv) | Conserva las 5 claves y valores originales. Añade columnas de recuento de estudios significativos según Wilcoxon. | Consistente con el archivo detallado | **APROBADO** |
| [`reports/ia07/informe_resultados.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/informe_resultados.md) | Actualiza la tabla de convergencia con las columnas de Wilcoxon pareado y precisa que 13 ms y 17 ms son medianas (medias: 23 ms y 27 ms). | Documentación coherente con los CSV | **APROBADO** |
| [`reports/ia07/entorno.json`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/ia07/entorno.json) | Actualiza el hash de `git_head` al commit `c6bb6df` tras regenerar `--analizar`. | Metadato de entorno | **APROBADO** |
| [`reports/sprint_09/experimento_final/resumen_tecnico.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/reports/sprint_09/experimento_final/resumen_tecnico.md) | Documenta hiperparámetros del profesor (espacios de búsqueda, parámetros fijos, selección interna temporal y tabla de 60 configuraciones seleccionadas con escape de barras `\|`). | Información de trazabilidad solicitada | **APROBADO** |
| [`notebooks/README.md`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/README.md) | Agrega sección del Sprint 09 (`notebooks/sprint_09/14_presentacion_resultados.ipynb`). | Índice completo | **APROBADO** |
| [`notebooks/sprint_09/14_presentacion_resultados.ipynb`](file:///home/ricardo/proyectos/tesis-flujo-caja-ia/notebooks/sprint_09/14_presentacion_resultados.ipynb) | Restaurado limpio a `HEAD`. Cuaderno intacto con todas sus salidas científicas originales verificadas. | Sin modificaciones pendientes | **APROBADO** |

---

## 2. Verificaciones Clave

1. **Inmutabilidad de datos y pruebas congeladas:**
   - Panel base `data/processed/panel_financiero_macro_bursatil.csv`: SHA-256 `c0a11695…` intacto.
   - Selección congelada `reports/ia07/seleccion_congelada.csv`: SHA-256 `9ee2e553…` intacto.
   - Predicciones y métricas de prueba en `reports/ia07/` y `reports/sprint_09/experimento_final/`: sin cambios.
2. **Formato Markdown de tablas:**
   - La tabla de configuraciones en `resumen_tecnico.md` cuenta con exactamente 5 columnas en sus 60 filas, renderizando sin descuadres.
3. **Cero procesos en ejecución:**
   - No quedan tareas en segundo plano ni cuadernos ejecutándose.

---

## 3. Dictamen Final

**DICTAMEN: APROBADO**  
Los cambios locales se encuentran debidamente verificados, sin riesgo científico y grabados en el disco local para su revisión.

