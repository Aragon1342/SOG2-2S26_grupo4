"""Utilidades compartidas por los módulos de análisis."""

MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def nombre_mes(fecha) -> str:
    """'2021-03-01' -> 'marzo de 2021' (sin depender del locale del sistema)."""
    return f"{MESES[fecha.month - 1]} de {fecha.year}"
