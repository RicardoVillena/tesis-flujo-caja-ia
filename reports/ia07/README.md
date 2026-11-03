# Sesión IA07: Random Search y Optuna TPE para Ridge

Trabajo con commit local en la rama, sin publicar, pendiente de auditoría independiente y de revisión final.

**Leer primero:** [informe_resultados.md](informe_resultados.md) y, para auditar, [informe_auditoria_kimi.md](informe_auditoria_kimi.md). Notebook: [15_optimizacion_hiperparametros.ipynb](../../notebooks/ia07/15_optimizacion_hiperparametros.ipynb).

| Contenido | Archivos |
|---|---|
| Protocolo y entorno | `protocolo.json`, `entorno.json` |
| Ventanas | `pliegues.csv` |
| Registro de trials | `trials.csv`, `referencia_densa.csv` |
| Convergencia | `curvas_convergencia.csv`, `comparacion_metodos.csv`, `comparacion_metodos_agregada.csv` |
| Hiperparámetros y pruning | `efecto_categoricos.csv`, `diagnostico_pruning.csv` |
| Configuraciones ganadoras | `seleccion_congelada.csv`, `seleccion_congelada.json` |
| Prueba | `evaluacion_prueba.json`, `metricas_prueba.csv`, `metricas_prueba_por_anio.csv`, `predicciones_prueba.csv` |
| Verificación | `verificacion_determinismo.json`, `integridad_previa.json`, `registro_pruebas.txt` |
| Gráficos | `graficos/` |

## Reproducción

El entorno hereda `tesis-fcl` sin alterarlo y solo añade Optuna:

```bash
~/miniconda3/envs/tesis-fcl/bin/python -m venv --system-site-packages ~/.venvs/tesis-fcl-ia07
~/.venvs/tesis-fcl-ia07/bin/python -m pip install -r requirements-ia07.txt
~/.venvs/tesis-fcl-ia07/bin/python -m ipykernel install --prefix=$HOME/.venvs/tesis-fcl-ia07 --name tesis-fcl-ia07
```

Etapas, en este orden y desde la raíz del repositorio:

```bash
python scripts/reproduce_optimizacion_hiperparametros.py --protocolo
python scripts/reproduce_optimizacion_hiperparametros.py --buscar     # unos 2 minutos con 12 núcleos
python scripts/reproduce_optimizacion_hiperparametros.py --analizar
python scripts/reproduce_optimizacion_hiperparametros.py --evaluar
python -m unittest tests.test_optimizacion_hiperparametros
```

`--buscar` y `--evaluar` se niegan a ejecutarse si `metricas_prueba.csv` ya existe en la carpeta, de modo que la búsqueda no se repite después de ver la prueba. Para repetir la búsqueda, usar `ejecutar_busqueda(out=...)` con otra carpeta. Abrir el notebook requiere seleccionar el kernel `tesis-fcl-ia07`.
