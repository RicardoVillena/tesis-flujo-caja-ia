"""Regenera o comprueba todos los cálculos desde el panel entregado, sin kernel.
Uso: python scripts/reproduce_features.py [--check]
--check no modifica el CSV. Los informes se actualizan con evidencia verificable.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
import pandas as pd
from src.feature_engineering import build_features, RATIOS


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def details(name):
    """Expresiones equivalentes a las aplicadas en build_features."""
    continuity = 'En t y moneda de la fila; no combina ejercicios ni monedas.'
    missing = 'Propaga NaN; no imputa. Numerador cero se conserva.'
    domain = 'Denominador > 0; cero, negativo o faltante produce NaN; infinito se convierte en NaN.'
    if name in RATIOS:
        num, den, sign = RATIOS[name]
        columns = [num, den]
        expr = f'divide(d.{num} * ({sign}), d.{den})'
        if num == 'CAPEX_reportado':
            expr = f'divide((-d.{num}).where(d.{num} <= 0), d.{den})'
            domain += ' CAPEX positivo se invalida.'
        if num == 'TotalIngreso':
            expr = f'divide(d.{num}.where(d.{num} > 0), d.{den})'
            domain += ' Ingreso actual <= 0 se invalida.'
    elif name.startswith('crecimiento_'):
        col = name.removeprefix('crecimiento_')
        columns = [col, 'RPJ', 'Ejercicio', 'Moneda']
        current = f'd.{col}.where(d.{col} > 0)' if col == 'TotalIngreso' else f'd.{col}'
        expr = f'prev = groups[{col!r}].shift(1); divide({current} - prev, prev)'
        continuity = 'Requiere t-1 exacto en el mismo segmento anual de empresa y moneda.'
        if col == 'TotalIngreso':
            domain += ' Ingreso actual <= 0 se invalida.'
    elif name.startswith('cambio_'):
        col = name.removeprefix('cambio_').removesuffix('_activo_previo')
        columns = [col, 'ActivoTotal', 'RPJ', 'Ejercicio', 'Moneda']
        expr = f'divide(d[{col!r}] - groups[{col!r}].shift(1), groups.ActivoTotal.shift(1))'
        continuity = 'Requiere t-1 exacto en el mismo segmento anual de empresa y moneda.'
    else:
        col = 'FCL_preliminar' if name.startswith('FCL_preliminar') else 'FCO'
        columns = [col, 'RPJ', 'Ejercicio', 'Moneda']
        if '_lag' in name:
            lag = int(name[-1])
            expr = f'groups[{col!r}].shift({lag})'
            continuity = f'Requiere {lag} filas anuales anteriores del mismo segmento, sin huecos ni cambios de moneda.'
            missing = 'NaN si falta el valor desplazado o la historia suficiente; sin imputación.'
        else:
            stat = 'mean' if '_mean' in name else 'std'
            expr = f'groups[{col!r}].transform(lambda s: s.shift(1).rolling(3, min_periods=3).{stat}())'
            continuity = 'Requiere t-3, t-2 y t-1 contiguos en la misma empresa y moneda; excluye t.'
            missing = 'Los tres valores previos deben estar observados; cualquier NaN invalida la ventana.'
        domain = 'No hay denominador financiero; ceros y flujos negativos son válidos.'
        if '_std' in name:
            domain += ' Desviación muestral ddof=1 (divide por 3-1).'
    if 'FCL_preliminar' in columns:
        columns.append('CAPEX_reportado')
        missing += ' Todas las derivaciones usan FCL validado: NaN cuando CAPEX de su año > 0; no altera FCL fuente.'
    return dict(columnas_originales=columns, python=expr, faltantes=missing,
                ceros_y_dominio=domain, continuidad_y_moneda=continuity)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    source = ROOT / 'data/processed/panel_fcl_preliminar.csv'
    output = ROOT / 'data/processed/features_financieras.csv'
    raw = pd.read_csv(source, dtype={'RPJ': str, 'RUC': str}, encoding='utf-8-sig')
    features, predictors, dictionary = build_features(raw)
    assert len(features) == len(raw) == 4221
    assert len(predictors) == 22 and features.shape[1] == 57
    canonical = raw.sort_values(['RPJ', 'Ejercicio']).reset_index(drop=True)
    pd.testing.assert_frame_equal(features[raw.columns], canonical)
    valid = raw[['FCO', 'CAPEX_reportado', 'FCL_preliminar']].notna().all(axis=1)
    np.testing.assert_allclose(raw.loc[valid, 'FCL_preliminar'],
        raw.loc[valid, 'FCO'] + raw.loc[valid, 'CAPEX_reportado'], rtol=0, atol=0)
    serialized = features.to_csv(index=False)
    if args.check:
        assert output.read_bytes() == serialized.encode('utf-8'), 'CSV difiere de regeneración exacta'
    else:
        output.write_bytes(serialized.encode('utf-8'))
    reread = pd.read_csv(io.StringIO(serialized), dtype={'RPJ': str, 'RUC': str})
    pd.testing.assert_frame_equal(features, reread, check_dtype=False, rtol=1e-12, atol=1e-12)
    assert features.isna().equals(reread.isna()), 'Cambió la máscara de NaN'
    evidence = []
    text = ['# Trazabilidad de las 22 características y los objetivos\n',
        'Generado por `scripts/reproduce_features.py` a partir del código y del panel incluido.\n',
        'Implementación: `src/feature_engineering.py::build_features`. `divide` acepta solo denominador positivo.\n',
        '`d` está ordenado por RPJ/ejercicio; `groups` agrupa RPJ y segmento_temporal. Un hueco anual o cambio de moneda rompe el segmento, incluso si vuelve la moneda original.\n',
        'No se eliminan filas ni imputan valores; NaN se serializa como campo vacío. Escala monetaria no acreditada. Los predictores son retrospectivos según ejercicio, sin fechas de publicación verificadas.\n',
        'Cada validación de exportación compara todas las filas y la máscara de NaN contra una regeneración independiente del notebook; no acredita el origen contable de las fuentes. Las pruebas sintéticas cubren ceros, faltantes, límites temporales, moneda y ausencia de influencia futura.\n']
    for name in predictors:
        meta = dictionary.set_index('nombre').loc[name]
        item = dict(nombre=name, definicion=meta.justificacion, formula=meta.formula,
                    unidad=meta.unidad, **details(name), observados=int(features[name].notna().sum()),
                    faltantes_n=int(features[name].isna().sum()),
                    infinitos=int(np.isinf(features[name].to_numpy(dtype=float)).sum()),
                    coincide_csv=True, conserva_nan=True)
        evidence.append(item)
        text += [f'## {name}\n', f'- Definición: {item["definicion"]}.',
            f'- Fórmula: {item["formula"]}.', f'- Unidad: {item["unidad"]}.',
            '- Columnas originales: ' + ', '.join(item['columnas_originales']) + '.',
            f'- Python: `{item["python"]}`.', f'- Faltantes: {item["faltantes"]}',
            f'- Ceros/dominio: {item["ceros_y_dominio"]}',
            f'- Continuidad/moneda: {item["continuidad_y_moneda"]}',
            f'- Validación: {item["observados"]} observados, {item["faltantes_n"]} NaN, {item["infinitos"]} infinitos; todas las filas y NaN coinciden con el CSV.\n']
    text += ['## FCL_preliminar (fuente y objetivo contemporáneo)\n',
        '`FCL_preliminar = FCO + CAPEX_reportado`, respetando el signo original de CAPEX. No es FCFF económicamente validado. Se verifica la identidad exacta en las ' + str(int(valid.sum())) + ' filas con los tres componentes observados.\n',
        'El constructor conserva la columna fuente, incluidos sus NaN; no reconstruye ni rellena FCL. Una suma con componente faltante no permitiría calcular un nuevo FCL. Para derivaciones y objetivo futuro, usa `raw.FCL_preliminar.where(~raw.CAPEX_reportado.gt(0))`: CAPEX positivo invalida; CAPEX faltante no activa esa bandera (limitación explícita).\n',
        'No hay denominador. Cero y flujos negativos son válidos; se conserva moneda de la fila. Código de extracción histórica de FCO/CAPEX, filtros y revisiones ausente; no se presenta este control aritmético como prueba de origen.\n',
        '## objetivo_fcl_t1\n',
        'Etiqueta: FCL validado de la misma empresa en el año calendario exacto t+1, sin imputar. Se copia `(RPJ, Ejercicio, Moneda, FCL_validado)`, se resta 1 a Ejercicio y se une por RPJ/ejercicio (`left`, `validate="one_to_one"`). Nunca se usa la siguiente fila como sustituto del siguiente año.\n',
        'Si falta t+1 o su FCL, la etiqueta es NaN. No tiene denominador; cero y valores negativos son válidos. Si cambia moneda, se conserva la etiqueta reportada y `moneda_objetivo`, pero `objetivo_moneda_consistente=False` y `utilizable_supervisado=False`. No se convierte moneda. CAPEX positivo en t+1 invalida su etiqueta.\n',
        '`anio_objetivo = Ejercicio + 1`. Elegibilidad exige etiqueta observada y moneda consistente. Entrenamiento: año objetivo <=2021; prueba: 2022–2025; resto sin etiqueta elegible. Objetivo y controles futuros se excluyen de X.\n',
        f'Validación: {features.objetivo_fcl_t1.notna().sum()} etiquetas observadas; {features.objetivo_fcl_t1.isna().sum()} NaN; {features.utilizable_supervisado.sum()} elegibles. Pruebas: unión anual exacta, cambios de moneda, faltantes y CAPEX positivo; coincidencia completa de la etiqueta exportada.\n']
    report = dict(filas=len(features), columnas=len(features.columns), predictores=22,
        panel_sha256=sha(source), features_sha256=sha(output), csv_regenerado_identico=True,
        fuentes_preservadas=True, mascara_nan_preservada=True, identidad_fcl_filas_verificadas=int(valid.sum()),
        variables=evidence)
    (ROOT / 'reports/validacion_calculos.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    (ROOT / 'reports/trazabilidad_variables.md').write_text('\n\n'.join(text).rstrip()+'\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'variables'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
