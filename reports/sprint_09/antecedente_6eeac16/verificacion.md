# Verificación del Sprint 09

Se ejecutó `scripts/reproduce_sprint_09.py` en el entorno `tesis-fcl` hasta completar ambos modelos, tres variantes, dos monedas y cinco años externos. Se generaron métricas, predicciones, búsquedas internas y 520 retiradas individuales de atributos (26 × 2 modelos × 2 monedas × 5 años).

Las cuatro verificaciones de `tests/test_sprint_09.py` se ejecutaron directamente mediante `runpy`, todas aprobadas:

- Mismas filas y objetivos entre variantes y referencias; años internos anteriores al externo; evaluación limitada a 2017–2021.
- Reconstrucción de RMSE y MAE desde las predicciones, y coherencia de la regla de decisión.
- Reproducción de los cuatro resultados E2 de Ridge/boosting del Sprint 08 con tolerancia relativa 1e-10.
- Cobertura de los 26 atributos por modelo/moneda/año y signo correcto del delta de importancia.

`pytest` no está instalado en el entorno; no se ejecutó la suite completa del repositorio. Los resultados no resuelven los fallos de integridad previamente documentados del Sprint 08.

## Estado de GitHub

Rama local creada: `sprint-09-variantes-importancia`.
La creación remota mediante el conector GitHub devolvió HTTP 403 (`Resource not accessible by integration`). La autenticación existente de `gh` también figura inválida. La publicación remota está pendiente de acceso de escritura válido. No se publicó ni fusionó la entrega.
