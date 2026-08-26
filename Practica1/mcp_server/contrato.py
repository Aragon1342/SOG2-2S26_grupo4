"""
Contrato entre los módulos de análisis (puntos 2 al 6) y el MCP Server.

Los compañeros que desarrollan el análisis NO necesitan saber nada de MCP:
solo escriben una función normal de pandas/matplotlib y la decoran con
@analisis(...). El servidor la detecta y la publica como tool del agente.
"""

from dataclasses import dataclass, field
from typing import Any, Callable

REGISTRO: dict[str, "Analisis"] = {}


@dataclass
class Resultado:
    """Lo que toda función de análisis debe devolver."""

    datos: list[dict[str, Any]] = field(default_factory=list)
    resumen: str = ""
    figura: Any | None = None


@dataclass
class Analisis:
    nombre: str
    descripcion: str
    funcion: Callable[..., Resultado]
    punto: str


def analisis(nombre: str, descripcion: str, punto: str = ""):
    """
    Decorador que registra una función de análisis como tool del agente.

    La `descripcion` es lo que lee el LLM para decidir cuándo invocarla,
    así que debe describir la pregunta que responde, no la implementación.
    Los parámetros de la función se vuelven parámetros de la tool, por lo que
    conviene anotarlos con tipos y darles valores por defecto.
    """

    def wrapper(func: Callable[..., Resultado]) -> Callable[..., Resultado]:
        if nombre in REGISTRO:
            raise ValueError(f"Ya existe un análisis llamado '{nombre}'")
        REGISTRO[nombre] = Analisis(nombre, descripcion, func, punto)
        return func

    return wrapper
