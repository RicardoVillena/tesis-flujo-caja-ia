# Revisión del dictamen de Kimi sobre la sesión IA07

**Estado:** Kimi dictaminó APROBADO CON OBSERVACIONES. La revisión final del autor sigue pendiente. Las correcciones de la sección 3 no están aplicadas.

**Base revisada:** commit `e68d3e2`. Esta revisión no cambió código, datos ni resultados.

## 1. Dictamen recibido

Texto de la última versión entregada, copiado tal como se recibió. Los cortes de palabras ya venían en el texto pegado y puede faltar contenido. La lista de hallazgos no se recibió.

> rificado hallazgos
>
> Fuga temporal / uso de prueba: el evaluador rechaza filas de prueba por aserto; la búsqueda es invariante a perturbar la prueba (×100 + 1e) y sensible a perturbar validación (control positivo); clipping e imputación se ajustan solo con entrenamiento de cada ventana; ventanas idénticas al notebook 08 (contraste con cv_folds.csv).
>
> Equivalencia RS/TPE: mismo objetivo, folds, espacio y presupuesto; 640 corridas × 60 trials = 38.400 trials, todos COMPLETE; curvas idénticas hasta el trial 10 (startup de T verificado en datos).
>
> Métricas: MAE/RMSE/R² con sklearn correctos y reproducibles desde predicciones; R²_OOS vs. media y persistencia incluido.
>
> Integridad de datos yos previos: panel sin tocar (SHA-256 registrado), partición 2.869/691 conservada, git status limpio en data/, reports/sprint_06/, notebooks 07/08; baselines 07 y CV/selección 08 reproducidos por tests.
>
> Reproducibilidad: 20 semillas fijas, protocolo versionado contra el código, verificacion_determinismo.json confirma segunda corrida idica (trials, referencia densa y selección), entorno fijado (requirements-ia07.txt, optuna 4.9.0).
>
> Gráficos: convergencia.png, respuesta_alpha.png y prueba_por_cohorte.pngcoherentes con las tablas (barras vs. líneas de persistencia/media cuadran conmetricas_prueba.csv`).
>
> Notebook: 13 secciones académicas ejecutadas con salidas (entorno, diagnóstico, datos, protocolo, convergencia, hiperparámetros, pruning, prueba, comprobaciones,es).
>
> Pruebas IA07: 26/26 en verde en el venv tesis-fcl-ia07.
>
> Dictamen
>
> APROBADO CON OBSERVACIONES. Cero hallazgos CRTICOS. El único MAYOR es inferencial (Holm post-hoc) y no compromete predicciones ni la conclusión central (optimizar α importa; el método de búsqueda importa poco). Todos los resultados numéricos del informe fueron verificados contra artefactos; nada se aprobó sin evidencia.
>
> Archivos revisados: src/optimizacion_hiperparametros.py, tests/test_optimizacion_hparametros.py, scripts/reproduce_optimizacion_hiperparametros.py, reports/ia07/informe_resultados.md, notebooks/ia07/15_optimizacion_hiperparametros.ipynb, más artefactos de reports/ia07/ (CSV/JSON/PNG) y las referencias de reports/sprint_06/ para contraste.
>
> Pendiente único: confirmación externa del rubric sobre el tratamiento documental del pruning (item 2), que no puede verificarse por evidencia dentro del repositorio.

La versión anterior del dictamen listaba además dos pendientes que esta retira sin explicación: la causa de los 3 fallos legacy y la ejecución del notebook en una sesión limpia.

## 2. Comprobaciones independientes

Ejecutadas con el entorno `tesis-fcl-ia07`, sin modificar archivos. Son comprobaciones puntuales: no quedaron como pruebas automatizadas.

| Punto | Resultado |
|---|---|
| Primeros 10 trials iguales en ambos métodos | Confirmado |
| MAE, RMSE y R² desde las predicciones | Confirmado en 72 filas; diferencia máxima 1,2e-14 |
| R²_OOS frente a media y persistencia | Confirmado en 72 filas; diferencia máxima 4,3e-14 |
| Años de validación iguales a `cv_por_anio.csv` del notebook 08 | Confirmado en las 4 cohortes |
| Recorte aprendido solo en la ventana | Confirmado en la ventana 1 de Soles/todas con E0 |
| Imputación aprendida solo en la ventana | Confirmado en las 4 ventanas de Soles/todas con E0 |
| Notebook en sesión limpia | 12 celdas de código, sin errores; salidas de texto iguales a las guardadas. No se compararon imágenes |
| Duraciones de los trials | Medianas 13,09 y 16,79 ms; medias 23,28 y 26,51 ms. 13 y 17 ms son medianas, no medias |

**Causa de los fallos legacy:** dos fallan porque el hash de `notebooks/03_extraccion_macroeconomica.ipynb` (`8ba6f7…`) ya no coincide con la referencia registrada (`2a892a…`). Ese notebook entró en el commit `ecf7f16`, anterior a IA07. El tercero lista ese notebook, `notebooks/README.md` y `reports/auditoria_extraccion_macroeconomica.md`, y ya fallaba igual antes de esta sesión. Las referencias siguen sin actualizarse y los fallos continúan.

## 3. Puntos abiertos

**Inferencia entre métodos.** `comparacion_metodos.csv` usa Mann-Whitney, que supone muestras independientes, pero ambos métodos comparten semilla y sus 10 primeros trials. Con Wilcoxon pareado por semilla, a 60 trials y en 16 estudios:

| Prueba | p < 0,05 | Tras Holm |
|---|---:|---:|
| Mann-Whitney (la del informe) | 8 | 4 |
| Wilcoxon pareado | 4 | 1 (Soles/bancario E0) |

En las 320 comparaciones pareadas, TPE gana en 224, Random Search en 93 y hay 3 empates. Las configuraciones ganadoras y las métricas de prueba no cambian, pero la frase sobre los 4 estudios que se sostienen tras Holm exagera la evidencia. Kimi no evaluó este punto.

**Correcciones propuestas, sin aplicar:**
1. Añadir Wilcoxon pareado como sensibilidad posterior a la auditoría y corregir esa frase en `informe_resultados.md` y en el notebook.
2. Aclarar que 13 y 17 ms son medianas.
3. Ampliar las pruebas para reconstruir MAE y R² y comparar los años de las ventanas.
4. Añadir la causa de los fallos legacy a `informe_auditoria_kimi.md`.

**Pendiente de Kimi:**
- Detallar sus hallazgos, incluido el MAYOR, con archivo, evidencia y corrección.
- Pronunciarse sobre las 8 decisiones de la sección 5 de `informe_auditoria_kimi.md`, archivo que no figura entre los revisados.
- Evaluar el punto de inferencia entre métodos.

**Pendiente del autor:**
- Aportar la rúbrica que Kimi cita como "item 2", que no está en el repositorio.
- Decidir si se aplican las correcciones y si se actualizan las referencias de los fallos legacy.
