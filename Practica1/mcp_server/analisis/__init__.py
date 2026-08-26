"""
Autocarga de módulos de análisis.

Cualquier archivo .py que se coloque en esta carpeta se importa al arrancar el
servidor, y sus funciones decoradas con @analisis quedan publicadas como tools.
No hay que registrar nada a mano en ningún otro lado.
"""

import importlib
import pkgutil
from pathlib import Path

_paquete = Path(__file__).parent

for _, nombre, _ in pkgutil.iter_modules([str(_paquete)]):
    importlib.import_module(f"{__name__}.{nombre}")
