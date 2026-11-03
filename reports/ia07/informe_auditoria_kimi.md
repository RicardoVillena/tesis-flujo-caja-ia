# Informe técnico para auditoría independiente: sesión IA07

**Dictamen:** este informe no declara el trabajo aprobado. La aprobación corresponde a esta auditoría y a la revisión final del autor de la tesis.

**Estado del repositorio:** rama `sprint-09-variantes-importancia`. El trabajo se ejecutó sobre `8239c27` y está en un commit local posterior, sin push.

**Encargo:** optimizar los hiperparámetros de Ridge con Random Search y Optuna TPE, con presupuestos equivalentes. Se debían conservar la partición temporal, los datos originales y el baseline Ridge, sin usar la prueba para seleccionar hiperparámetros ni características. El pruning y el early stopping solo se documentan.

**Resultados:** ver [informe_resultados.md](informe_resultados.md). Este documento se centra en qué verificar.

## 1. Archivos

### Creados

| Ruta | Función | SHA-256 |
|---|---|---|
| `src/optimizacion_hiperparametros.py` | Módulo reutilizable | `06028681…` |
| `scripts/reproduce_optimizacion_hiperparametros.py` | Etapas de ejecución | `6a6306f7…` |
| `tests/test_optimizacion_hiperparametros.py` | 26 pruebas | `03402330…` |
| `notebooks/ia07/15_optimizacion_hiperparametros.ipynb` | Notebook ejecutado, kernel `tesis-fcl-ia07` | `00a77aa8…` |
| `requirements-ia07.txt` | Optuna y sus dependencias, con versión fijada | `04f928a2…` |
| `reports/ia07/` | Salidas e informes; índice en [README.md](README.md) | `protocolo.json`: `27433742…`; `seleccion_congelada.csv`: `9ee2e553…` |

### Modificados

| Ruta | Cambio |
|---|---|
| `notebooks/README.md` | 4 líneas añadidas al final (índice de IA07) |

### Fuera del repositorio

`~/.venvs/tesis-fcl-ia07`: entorno virtual que hereda `tesis-fcl` y solo añade optuna 4.9.0, alembic 1.20.1, colorlog 6.12.0, Mako 1.4.3, SQLAlchemy 2.1.7 y tqdm 4.70.1. Incluye el kernel `tesis-fcl-ia07`. El entorno `tesis-fcl` no se modificó.

### Presentes en el árbol, ajenos a esta sesión

`reports/memoria_investigacion.md` y `notebooks/Trabajo_de_investigacion_final.pdf:Zone.Identifier` ya estaban sin seguimiento al empezar, y no se tocaron.

## 2. Cronología (UTC, 3 de noviembre de 2026)

| Hora | Hecho | Evidencia |
|---|---|---|
| Antes de 22:41 | 16 pruebas previas aprobadas, incluida la reproducción del 07 y el 08 | Ejecución local; no quedó archivo de ese momento |
| 22:41:43 | Protocolo escrito | `protocolo.json` (fecha del archivo) |
| 22:43:31 | Búsqueda terminada y selección congelada | `seleccion_congelada.json` |
| 22:44:01 | Evaluación única en prueba | `evaluacion_prueba.json` |

**Cambios de código después de la evaluación en prueba:**
1. Se añadió el ajuste de Holm a `analizar_convergencia`, después de ver los valores sin ajustar. Solo usa datos de validación.
2. Se añadió la etapa `--graficos` y dos ajustes visuales (leyenda y rejilla).

Qué se comprobó con SHA-256:
- Al añadir Holm se volvió a ejecutar `--analizar`. `seleccion_congelada.csv` y `curvas_convergencia.csv` no cambiaron. `comparacion_metodos*.csv` cambiaron por las columnas nuevas. `diagnostico_pruning.csv` y `efecto_categoricos.csv` se reescribieron sin comprobar su hash en ese paso, aunque su código no cambió. Los CSV de prueba no se reescribieron.
- Al regenerar los gráficos, todos los CSV de la carpeta conservaron su hash.

La evaluación en prueba se ejecutó una sola vez y no se corrigió ningún error después de verla.

## 3. Pruebas ejecutadas

Registro: [registro_pruebas.txt](registro_pruebas.txt).

| Comando | Entorno | Resultado |
|---|---|---|
| `python -m unittest -v tests.test_optimizacion_hiperparametros` | `tesis-fcl-ia07` | 26 ejecutadas, 26 aprobadas, 0 omitidas |
| `PYTHONPATH=. python -m unittest discover -s tests` | `tesis-fcl-ia07` | 150 ejecutadas: **147 aprobadas y 3 fallidas** |
| `PYTHONPATH=. python -m unittest discover -s tests -p 'test_optimizacion*'` | `tesis-fcl` (sin Optuna) | Módulo omitido |
| Búsqueda completa repetida en una carpeta temporal | `tesis-fcl-ia07` | Mismos 38.400 trials, misma referencia densa, misma selección (`verificacion_determinismo.json`) |

**Los 3 fallos:**
- `test_auditoria_calidad…test_prior_files_intact_against_head_and_pre_edit_reference`
- `test_clasificacion_sectorial…test_reproducibilidad_fuentes_y_salida_exacta`
- `test_enriquecimiento_sectorial…test_reproduccion_exacta_catalogos_y_json_sin_red`

Son los mismos tres, con los mismos mensajes y hashes, que figuran en `reports/sprint_09/experimento_final/registro_pruebas.txt`, anterior a esta sesión. Dos salvedades:
- La lista de modificados del primero ya incluía `notebooks/README.md`, que esta sesión volvió a editar.
- Ese primer test se detiene en su primera aserción, así que no llega a evaluar sus comprobaciones posteriores. Una de ellas (`nuevos_fuera_de_sprint08`) podría verse afectada por los archivos nuevos de esta sesión.

Bajo `tesis-fcl`, cargar el módulo por nombre (`python -m unittest tests.test_optimizacion_hiperparametros`) termina con un error de importación que informa de que falta Optuna. Por descubrimiento se omite correctamente.

## 4. Qué cubren las pruebas

| Requisito | Prueba o control |
|---|---|
| Partición conservada | `test_particion_original_conservada`, `test_pliegues_iguales_al_notebook_08_y_sin_prueba` |
| Baseline Ridge conservado | `test_baseline_ridge_07_reproducido`: predicciones completas E0, E1 y E2 en ambas monedas; `test_baseline_y_rejilla_coinciden_con_metricas_previas` |
| Coherencia con el 08 | `test_puntuaciones_cv_08_reproducidas` (216 valores; los otros 54 de los 270 son la cohorte de dólares repetida), `test_predicciones_08_reproducidas`, `test_seleccion_08_coincide_con_su_archivo` |
| Sin fuga de prueba | `test_evaluador_rechaza_filas_de_prueba`, `test_perturbar_prueba_no_cambia_la_busqueda` con control positivo, `test_recorte_aprendido_solo_en_entrenamiento` |
| Congelación | `test_congelacion_intacta_y_previa_a_prueba`, `test_evaluar_rechaza_seleccion_alterada` |
| Presupuestos equivalentes | `test_presupuestos_equivalentes`, `test_determinismo_y_presupuesto_equivalente` |
| Registro correcto | `test_trials_reproducibles_desde_el_registro`, `test_ganadores_son_el_minimo_de_cv`, `test_metricas_reconstruidas_y_mismas_filas` |
| Datos sin tocar | `test_archivos_previos_sin_cambios` (`git status` de `data`, `reports/sprint_06` y los notebooks 07 y 08, más hash del panel) |

**Límites de cobertura:**
- La perturbación de la prueba solo se ejecuta en Dólares/todas con E0, con 15 trials y ambos métodos. Para el resto, la garantía es estructural: `EvaluadorCV` rechaza filas de prueba.
- `test_trials_reproducibles_desde_el_registro` repite un solo estudio. La repetición completa se hizo una vez, fuera de la suite.
- `test_archivos_previos_sin_cambios` depende de `git status`, y `data/raw/base_de_datos.xlsx` está ignorado por git, así que no queda cubierto.

## 5. Decisiones que conviene cuestionar

1. **Uso de la prueba.** Se evaluaron las configuraciones congeladas una vez, porque la instrucción prohíbe usar la prueba para seleccionar, no para evaluar. Los Sprints 08 y 09 no la habían usado en sus protocolos. Solo afecta a Ridge; no se evaluó `persistencia|boosting_abs`.
2. **Espacio de búsqueda.** Lo fijé yo: los límites de alpha y el nivel `p05_p95`, que no estaba en los notebooks 07 y 08. El PDF del plan menciona winsorización 5/95. El nivel `sin_recorte` y el escalador robusto proceden del 07.
3. **Características.** Se fijaron 16 estudios: E0, E1 y E2 del 07 y la selección del 08 por cohorte. No se usaron las 9 especificaciones del 08. El ganador por cohorte sí compara características por validación, y la especificación del 08 parte con ventaja porque se eligió en las mismas ventanas.
4. **Random Search con Optuna.** Se usó `RandomSampler` en lugar de `RandomizedSearchCV`, para compartir objetivo y registro. Los 10 primeros trials coinciden con los de TPE por compartir semilla, así que las muestras no son independientes en ese tramo.
5. **Presupuesto.** 60 trials y 20 semillas son una decisión de diseño, sin análisis de potencia. La ventaja de TPE podría cambiar con otro presupuesto, como muestran las curvas.
6. **Semilla principal.** La semilla `20261103` decide la configuración que va a prueba. Otra semilla daría configuraciones casi equivalentes en validación, pero posiblemente con otro RMSE de prueba.
7. **Referencias de persistencia.** Para los modelos de esta sesión se usa la definición del 08 (mediana de FCL(t) como respaldo), no la de los Sprints 08 y 09 (media del objetivo). Las cifras no son directamente comparables con las de esos sprints.
8. **Formato del notebook.** Se siguió el de los notebooks 07 y 08, con títulos numerados en negrita. El notebook 14 usó otro formato por una instrucción específica de esa entrega.

## 6. Comprobaciones sugeridas

```bash
P=~/.venvs/tesis-fcl-ia07/bin/python
$P -m unittest -v tests.test_optimizacion_hiperparametros
sha256sum reports/ia07/seleccion_congelada.csv   # debe empezar por 9ee2e553
git status --short -- data reports/sprint_06 notebooks/07_baseline_variantes.ipynb notebooks/08_mejoras_baseline.ipynb   # debe estar vacío
```

Puntos de revisión manual:
- `ejecutar_busqueda` y `_corrida`: confirmar que ninguna ruta entrega filas de prueba a la búsqueda.
- `evaluar_prueba`: confirmar que nada vuelve a la selección.
- `pliegues`: confirmar que coincide con la celda 16 del notebook 08.
- Las afirmaciones del notebook y del informe, frente a los CSV de `reports/ia07/`. Las celdas Markdown se redactaron a mano después de consultar las tablas; no se generan desde los datos.
