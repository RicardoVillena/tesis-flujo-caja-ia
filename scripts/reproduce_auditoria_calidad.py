"""Reproduce Sprint 08 sin red ni modelos predictivos."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.auditoria_calidad import run
if __name__=='__main__':
    tables=run()
    print('Sprint 08 reproducido:', {k:len(v) for k,v in tables.items()})
