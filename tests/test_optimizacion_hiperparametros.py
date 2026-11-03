"""Pruebas de la sesión IA07. Se omiten si Optuna no está instalado (entorno tesis-fcl sin el complemento de IA07)."""
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
try:
    import optuna  # noqa: F401
except ImportError as error:
    raise unittest.SkipTest('Optuna no disponible; usar el entorno de requirements-ia07.txt') from error
import src.optimizacion_hiperparametros as oh

OUT = oh.OUT
S06 = oh.ROOT / 'reports/sprint_06'
m = lag = fin = ratios = None


def setUpModule():
    global m, lag, fin, ratios
    m, lag, fin, ratios = oh.cargar_muestra()


def evaluador(cohorte=('D lares', 'todas'), nombre='E0_07', tabla=None):
    t, cols = oh.caracteristicas(nombre, cohorte, m, lag, fin)
    return oh.EvaluadorCV(oh.solo_entrenamiento(oh.subconjunto(t if tabla is None else tabla, *cohorte)), cols, ratios)


class DatosYParticionTests(unittest.TestCase):
    def test_particion_original_conservada(self):
        self.assertEqual(m.particion.value_counts().to_dict(), {'entrenamiento': 2869, 'prueba': 691})
        self.assertEqual(m.loc[m.particion.eq('entrenamiento'), 'anio_objetivo'].max(), 2021)
        pd.testing.assert_series_equal(lag.particion, m.particion)
        pd.testing.assert_series_equal(lag.objetivo_fcl_t1, m.objetivo_fcl_t1)

    def test_pliegues_iguales_al_notebook_08_y_sin_prueba(self):
        ref = pd.read_csv(S06 / 'mejoras/cv_folds.csv')
        for cohorte in oh.COHORTES:
            t = oh.solo_entrenamiento(oh.subconjunto(m, *cohorte))
            folds = oh.pliegues(t)
            r = ref[ref.moneda.eq(cohorte[0]) & ref.grupo.eq(cohorte[1])].drop_duplicates('fold').sort_values('fold')
            self.assertEqual([(len(a), len(b)) for a, b in folds], list(zip(r.n_train, r.n_validacion)))
            for a, b in folds:
                self.assertLess(t.loc[a].anio_objetivo.max(), t.loc[b].anio_objetivo.min())
                self.assertTrue(t.loc[a.union(b)].anio_objetivo.le(2021).all())

    def test_cohorte_dolares_no_bancaria_es_identica(self):
        self.assertTrue(oh.subconjunto(m, 'D lares', 'todas').id_fila.equals(oh.subconjunto(m, 'D lares', 'no_bancario').id_fila))

    def test_seleccion_08_coincide_con_su_archivo(self):
        ref = pd.read_csv(S06 / 'mejoras/seleccion_congelada_cv.csv')
        for (mo, gr), (spec, exp) in oh.SELECCION_08.items():
            r = ref[ref.moneda.eq(mo) & ref.grupo.eq(gr)].iloc[0]
            self.assertEqual((r.especificacion, r.experimento), (spec, exp))


class ReproduccionTests(unittest.TestCase):
    def test_baseline_ridge_07_reproducido(self):
        ref = pd.read_csv(S06 / 'predicciones_baseline.csv', float_precision='round_trip')
        ref = ref[ref.escenario.eq('principal')]
        for moneda in ('D lares', 'Soles'):
            t = oh.subconjunto(m, moneda, 'todas')
            tr = oh.solo_entrenamiento(t)
            for nombre, exp in (('E0_07', 'E0_financiero'), ('E1_07', 'E1_macroeconomico'), ('E2_07', 'E2_bursatil')):
                _, cols = oh.caracteristicas(nombre, (moneda, 'todas'), m, lag, fin)
                p = oh.crear_pipeline(cols, ratios, 1.).fit(tr[cols], tr.objetivo_fcl_t1).predict(t[cols])
                r = ref[ref.moneda.eq(moneda) & ref.experimento.eq(exp)].set_index('id_fila').loc[t.id_fila]
                np.testing.assert_allclose(p, r.y_predicho, rtol=1e-9, atol=1e-6)

    def test_puntuaciones_cv_08_reproducidas(self):
        ref = pd.read_csv(S06 / 'mejoras/cv_puntuaciones.csv', float_precision='round_trip')
        for cohorte in oh.COHORTES:
            for spec in ('niveles_t_externos_t', 'niveles_t_externos_t_1', 'sin_niveles_t_externos_t_1'):
                tabla = m if spec == 'niveles_t_externos_t' else lag
                for exp in ('E0_financiero', 'E1_macroeconomico', 'E2_bursatil'):
                    cols = oh.especificacion_08(spec, exp, fin)
                    ev = oh.EvaluadorCV(oh.solo_entrenamiento(oh.subconjunto(tabla, *cohorte)), cols, ratios)
                    r = ref[ref.moneda.eq(cohorte[0]) & ref.grupo.eq(cohorte[1]) & ref.especificacion.eq(spec) & ref.experimento.eq(exp)]
                    self.assertEqual(len(r), 6)
                    for f in r.itertuples():
                        np.testing.assert_allclose(ev.evaluar(f.alpha, 'standard', 'p01_p99')[0], f.mse_cv, rtol=1e-9)

    def test_predicciones_08_reproducidas(self):
        ref = pd.read_csv(S06 / 'mejoras/predicciones_seleccionadas_cv.csv', float_precision='round_trip')
        sel = pd.read_csv(S06 / 'mejoras/seleccion_congelada_cv.csv')
        for cohorte in oh.COHORTES:
            s = sel[sel.moneda.eq(cohorte[0]) & sel.grupo.eq(cohorte[1])].iloc[0]
            tabla, cols = oh.caracteristicas('seleccion_08', cohorte, m, lag, fin)
            t = oh.subconjunto(tabla, *cohorte)
            tr = oh.solo_entrenamiento(t)
            p = oh.crear_pipeline(cols, ratios, s.alpha, 'standard', 'p01_p99').fit(tr[cols], tr.objetivo_fcl_t1).predict(t[cols])
            r = ref[ref.moneda.eq(cohorte[0]) & ref.grupo_ajuste.eq(cohorte[1])]
            if len(r):
                np.testing.assert_allclose(p, r.set_index('id_fila').loc[t.id_fila].y_predicho, rtol=1e-9, atol=1e-6)
            else:
                completa = pd.read_csv(S06 / 'mejoras/predicciones_mejoras.csv', float_precision='round_trip')
                r = completa[completa.moneda.eq(cohorte[0]) & completa.grupo_ajuste.eq(cohorte[1]) & completa.especificacion.eq(s.especificacion) & completa.experimento.eq(s.experimento)]
                np.testing.assert_allclose(p, r.set_index('id_fila').loc[t.id_fila].y_predicho, rtol=1e-9, atol=1e-6)


class SinFugaTests(unittest.TestCase):
    def test_evaluador_rechaza_filas_de_prueba(self):
        t, cols = oh.caracteristicas('E0_07', ('Soles', 'todas'), m, lag, fin)
        with self.assertRaises(AssertionError):
            oh.EvaluadorCV(oh.subconjunto(t, 'Soles', 'todas'), cols, ratios)

    def test_perturbar_prueba_no_cambia_la_busqueda(self):
        alterada = m.copy()
        prueba = alterada.particion.eq('prueba')
        numericas = [c for c in alterada.select_dtypes('number').columns if c not in {'anio_objetivo', 'Ejercicio', 'id_fila'}]
        alterada[numericas] = alterada[numericas].astype(float)
        alterada.loc[prueba, numericas] = alterada.loc[prueba, numericas] * 100 + 1e4
        for metodo in oh.METODOS:
            a = oh.buscar(evaluador(), metodo, 7, 15)
            b = oh.buscar(evaluador(tabla=alterada), metodo, 7, 15)
            pd.testing.assert_frame_equal(a.drop(columns='duracion_s'), b.drop(columns='duracion_s'), check_exact=True)

    def test_control_positivo_alterar_validacion_si_cambia(self):
        alterada = m.copy()
        alterada['objetivo_fcl_t1'] = alterada.objetivo_fcl_t1.where(alterada.anio_objetivo.ne(2021), alterada.objetivo_fcl_t1 * 3)
        self.assertNotEqual(evaluador().evaluar(1.)[0], evaluador(tabla=alterada).evaluar(1.)[0])

    def test_recorte_aprendido_solo_en_entrenamiento(self):
        t, cols = oh.caracteristicas('E0_07', ('Soles', 'todas'), m, lag, fin)
        tr = oh.solo_entrenamiento(oh.subconjunto(t, 'Soles', 'todas'))
        pipe = oh.crear_pipeline(cols, ratios, 1., 'standard', 'p01_p99').fit(tr[cols], tr.objetivo_fcl_t1)
        interno = pipe.named_steps['preparacion'].named_transformers_['numericas']
        z = interno.named_steps['imputer'].transform(tr[cols])
        clip = interno.named_steps['clip']
        np.testing.assert_allclose(clip.lower_, np.quantile(z[:, clip.indices_], .01, axis=0))
        self.assertEqual({cols[i] for i in clip.indices_}, set(ratios))


class BusquedaTests(unittest.TestCase):
    def test_cache_igual_al_pipeline_completo(self):
        ev = evaluador(('Soles', 'bancario'), 'E1_07')
        t, cols = oh.caracteristicas('E1_07', ('Soles', 'bancario'), m, lag, fin)
        t = oh.solo_entrenamiento(oh.subconjunto(t, 'Soles', 'bancario'))
        for alpha, e, r in ((3., 'robust', 'p05_p95'), (500., 'standard', 'sin_recorte')):
            anuales = []
            for a, b in oh.pliegues(t):
                p = oh.crear_pipeline(cols, ratios, alpha, e, r).fit(t.loc[a, cols], t.loc[a].objetivo_fcl_t1).predict(t.loc[b, cols])
                d = (p - t.loc[b].objetivo_fcl_t1.to_numpy()) ** 2
                anuales += [d[t.loc[b].anio_objetivo.to_numpy() == y].mean() for y in sorted(t.loc[b].anio_objetivo.unique())]
            np.testing.assert_allclose(ev.evaluar(alpha, e, r)[0], np.mean(anuales), rtol=1e-12)

    def test_determinismo_y_presupuesto_equivalente(self):
        ev = evaluador()
        for metodo in oh.METODOS:
            a, b = oh.buscar(ev, metodo, 11, 20), oh.buscar(ev, metodo, 11, 20)
            pd.testing.assert_frame_equal(a.drop(columns='duracion_s'), b.drop(columns='duracion_s'), check_exact=True)
            self.assertEqual(len(a), 20)

    def test_muestreadores_correctos_y_distintos(self):
        self.assertIsInstance(oh.muestreador('random_search', 1), optuna.samplers.RandomSampler)
        self.assertIsInstance(oh.muestreador('tpe', 1), optuna.samplers.TPESampler)
        a = oh.buscar(evaluador(), 'random_search', 11, 30)
        b = oh.buscar(evaluador(), 'tpe', 11, 30)
        self.assertFalse(np.allclose(a.alpha, b.alpha))

    def test_espacio_respetado(self):
        a = oh.buscar(evaluador(), 'tpe', 5, 25)
        self.assertTrue(a.alpha.between(oh.ALPHA_MIN, oh.ALPHA_MAX).all())
        self.assertTrue(a.escalador.isin(oh.ESCALADORES).all() and a.recorte.isin(list(oh.RECORTES)).all())

    def test_holm(self):
        np.testing.assert_allclose(oh.holm([.01, .04, .03, .5]), [.04, .09, .09, .5])

    def test_eleccion_desempata_hacia_mayor_alpha(self):
        t = pd.DataFrame(dict(mse_cv=[2., 1., 1.], alpha=[5., 1., 9.], trial=[0, 1, 2]))
        self.assertEqual(oh.elegir(t).alpha, 9.)


@unittest.skipUnless((OUT / 'metricas_prueba.csv').exists(), 'resultados completos aún no generados')
class ResultadosTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trials = pd.read_csv(OUT / 'trials.csv')
        cls.sel = pd.read_csv(OUT / 'seleccion_congelada.csv')
        cls.met = pd.read_csv(OUT / 'metricas_prueba.csv')

    def test_protocolo_versionado(self):
        self.assertEqual(json.loads((OUT / 'protocolo.json').read_text(encoding='utf-8')), json.loads(json.dumps(oh.protocolo(), ensure_ascii=False)))

    def test_presupuestos_equivalentes(self):
        n = self.trials.groupby([*oh.ID_ESTUDIO, 'metodo', 'semilla']).size()
        self.assertTrue(n.eq(oh.PRESUPUESTO).all())
        self.assertEqual(len(n), len(oh.COHORTES) * len(oh.CARACTERISTICAS) * 2 * len(oh.SEMILLAS))
        self.assertTrue(self.trials.estado.eq('COMPLETE').all())

    def test_trials_reproducibles_desde_el_registro(self):
        g = self.trials[self.trials.moneda.eq('Soles') & self.trials.grupo.eq('bancario') & self.trials.caracteristicas.eq('seleccion_08') & self.trials.metodo.eq('tpe') & self.trials.semilla.eq(oh.SEMILLA_PRINCIPAL)]
        nuevo = oh.buscar(evaluador(('Soles', 'bancario'), 'seleccion_08', tabla=lag), 'tpe', oh.SEMILLA_PRINCIPAL)
        np.testing.assert_allclose(nuevo.mse_cv, g.sort_values('trial').mse_cv, rtol=1e-12)

    def test_ganadores_son_el_minimo_de_cv(self):
        for r in self.sel[self.sel.procedimiento.isin(oh.METODOS)].itertuples():
            g = self.trials[self.trials.moneda.eq(r.moneda) & self.trials.grupo.eq(r.grupo) & self.trials.caracteristicas.eq(r.caracteristicas) & self.trials.metodo.eq(r.procedimiento) & self.trials.semilla.eq(oh.SEMILLA_PRINCIPAL)]
            np.testing.assert_allclose(g.mse_cv.min(), r.mse_cv, rtol=1e-12)

    def test_congelacion_intacta_y_previa_a_prueba(self):
        registro = oh.verificar_congelacion(OUT)
        evaluacion = json.loads((OUT / 'evaluacion_prueba.json').read_text(encoding='utf-8'))
        self.assertEqual(registro['sha256'], evaluacion['sha256_seleccion'])
        self.assertLess(registro['congelada_utc'], evaluacion['evaluada_utc'])

    def test_evaluar_rechaza_seleccion_alterada(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            for f in ('seleccion_congelada.csv', 'seleccion_congelada.json'):
                shutil.copy(OUT / f, d / f)
            with open(d / 'seleccion_congelada.csv', 'a', encoding='utf-8') as h:
                h.write('alterada\n')
            with self.assertRaises(AssertionError):
                oh.evaluar_prueba(d)

    def test_metricas_reconstruidas_y_mismas_filas(self):
        pred = pd.read_csv(OUT / 'predicciones_prueba.csv', float_precision='round_trip')
        for r in self.met.itertuples():
            g = pred[pred.moneda.eq(r.moneda) & pred.grupo.eq(r.grupo) & pred.caracteristicas.eq(r.caracteristicas) & pred.procedimiento.eq(r.procedimiento)]
            np.testing.assert_allclose(np.sqrt(np.mean((g.y_real - g.y_predicho) ** 2)), r.RMSE, rtol=1e-9)
            self.assertEqual(set(g.id_fila), set(oh.subconjunto(m, r.moneda, r.grupo).query("particion=='prueba'").id_fila))
            self.assertTrue(g.anio_objetivo.between(2022, 2025).all())

    def test_baseline_y_rejilla_coinciden_con_metricas_previas(self):
        base = pd.read_csv(S06 / 'resultados_experimentos.csv')
        base = base[base.escenario.eq('principal') & base.particion.eq('prueba')]
        for ca, exp in (('E0_07', 'E0_financiero'), ('E1_07', 'E1_macroeconomico'), ('E2_07', 'E2_bursatil')):
            for mo in ('D lares', 'Soles'):
                a = self.met[self.met.moneda.eq(mo) & self.met.grupo.eq('todas') & self.met.caracteristicas.eq(ca) & self.met.procedimiento.eq('ridge_alpha1')].iloc[0]
                b = base[base.moneda.eq(mo) & base.experimento.eq(exp)].iloc[0]
                np.testing.assert_allclose([a.MAE, a.RMSE], [b.MAE, b.RMSE], rtol=1e-9)
        previas = pd.read_csv(S06 / 'mejoras/metricas_mejoras.csv')
        for (mo, gr), (spec, exp) in oh.SELECCION_08.items():
            a = self.met[self.met.moneda.eq(mo) & self.met.grupo.eq(gr) & self.met.caracteristicas.eq('seleccion_08') & self.met.procedimiento.eq('rejilla_08')].iloc[0]
            b = previas[previas.moneda.eq(mo) & previas.grupo_ajuste.eq(gr) & previas.especificacion.eq(spec) & previas.experimento.eq(exp) & previas.particion.eq('prueba')].iloc[0]
            np.testing.assert_allclose([a.alpha, a.RMSE], [b.alpha, b.RMSE], rtol=1e-9)

    def test_archivos_previos_sin_cambios(self):
        self.assertEqual(oh.estado_archivos_previos()['cambios_git'], [])
        registro = json.loads((OUT / 'integridad_previa.json').read_text(encoding='utf-8'))
        self.assertEqual(registro['sha256_panel'], hashlib.sha256(oh.PANEL.read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
