"""Ejecutar desde la raíz con Python del entorno tesis-fcl; no instala paquetes."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if Path(sys.prefix).name != 'tesis-fcl' or sys.version_info[:2] != (3, 12):
    raise RuntimeError('Se requiere tesis-fcl, Python 3.12.x')
if subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() not in {'feature-engineering', 'feature-engineering-semana5-presentacion'}:
    raise RuntimeError('Se requiere la rama feature-engineering')
# Cache y runtime dentro del repositorio, ignorados por Git.
cache = ROOT / '.cache' / 'feature-engineering'
for key, child in [('JUPYTER_RUNTIME_DIR', 'jupyter'), ('IPYTHONDIR', 'ipython'), ('MPLCONFIGDIR', 'matplotlib')]:
    folder = cache / child
    folder.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(folder)
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
import nbformat
from nbclient import NotebookClient

protected = [ROOT / p for p in [
    'notebooks/EDA_FCL_2005_2025.ipynb', 'data/processed/panel_fcl_preliminar.csv',
    'data/raw/base_de_datos.xlsx', 'src/ingestion/ingest_smv.py']]
protected.extend(p for p in (ROOT / 'data/raw/smv').rglob('*') if p.is_file())
def hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
before = hashes()
p = ROOT / 'notebooks/02_feature_engineering.ipynb'
nb = nbformat.read(p, as_version=4)
NotebookClient(nb, timeout=180, kernel_name='tesis-fcl',
               resources={'metadata': {'path': str(ROOT)}}).execute()
code_cells = [c for c in nb.cells if c.cell_type == 'code']
assert all(c.execution_count is not None for c in code_cells)
assert not any(o.output_type == 'error' for c in code_cells for o in c.outputs)
assert hashes() == before, 'Cambió un archivo protegido'
nbformat.write(nb, p)
validation = dict(kernel='tesis-fcl', python=sys.version, executable=sys.executable,
                  celdas_codigo_ejecutadas=len(code_cells), celdas_totales=len(nb.cells),
                  errores=0, archivos_protegidos_sin_cambios=before)
(ROOT / 'reports/validacion_ejecucion.json').write_text(
    json.dumps(validation, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'Notebook ejecutado: {len(code_cells)} celdas de código, sin errores; {len(protected)} archivos protegidos intactos.')
