# Reproducir la ablación de variables (Sprint 08 — Etapa 2)

Desde la raíz del repositorio, con el entorno existente `tesis-fcl` (sin instalar dependencias):

```bash
conda activate tesis-fcl
python scripts/reproduce_ablacion_variables.py      # regenera reports/sprint_08/ablacion/
python -m unittest tests.test_ablacion_variables -v  # pruebas de aislamiento, pliegues y métricas
```

El notebook `notebooks/sprint_08/12_ablacion_variables.ipynb` explica el método y muestra los resultados;
toda la lógica está en `src/ablacion_variables.py`. La ejecución es determinista (Ridge con solver SVD):
dos corridas producen archivos idénticos. No usa red ni datos de prueba 2022–2025.
