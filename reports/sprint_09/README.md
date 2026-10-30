# Sprint 09 — Variantes de atributos e importancia de variables

Rama `sprint-09-variantes-importancia`. Este sprint evalúa si las variables macroeconómicas y bursátiles mejoran la predicción del FCL preliminar t+1 frente a usar solo variables financieras. Incluye importancia de variables y una propuesta de matriz de consistencia. Todo es exploratorio, solo con entrenamiento (años objetivo ≤ 2021) y con soles y dólares por separado.

## Leer primero

1. [informe_sprint_09.md](informe_sprint_09.md): respuestas a las 6 preguntas y estado de las hipótesis.
2. [matriz_consistencia.md](matriz_consistencia.md): propuesta para revisión académica.
3. [matriz_operacionalizacion.md](matriz_operacionalizacion.md): definiciones, dimensiones, indicadores, medición, unidades y fuentes de las variables.
4. [verificacion.md](verificacion.md): pruebas, reproducción y fallos históricos.
5. [alineacion_investigacion/](alineacion_investigacion/README.md): alineación con el plan de tesis (población no financiera, tamaño, antecedentes, matrices revisadas y viabilidad de valoración probabilística); revisión local exploratoria.
6. [experimento_final/](experimento_final/README.md): última etapa experimental (formulaciones directa, de corrección de persistencia y relativa; pérdida absoluta; E0–E3 en la población no financiera); revisión local exploratoria.

## Archivos

| Contenido | Archivos |
|---|---|
| Protocolo, versionado antes de ejecutar | [protocolo.json](protocolo.json) |
| Entorno | [entorno.json](entorno.json) |
| Pliegues internos y búsquedas | [pliegues_internos.csv](pliegues_internos.csv), [busquedas_internas.csv](busquedas_internas.csv) |
| Selección E4 | [seleccion_e4.csv](seleccion_e4.csv) (atributos por pliegue), [seleccion_e4_historial.csv](seleccion_e4_historial.csv) |
| Predicciones con identificadores de fila | [predicciones.csv](predicciones.csv) |
| Métricas | [metricas_por_anio.csv](metricas_por_anio.csv), [resumen_procedimientos.csv](resumen_procedimientos.csv) |
| Comparaciones pareadas | [comparaciones_por_anio.csv](comparaciones_por_anio.csv), [resumen_comparaciones.csv](resumen_comparaciones.csv) |
| Importancia | [importancia_individual_por_anio.csv](importancia_individual_por_anio.csv), [importancia_individual.csv](importancia_individual.csv), [importancia_bloques_por_anio.csv](importancia_bloques_por_anio.csv), [importancia_bloques.csv](importancia_bloques.csv) |
| Concentración del error | [concentracion_error.csv](concentracion_error.csv) |
| Gráficos | [graficos/](graficos/) |
| Verificación | [verificacion_reproduccion.json](verificacion_reproduccion.json), [registro_pruebas.txt](registro_pruebas.txt) |
| Antecedente (versión inicial, `6eeac16`) | [antecedente_6eeac16/](antecedente_6eeac16/LEEME_ANTECEDENTE.md) |

## Reproducción

Desde la raíz del repositorio, en el entorno existente `tesis-fcl` (sin instalar paquetes ni usar red):

```bash
python scripts/reproduce_sprint_09.py --protocolo   # solo escribe protocolo.json (paso previo)
python scripts/reproduce_sprint_09.py               # ejecución completa (~7 min en esta máquina); regenera reports/sprint_09/ salvo antecedente_6eeac16/
python -m unittest tests.test_sprint_09 -v          # pruebas (leen los resultados y repiten controles reducidos)
```

**Dependencias de la ejecución:**
- Lee en modo solo lectura el panel y las fuentes anuales de `data/processed/`, `reports/sprint_08/especificacion_e2.json` y el notebook 07.
- Para verificar la reproducción, lee las predicciones de `reports/sprint_08/comparacion_modelos/` y `antecedente_6eeac16/`.
- El script fija `OMP_NUM_THREADS=1`; los resultados se verificaron con esa configuración.

**Alcance de la reproducción:** la equivalencia exacta se comprobó frente al Sprint 08 y frente a la versión inicial, en este entorno; no está comprobada en otras máquinas ni con otras versiones.

## Estado de GitHub

Ver la sección de GitHub en [verificacion.md](verificacion.md#estado-de-github).
