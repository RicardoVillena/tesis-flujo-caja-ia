"""Ejecutar desde cualquier directorio con el entorno tesis-fcl existente."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.clasificacion_sectorial import run
if __name__ == '__main__':
    _, _, audit = run(ROOT)
    for key in ['observaciones','empresas','empresas_con_alguna_clasificacion',
                'industrias_identificadas','empresas_con_registros_pendientes']:
        print(f'{key}: {audit[key]}')
