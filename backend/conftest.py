import sys
from pathlib import Path

# Backend-Wurzel auf den Importpfad legen, damit Tests `menu`, `db`, ... finden.
sys.path.insert(0, str(Path(__file__).resolve().parent))
