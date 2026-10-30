"""Verifica comparabilidad, reconstrucción y continuidad con Sprint 08."""
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / 'reports/sprint_09'


def test_mismas_filas_y_particion_temporal():
    p = pd.read_csv(OUT/'predicciones.csv')
    assert p.anio_objetivo.between(2017, 2021).all()
    for _, g in p.groupby(['moneda', 'anio_objetivo']):
        groups = list(g.groupby(['modelo', 'variante']))
        expected = groups[0][1].set_index('id_fila').y_real.sort_index()
        assert len(groups) == 8
        for _, v in groups:
            assert not v.id_fila.duplicated().any()
            pd.testing.assert_series_equal(v.set_index('id_fila').y_real.sort_index(), expected)
    searches = pd.read_csv(OUT/'busquedas.csv')
    for r in searches.itertuples():
        assert all(y < r.anio_externo for y in [int(c.split('_')[1]) for c in searches.columns if c.startswith('rmse_') and c != 'rmse_interno_medio' and pd.notna(getattr(r, c))])


def test_metricas_recalculadas_y_regla():
    p = pd.read_csv(OUT/'predicciones.csv')
    annual = pd.read_csv(OUT/'metricas_por_anio.csv')
    for r in annual.itertuples():
        g = p[(p.moneda == r.moneda) & (p.modelo == r.modelo) & (p.variante == r.variante) & (p.anio_objetivo == r.anio_externo)]
        assert np.isclose(np.sqrt(np.mean((g.y_real-g.y_predicho)**2)), r.RMSE)
        assert np.isclose(np.mean(abs(g.y_real-g.y_predicho)), r.MAE)
    c = pd.read_csv(OUT/'comparacion_incremental.csv')
    assert (c.mejora_consistente == ((c.delta_RMSE_pct <= -1) & (c.anios_mejora >= 4) & (c.delta_MAE_pct <= 0))).all()


def test_e2_reproduce_sprint_08():
    previous = pd.read_csv(OUT.parent/'sprint_08/comparacion_modelos/resumen_procedimientos.csv')
    current = pd.read_csv(OUT/'resumen.csv')
    joint = current[current.variante.eq('E2')].merge(previous, left_on=['moneda','modelo'], right_on=['moneda','procedimiento'], suffixes=('_actual','_previo'))
    assert len(joint) == 4
    for metric in ['RMSE_anual_medio','MAE_anual_medio']:
        np.testing.assert_allclose(joint[metric+'_actual'], joint[metric+'_previo'], rtol=1e-10)


def test_importancia_completa_y_signo():
    imp = pd.read_csv(OUT/'importancia_por_anio.csv')
    assert len(imp) == 2*2*5*26
    assert imp.groupby(['moneda','modelo','anio_externo']).atributo.nunique().eq(26).all()
    np.testing.assert_allclose(imp.delta_RMSE, imp.RMSE_sin_atributo-imp.RMSE_completo, atol=1e-8)
