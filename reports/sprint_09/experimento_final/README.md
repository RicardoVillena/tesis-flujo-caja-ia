# Experimento final (Sprint 09) — formulaciones del objetivo, pérdida robusta y variables externas

Última etapa experimental, exploratoria y **sin commit**: los cambios quedan en local para revisión. Después de esta etapa se detiene la experimentación.

## Qué es

- **Alcance:** predicción del FCL preliminar t+1; no es FCFF validado ni una valoración DCF.
- **Población:** no financiera según la regla SMV.
- **Formulaciones:** directa, corrección de persistencia y relativa al activo. Esta última no está validada económicamente.
- **Modelos:** Ridge y boosting con pérdida cuadrática y absoluta.
- **Atributos:** variantes E0 a E3.

**Leer primero:**
1. [resumen_tecnico.md](resumen_tecnico.md): respuestas a las 5 preguntas, separando reducción observada, consistencia temporal y confirmación independiente.
2. [auditoria_unidades.md](auditoria_unidades.md): unidades, casos extremos y decisiones (sin correcciones).
3. [protocolo.json](protocolo.json): protocolo fijado antes de ejecutar (SHA-256 `c2430bd4…`, 30 de octubre de 2026, 17:04:28).

Las demás salidas se describen en la sección "Archivos" del resumen técnico. Gráficos en [graficos/](graficos/).

## Reproducción

Desde la raíz del repositorio, en el entorno `tesis-fcl` (sin red ni datos de prueba 2022–2025):

```bash
python scripts/reproduce_experimento_final.py --protocolo   # solo escribe protocolo.json
python scripts/reproduce_experimento_final.py               # regenera esta carpeta (salvo los .md); exige el protocolo versionado
python -m unittest tests.test_experimento_final -v
```

- **Paralelismo:** la ejecución reparte el trabajo por moneda y año con joblib, con un hilo por proceso; los resultados son deterministas.
- **Dependencias de solo lectura:** `data/processed/`, el catálogo del Sprint 07, `reports/sprint_08/saltos_escala_train.csv` y `reports/sprint_09/alineacion_investigacion/predicciones.csv` (para la auditoría de casos y la verificación de reproducción).
- **Código:** `src/experimento_final.py`.

## Correcciones de la auditoría aplicadas en esta etapa

- **Población conservadora:** queda identificada como sensibilidad retrospectiva, porque usa CIIU de 2023–2025, y no se usa aquí. La nota está en [../alineacion_investigacion/informe_alineacion.md](../alineacion_investigacion/informe_alineacion.md).
- **Antecedentes:** se corrigió en [../alineacion_investigacion/antecedentes.md](../alineacion_investigacion/antecedentes.md) la afirmación de que ningún antecedente predice FCL. Lu y Zhao pronostican flujos de caja, aunque su definición exacta no quedó verificada.
