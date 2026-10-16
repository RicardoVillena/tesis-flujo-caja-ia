"""Migración del notebook de Semana 5 para resolver HAL-01–HAL-12 (idempotente)."""
from pathlib import Path
import nbformat
ROOT = Path(__file__).resolve().parents[1]
p = ROOT / 'notebooks/02_feature_engineering.ipynb'
nb = nbformat.read(p, as_version=4)
if any('Diagnósticos Antigravity' in c.source for c in nb.cells):
    raise SystemExit('Migración ya aplicada; ejecutar scripts/execute_feature_engineering.py')
for c in nb.cells:
    if c.cell_type == 'code':
        c.source = c.source.replace('sys.version_info[:3] == (3, 12, 15)', 'sys.version_info[:2] == (3, 12)')
        c.source = c.source.replace('from sklearn.preprocessing import StandardScaler',
            'from sklearn.pipeline import Pipeline\nfrom sklearn.base import clone\nfrom scipy.stats import mannwhitneyu\nfrom matplotlib.ticker import MaxNLocator')
        c.source = c.source.replace('from src.feature_engineering import build_features',
            'from src.feature_engineering import build_features, make_preprocessor, REDUNDANT_PREDICTORS')
        c.source = c.source.replace('dtype={"RPJ": str, "RUC": str})', 'dtype={"RPJ": str, "RUC": str}, encoding="utf-8-sig")')
        if 'print("Rama:"' in c.source:
            c.source += '\nDISPLAY_LABELS = {"D lares": "Dólares", "M todo Directo": "Método Directo", "M todo Indirecto": "Método Indirecto"}\ndef presentation(frame):\n    """Solo presentación: las etiquetas fuente del CSV no cambian."""\n    return frame.rename(index=DISPLAY_LABELS).replace(DISPLAY_LABELS)\n'
        c.source = c.source.replace('display(raw.Moneda.value_counts().rename("registros").to_frame())',
            'display(presentation(raw.Moneda.value_counts().rename("registros").to_frame()))')
        c.source = c.source.replace('plt.ylabel("Observaciones"); plt.tight_layout(); plt.show()',
            'plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))\nplt.ylabel("Observaciones"); plt.tight_layout(); plt.show()')
        c.source = c.source.replace('display(features.groupby("Moneda")[temporal].count())',
            'display(presentation(features.groupby("Moneda")[temporal].count()))')
        if 'prepared, diagnostics = {}, []' in c.source:
            start = c.source.index('    imputer = SimpleImputer')
            stop = c.source.index('    q1, q3 =',start)
            c.source = c.source[:start] + '''    pipeline = make_preprocessor()
    xtr = pipeline.fit_transform(tr[cols])
    xte = pipeline.transform(te[cols]) if len(te) else np.empty((0, len(cols)))
    prepared[currency] = dict(columns=cols, pipeline=pipeline,
                             X_train=xtr, X_test=xte,
                             missing_train=tr[cols].isna(), missing_test=te[cols].isna())
    assert np.isfinite(xtr).all() and np.isfinite(xte).all()
    np.testing.assert_allclose(pipeline.named_steps["imputer"].statistics_, tr[cols].median().to_numpy())
    # RobustScaler: el centro y el IQR proceden exclusivamente de entrenamiento.
    np.testing.assert_allclose(pipeline.named_steps["scaler"].center_,
                               np.median(pipeline.named_steps["imputer"].transform(tr[cols]), axis=0))
    scaled_iqr = float(np.subtract(*np.percentile(xtr[:, cols.index("crecimiento_ActivoTotal")], [75, 25])))
''' + c.source[stop:]
            c.source = c.source.replace('"celdas_extremas_train": int(outliers.sum())',
                '"celdas_extremas_train": int(outliers.sum()), "IQR_crecimiento_activos_robusto": scaled_iqr')
            c.source = c.source.replace('display(pd.DataFrame(diagnostics))','display(presentation(pd.DataFrame(diagnostics)))')
        c.source = c.source.replace('f"Spearman de ratios — entrenamiento — {currency}"',
                                  'f"Spearman de ratios — entrenamiento — {DISPLAY_LABELS.get(currency, currency)}"')
        c.source = c.source.replace('    fig.colorbar(im, ax=ax);', '''    for i in range(len(ratio_names)):
        for j in range(len(ratio_names)):
            value = corr.iloc[i, j]
            ax.text(j, i, f"{value:.2f}" if pd.notna(value) else "NA", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax);''')
        c.source = c.source.replace('display(train.groupby(["TipoSector", "Moneda"]).size().rename("registros_train").to_frame())',
            'display(presentation(train.groupby(["TipoSector", "Moneda"]).size().rename("registros_train").reset_index()))')
        c.source = c.source.replace('"No hay fechas de publicación verificadas. Ratios solo con denominadores positivos. "',
            '"No hay fechas de publicación verificadas. Orden canónico: (RPJ, Ejercicio), sin índice posicional original. "\n    "Ratios solo con denominadores positivos; rotación y crecimiento de ingresos exigen ingreso actual positivo. "\n    "Las derivaciones de FCL invalidan CAPEX positivo; la columna fuente FCL_preliminar se conserva. "\n    "Subconjunto PREDICTORS_NO_COLINEALES: 19, excluye fcl_activo y ambas medias móviles. "')
        if 'report = "# Semana 5' in c.source:
            c.source = c.source.replace('Imputación mediana y escalado ilustrativos', 'Imputación mediana y RobustScaler en Pipeline ilustrativos')
            c.source = c.source.replace('report += markdown_table(pd.DataFrame(diagnostics))',
                'report += markdown_table(presentation(pd.DataFrame(diagnostics)))')
            c.source = c.source.replace('"Entorno tesis-fcl, Python 3.12.15.', '"Entorno tesis-fcl, Python 3.12.x (ejecución verificada en 3.12.15).')
            c.source = c.source.replace('report += f"SHA256 del CSV fuente:', '''report += "\\n\\n## Correcciones Antigravity y diagnósticos\\n\\n"
report += ("Se conservan 22 características y se define un subconjunto de 19 sin las tres redundancias lineales exactas. "
           "Las identidades se verifican solo en entrenamiento; las dependencias DuPont son multiplicativas. "
           "Los casos completos se usan únicamente en diagnósticos; queda prohibido descartar filas mediante dropna sobre predictores en modelado. "
           "La inferencia Mann-Whitney es exploratoria: observaciones de una empresa no son independientes. "
           "RobustScaler preserva la escala intercuartílica, pero no elimina ni acota extremos. "
           "Las versiones normalizadas por ActivoTotal(t) son una sensibilidad en memoria, no nuevos predictores exportados ni un cambio del objetivo principal. "
           "La reconstrucción monetaria requiere activos y moneda de origen. La bandera revision_interanual permite estratificar, "
           "pero no demuestra por sí sola fecha o causa de una reexpresión; tampoco su ausencia garantiza datos point-in-time. "
           "La Semana 6 deberá comparar resultados por esta bandera y por moneda, auditando también las fuentes históricas de los rezagos. "
           "La imputación y el escalado deben clonarse y ajustarse dentro de cada pliegue temporal por moneda.\\n\\n")
report += "### Rango: solo entrenamiento completo\\n\\n" + markdown_table(presentation(rank_diagnostics))
report += "\\n\\n### Casos completos versus incompletos\\n\\n" + markdown_table(presentation(selection_summary))
report += "\\n\\n### Mann-Whitney por moneda (completos frente a incompletos)\\n\\n" + markdown_table(presentation(selection_tests))
report += "\\n\\n### Revisión interanual: estratificación, sin entrenar\\n\\n" + markdown_table(presentation(revision_summary))
report += "\\n\\n### Disponibilidad por año origen\\n\\n" + markdown_table(selection_by_year)
report += "\\n\\nSubconjunto recomendado de 19: `" + "`, `".join(PREDICTORS_NO_COLINEALES) + "`.\\n"
report += f"SHA256 del CSV fuente:''')
    else:
        c.source = c.source.replace('imputación mediana y escalado', 'imputación mediana y escalado robusto')
        c.source = c.source.replace('imputación mediana y el escalado', 'imputación mediana y el escalado robusto')
        c.source = c.source.replace('Los extremos pueden ser eventos económicos reales;',
            'Se usa un Pipeline de SimpleImputer y RobustScaler, que no elimina ni acota extremos. Para validación temporal se debe clonar el Pipeline y ajustarlo desde cero en cada pliegue, por moneda; jamás reutilizar X_train ya transformado globalmente. Los extremos pueden ser eventos económicos reales;')
        if c.source.startswith('## 6.'):
            c.source += '\n\nHAL-02/03: CAPEX positivo invalida internamente FCL para ratios, rezagos, ventanas y etiquetas, conservando intacto el valor fuente exportado. Para rotación y crecimiento se exige ingreso actual > 0; esta es una convención de dominio y no convierte ingresos negativos reportados en faltantes del origen.'
        if c.source.startswith('## 12.'):
            c.source += '\n\n**No usar `dropna()` sobre predictores para modelado.** El subconjunto completo es selectivo por tamaño, antigüedad e ingresos. Su conteo no representa la muestra recomendada para entrenar.'
# Nuevas celdas: todos los diagnósticos se calculan antes del reporte.
insert_at = next(i for i,c in enumerate(nb.cells) if c.source.startswith('## 10.'))
new = [nbformat.v4.new_markdown_cell(r'''### Diagnósticos Antigravity — HAL-01, HAL-05, HAL-06 y HAL-07
Hay tres identidades lineales: `fcl_activo = fco_activo - inversion_capex_activo` y cada media móvil es la suma de sus tres rezagos dividida entre tres. Se eliminan esas tres variables del subconjunto `PREDICTORS_NO_COLINEALES` (19). Las identidades multiplicativas son `rentabilidad_activo_cierre = margen_neto × rotacion_activo_cierre` y `fco_activo = fco_ingresos × rotacion_activo_cierre`. No son dependencias lineales adicionales.

El rango y VIF se calculan en entrenamiento con filas completas únicamente como diagnóstico. Se centran y normalizan columnas para que las unidades no dominen la tolerancia numérica. VIF se calcula con álgebra lineal entre predictores, sin entrenar un modelo del objetivo. La reducción a 19 elimina redundancias exactas, no garantiza independencia estadística ni resuelve por sí sola atribuciones SHAP; habrá que evaluar dependencias restantes o agrupar explicaciones.

Se contrasta tamaño entre casos completos e incompletos por moneda con Mann-Whitney bilateral. Es un análisis descriptivo exploratorio: la dependencia longitudinal dentro de empresa impide interpretar el p-valor como una inferencia de muestras independientes rigurosa. No se seleccionan características con estos resultados. El análisis de prueba solo cuantifica disponibilidad y revisión; ninguna selección o transformación se ajusta con prueba.

Como sensibilidad de escala se calculan en memoria las diez variables temporales divididas por `ActivoTotal(t)` y `objetivo_fcl_t1 / ActivoTotal(t)`, usando activos positivos conocidos al origen. El objetivo principal y las 22 columnas exportadas no cambian. Para recuperar moneda: multiplicar una futura predicción normalizada por los activos de t; evaluar MAE/RMSE por moneda y tamaño. Esta normalización no corrige inflación, diferencias contables ni denominadores económicamente diminutos.'''), nbformat.v4.new_code_cell('''PREDICTORS_NO_COLINEALES = [c for c in PREDICTORS if c not in REDUNDANT_PREDICTORS]
assert len(PREDICTORS_NO_COLINEALES) == 19
rank_rows, vif_rows = [], []
for currency, tr in train.groupby("Moneda"):
    diagnostic = tr.loc[tr[PREDICTORS].notna().all(axis=1), PREDICTORS]
    assert len(diagnostic) > len(PREDICTORS)
    # Verificar identidades en la muestra de diagnóstico de entrenamiento.
    np.testing.assert_allclose(diagnostic.fcl_activo, diagnostic.fco_activo - diagnostic.inversion_capex_activo, atol=1e-10)
    for name in ["FCO", "FCL_preliminar"]:
        np.testing.assert_allclose(diagnostic[f"{name}_mean3_previa"], diagnostic[[f"{name}_lag{k}" for k in [1,2,3]]].mean(axis=1), atol=1e-10)
    np.testing.assert_allclose(diagnostic.rentabilidad_activo_cierre, diagnostic.margen_neto * diagnostic.rotacion_activo_cierre, atol=1e-10)
    np.testing.assert_allclose(diagnostic.fco_activo, diagnostic.fco_ingresos * diagnostic.rotacion_activo_cierre, atol=1e-10)
    for name, cols in [("original_22", PREDICTORS), ("reducido_19", PREDICTORS_NO_COLINEALES)]:
        a = diagnostic[cols].to_numpy(float)
        std = a.std(axis=0)
        z = (a - a.mean(axis=0)) / np.where(std > 0, std, 1)
        rank = np.linalg.matrix_rank(z)
        rank_rows.append(dict(moneda=currency, conjunto=name, filas=len(z), columnas=len(cols), rango=int(rank)))
        if name == "reducido_19":
            assert rank == len(cols)
        for j, col in enumerate(cols):
            y = z[:, j]
            x = np.delete(z, j, axis=1)
            residual = y - x @ np.linalg.lstsq(x, y, rcond=None)[0]
            sst, sse = y @ y, residual @ residual
            vif = np.inf if sst == 0 or sse <= 1e-12 * sst else sst / sse
            vif_rows.append(dict(moneda=currency, conjunto=name, predictor=col, VIF=vif))
rank_diagnostics, vif_diagnostics = pd.DataFrame(rank_rows), pd.DataFrame(vif_rows)
display(presentation(rank_diagnostics))
display(presentation(vif_diagnostics))
# Comparación descriptiva: no se eliminan estas filas del pipeline.
eligible_diagnostic = features.loc[features.utilizable_supervisado].copy()
eligible_diagnostic["caso_completo"] = eligible_diagnostic[PREDICTORS].notna().all(axis=1)
selection_summary = eligible_diagnostic.groupby(["Moneda", "caso_completo"]).agg(
    registros=("RPJ", "size"), empresas=("RPJ", "nunique"), activo_mediano=("ActivoTotal", "median"),
    historial_mediano=("historial_previo_contiguo", "median"), ingresos_no_positivos=("ingresos_no_positivos", "sum")).reset_index()
selection_tests = []
for currency, sub in eligible_diagnostic.groupby("Moneda"):
    a = sub.loc[sub.caso_completo, "ActivoTotal"]
    b = sub.loc[~sub.caso_completo, "ActivoTotal"]
    u, pvalue = mannwhitneyu(a, b, alternative="two-sided", method="asymptotic")
    selection_tests.append(dict(moneda=currency, completos=len(a), incompletos=len(b), U=float(u), p_exploratorio=float(pvalue)))
selection_tests = pd.DataFrame(selection_tests)
selection_by_year = eligible_diagnostic.groupby("Ejercicio").agg(elegibles=("RPJ", "size"), completos=("caso_completo", "sum")).reset_index()
revision_summary = eligible_diagnostic.groupby(["particion", "Moneda", "revision_interanual"]).agg(
    registros=("RPJ", "size"), empresas=("RPJ", "nunique")).reset_index()
revision_summary["proporcion_en_particion_moneda"] = revision_summary.registros / revision_summary.groupby(["particion", "Moneda"]).registros.transform("sum")
print("Empresas elegibles excluidas si se exigieran casos completos:",
      eligible_diagnostic.RPJ.nunique() - eligible_diagnostic.loc[eligible_diagnostic.caso_completo, "RPJ"].nunique())
display(presentation(selection_summary)); display(presentation(selection_tests)); display(selection_by_year)
display(presentation(revision_summary))
size_normalized = features[temporal].div(features.ActivoTotal.where(features.ActivoTotal.gt(0)), axis=0)
size_normalized.columns = [c + "_sobre_activo_t" for c in temporal]
size_normalized["objetivo_fcl_t1_sobre_activo_t"] = features.objetivo_fcl_t1 / features.ActivoTotal.where(features.ActivoTotal.gt(0))
assert not np.isinf(size_normalized.to_numpy(float)).any()
print("Sensibilidad normalizada: solo en memoria; objetivo y 22 predictores exportados sin ampliación.")''')]
nb.cells[insert_at:insert_at]=new
# Sin salidas obsoletas antes de la nueva ejecución.
for c in nb.cells:
    if c.cell_type=='code': c.outputs=[]; c.execution_count=None
nbformat.write(nb,p)
script=ROOT/'scripts/execute_feature_engineering.py'
s=script.read_text().replace('sys.version_info[:3] != (3, 12, 15)','sys.version_info[:2] != (3, 12)').replace('Se requiere tesis-fcl, Python 3.12.15','Se requiere tesis-fcl, Python 3.12.x')
script.write_text(s)
