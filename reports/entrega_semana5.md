# Entrega completa — Semana 5

Rama: `feature-engineering`. Estado: preparada localmente; publicación remota
pendiente de autenticación. El push previo falló sin credenciales HTTPS y la
conexión de GitHub respondió 403 (`Resource not accessible by integration`).
No se modificaron credenciales, permisos de la integración ni historial.

## Archivos incluidos en la entrega

- `data/processed/panel_fcl_preliminar.csv`: 4.221 filas originales, sin cambios.
- `data/processed/features_financieras.csv`: 4.221 filas, 57 columnas, 22 predictores;
  fuentes, controles y NaN preservados.
- `data/raw/smv/*.xml`: 22 respuestas originales, con copia duplicada de 2025.
- `data/README.md`, `data/raw/smv/README.md`: fuente, licencia y atribución.
- `notebooks/02_feature_engineering.ipynb`: ejecución completa; tablas y gráficos.
- `notebooks/EDA_FCL_2005_2025.ipynb`: EDA anterior, preservado.
- `src/feature_engineering.py` y `src/ingestion/ingest_smv.py`.
- `scripts/reproduce_features.py`, `scripts/trace_smv.py`,
  `scripts/execute_feature_engineering.py` y `scripts/correct_antigravity_notebook.py`
  (este último es un utilitario previo de edición; no es parte de la ingesta).
- `tests/test_feature_engineering.py`, `tests/test_trace_smv.py`, `tests/test_delivery.py`.
- `requirements-feature-engineering.txt`, `environment-feature-engineering.yml`.
- `reports/diccionario_features.md`, `reports/trazabilidad_variables.md`,
  `reports/procedimiento_smv.md`, `reports/resumen_feature_engineering.md`,
  `reports/correcciones_antigravity.md` (documentación de correcciones, no informe interno).
- `reports/trazabilidad_smv.json`, `reports/validacion_calculos.json`,
  `reports/validacion_ejecucion.json`, `reports/resultados_pruebas.txt`, `reports/validacion_clon.json` y este documento.
- `README.md` y `.gitignore`.

## Validación

15 pruebas aprobadas, con referencia manual para las 22 características y control
sobre las 4.221 filas entregadas. Notebook: 11 celdas de código sin errores.
La regeneración sin kernel coincide byte a byte con el CSV, incluso después de
reexportar desde el notebook; preserva fuentes y máscara de NaN.
Hash SHA-256 del CSV de características:
`0a9cafca02a4272210863c01fdd79f7e1a50573099e5779d09955e19adea5702`.
La comprobación se repitió en un clon local de la rama, sin Excel ni informe
interno, con el mismo resultado (ver `validacion_clon.json`). El notebook cambia
sus tiempos de ejecución y rutas de evidencia al reejecutarse; el CSV permanece
idéntico.
No se acredita una instalación nueva de dependencias ni reconstrucción histórica
del panel desde el servicio SMV; ver las brechas en `procedimiento_smv.md`.

## Exclusiones

- `data/raw/base_de_datos.xlsx`: fuente y derechos no verificados; no interviene
  en Feature Engineering ni es necesario para ejecutar el notebook.
- `reports/auditoria_feature_engineering.md`: informe interno de Antigravity.
- Logs de descarga, cachés y runtime: material de ejecución local.
- No se incluyen credenciales. No hay respuestas históricas de detalle de flujos
  disponibles para publicar: su ausencia es una brecha de procedencia.

## Completar la publicación

En una terminal propia con GitHub CLI instalado y una cuenta con escritura en
`RicardoVillena/tesis-flujo-caja-ia`:

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
git switch feature-engineering
git push -u origin feature-engineering
```

Estos pasos de autenticación deben ejecutarse por el usuario; no se ejecutaron
ni se cambió configuración de credenciales durante la preparación.
[Documentación oficial de GitHub CLI](https://cli.github.com/manual/gh_auth_login).
Si persiste 403, verificar escritura en ese repositorio o autorizar la integración
con acceso al repositorio y permiso Contents de lectura/escritura. Un token de
acceso detallado debe limitarse a ese repositorio y tener Contents: read/write;
no compartirlo en el chat ni escribirlo en archivos del proyecto.
[Documentación de tokens de GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).
Si el remoto rechaza el avance, inspeccionar la divergencia antes de continuar;
no hacer push forzado ni merge automático.

## Enlaces de destino (disponibles después del push)

- [Rama de entrega](https://github.com/RicardoVillena/tesis-flujo-caja-ia/tree/feature-engineering).
- [Notebook](https://github.com/RicardoVillena/tesis-flujo-caja-ia/blob/feature-engineering/notebooks/02_feature_engineering.ipynb).
- [Cálculos completos](https://github.com/RicardoVillena/tesis-flujo-caja-ia/blob/feature-engineering/data/processed/features_financieras.csv).

Para identificar el commit de entrega: `git rev-parse feature-engineering`.

Último intento de push: falló por ausencia de credenciales HTTPS (`could not read Username`). No se reintentó alterar permisos de la integración que antes devolvió 403.
