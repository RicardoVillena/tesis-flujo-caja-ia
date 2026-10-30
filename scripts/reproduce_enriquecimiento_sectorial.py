"""Reproducción local sin red, PDF parser ni entrenamiento."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.enriquecimiento_sectorial import run
if __name__=='__main__':
    _,tables,audit=run(ROOT)
    print(tables['comparacion_cobertura.csv'].to_string(index=False))
