# Reproducir la comparación de modelos (Sprint 08)

```bash
conda activate tesis-fcl          # entorno existente; no requiere instalar paquetes
python scripts/reproduce_comparacion_modelos.py
python -m unittest tests.test_comparacion_modelos -v
```

Escribe `reports/sprint_08/comparacion_modelos/`. Deterministas: todo salvo `tiempos_ajuste.csv`.
Usa solo entrenamiento (años objetivo <= 2021); no lee datos de prueba ni red.
