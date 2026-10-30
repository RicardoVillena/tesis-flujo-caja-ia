# Sprint 09 — Variantes e importancia de variables

Rama: `sprint-09-variantes-importancia`.

Entrega para responder a la observación sobre el deterioro al incorporar variables externas:

1. [Protocolo](protocolo.json): E0 (19 financieras), E1 (23: agrega macro), E2 (26: agrega bursátiles), Ridge y boosting; mismas filas, años y presupuesto de ajuste por algoritmo.
2. [Resultados](resultados.md) y [comparación incremental](comparacion_incremental.csv): evidencia favorable o desfavorable, por moneda; sin atribuir a las variables mejoras debidas solo al cambio de algoritmo.
3. [Importancia individual](importancia_variables.csv) y [detalle anual](importancia_por_anio.csv): ablación con reajuste y configuración E2 congelada en cada pliegue; positivo significa aporte predictivo del atributo en ese contexto.
4. [Matriz de consistencia propuesta](matriz_consistencia.md): problemas, objetivos, hipótesis, variables e indicadores; sujeta a revisión académica.

Reproducción desde la raíz:

```bash
conda run -n tesis-fcl python scripts/reproduce_sprint_09.py
```

Se reutiliza el protocolo anidado del Sprint 08 (tres años internos, ocho años mínimos de historia; años externos 2017–2021). La selección usa solo el pasado del año evaluado. Se conservan media histórica y persistencia en las mismas filas. El pipeline aprende imputación y escalado dentro de cada entrenamiento. Las rejillas se escriben en `protocolo.json` antes del cálculo.

No hay garantía previa de mejora. Las comparaciones son exploratorias y no constituyen confirmación independiente. Los resultados previos de otro protocolo, moneda o cohorte no se comparan como si fueran equivalentes. El ranking individual es condicional a los hiperparámetros E2 y puede verse afectado por redundancia; no interpreta causalidad.
