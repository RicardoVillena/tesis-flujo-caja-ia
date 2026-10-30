# Sprint 08 — Entrega final

Auditoría de calidad de los 26 atributos de E2, evaluación de retirada de variables y comparación exploratoria de modelos para el FCL preliminar t+1. Solo usa entrenamiento (años objetivo ≤ 2021), con soles y dólares por separado.

## Leer primero

1. [informe_final_sprint_08.md](informe_final_sprint_08.md): informe consolidado con conclusiones por moneda.
2. [estado_verificacion.md](estado_verificacion.md): estado de las pruebas y los fallos históricos con su causa.

## Resultados finales y antecedentes

| Etapa | Estado | Informe | Decisión o resultado clave |
|---|---|---|---|
| 1. Auditoría de calidad | Final | [resumen_auditoria.md](resumen_auditoria.md) | [hallazgos_calidad.csv](hallazgos_calidad.csv), [tabla_26_atributos.csv](tabla_26_atributos.csv), [auditoria_temporal.csv](auditoria_temporal.csv) |
| 2a. Ablación individual y primera validación anidada | Antecedente | [ablacion/informe_ablacion.md](ablacion/informe_ablacion.md) | [ablacion/resumen_ablacion.csv](ablacion/resumen_ablacion.csv), [ablacion/anidada_resumen.csv](ablacion/anidada_resumen.csv) |
| 2b. Revisión de la validación anidada | **Final (variables)** | [ablacion_revision/informe_revision.md](ablacion_revision/informe_revision.md) | [ablacion_revision/decision_final.csv](ablacion_revision/decision_final.csv) |
| 3. Comparación de modelos | **Final (modelado)** | [comparacion_modelos/informe_comparacion.md](comparacion_modelos/informe_comparacion.md) | [comparacion_modelos/decision.csv](comparacion_modelos/decision.csv) |

Instrucciones originales de la Etapa 1: [instrucciones_claude.md](instrucciones_claude.md).

## Notebooks

| Notebook | Función |
|---|---|
| [11_auditoria_calidad_atributos.ipynb](../../notebooks/sprint_08/11_auditoria_calidad_atributos.ipynb) | Auditoría de calidad (Etapa 1) |
| [12_ablacion_variables.ipynb](../../notebooks/sprint_08/12_ablacion_variables.ipynb) | Ablación individual y primera validación anidada |
| [13_comparacion_modelos.ipynb](../../notebooks/sprint_08/13_comparacion_modelos.ipynb) | Comparación de modelos |

La revisión 2b no tiene notebook; se ejecuta con su script. Hay un índice general en [notebooks/README.md](../../notebooks/README.md).

## Reproducción

**Entorno:** el existente `tesis-fcl` (`/home/ricardo/miniconda3/envs/tesis-fcl`): Python 3.12.15, scikit-learn 1.9.1, numpy 2.5.4, pandas 3.0.6. No se instalan paquetes. Sin red. Los notebooks usan el kernel `tesis-fcl`. Los comandos se lanzan desde la raíz del repositorio.

| Etapa | Comando | Regenera y escribe en | Depende de |
|---|---|---|---|
| 1 | `python scripts/reproduce_auditoria_calidad.py` (o el notebook 11) | `reports/sprint_08/*.csv`, `resumen_auditoria.md`, `integridad.json`, `especificacion_e2.json`; no escribe `referencia_integridad_previa.csv` ni los registros de pruebas | Datos procesados y notebook 07 (solo lectura) |
| 2a | `python scripts/reproduce_ablacion_variables.py` (o el notebook 12) | `reports/sprint_08/ablacion/` (salvo `pruebas_automatizadas.txt`) | Igual que la Etapa 1 y `reports/sprint_06/` (solo lectura) |
| 2b | `python scripts/reproduce_ablacion_variables.py --revision` | `reports/sprint_08/ablacion_revision/` (salvo `pruebas_automatizadas.txt`) | Lee `reports/sprint_08/ablacion/` para comparar con la ejecución anterior |
| 3 | `python scripts/reproduce_comparacion_modelos.py` (o el notebook 13) | `reports/sprint_08/comparacion_modelos/` (salvo `pruebas_automatizadas.txt`) | Lee `reports/sprint_08/ablacion_revision/predicciones_externas.csv` para verificar la reproducción |
| Pruebas | `python -m unittest tests.test_auditoria_calidad tests.test_ablacion_variables tests.test_comparacion_modelos -v` | Solo directorios temporales | — |

Para verificar sin tocar los entregables, se pueden llamar las funciones `run(<directorio temporal>)` de `src/auditoria_calidad.py`, `src/ablacion_variables.py` (`run` y `run_revision`) y `src/comparacion_modelos.py`. Es lo que hacen las pruebas.

**Limitaciones conocidas de la reproducción:**
- **Integridad y estado del repositorio:**
  - `integridad.json` (en todas las etapas) y la sección de integridad de `resumen_auditoria.md` dependen del estado del repositorio, es decir, de cuántos archivos hay y de cuáles tienen cambios sin commit.
  - Regenerarlos con el árbol actual cambia esos campos respecto a la versión archivada, aunque los datos, las predicciones y las métricas no cambien.
  - La Etapa 1 se archivó antes de las modificaciones sin commit descritas en [estado_verificacion.md](estado_verificacion.md).
- **Tiempos:** `comparacion_modelos/tiempos_ajuste.csv` no es determinista.
- **Alcance de la reproducción:** la verificada es la de este entorno, comprobada por las pruebas con dos ejecuciones idénticas byte a byte. No está comprobada en otras máquinas ni con otras versiones de las bibliotecas.
- **Escritura:** regenerar una etapa sobrescribe su carpeta archivada. Para auditar, conviene usar un directorio temporal.
