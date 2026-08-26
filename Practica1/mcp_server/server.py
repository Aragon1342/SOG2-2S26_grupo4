"""
MCP Server — Práctica 1 SOG2, grupo 4.

Toma cada función registrada en analisis/ y la publica como tool MCP.
Agregar un análisis nuevo NO requiere tocar este archivo.
"""

import inspect
import io
import json
import logging

from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent, TextContent

from . import analisis as _
from .contrato import REGISTRO, Analisis, Resultado

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("mcp-ventas")

mcp = FastMCP("analisis-ventas-2021")


def _figura_a_png(figura) -> bytes:
    buffer = io.BytesIO()
    figura.savefig(buffer, format="png", dpi=110, bbox_inches="tight")
    import matplotlib.pyplot as plt

    plt.close(figura)
    return buffer.getvalue()


def _a_contenido_mcp(resultado: Resultado) -> list[TextContent | ImageContent]:
    import base64

    partes: list[TextContent | ImageContent] = [
        TextContent(
            type="text",
            text=json.dumps(
                {"resumen": resultado.resumen, "datos": resultado.datos},
                ensure_ascii=False,
                default=str,
            ),
        )
    ]
    if resultado.figura is not None:
        png = _figura_a_png(resultado.figura)
        partes.append(
            ImageContent(
                type="image",
                data=base64.b64encode(png).decode(),
                mimeType="image/png",
            )
        )
    return partes


def _publicar(a: Analisis) -> None:
    def tool(**kwargs):
        log.info("tool=%s args=%s", a.nombre, kwargs)
        try:
            return _a_contenido_mcp(a.funcion(**kwargs))
        except Exception as exc:
            log.exception("falló %s", a.nombre)
            return [TextContent(type="text", text=f"Error en '{a.nombre}': {exc}")]

    tool.__name__ = a.nombre
    tool.__doc__ = f"{a.descripcion} (Punto {a.punto} del enunciado.)"
    tool.__signature__ = inspect.signature(a.funcion).replace(
        return_annotation=inspect.Signature.empty
    )
    mcp.tool(name=a.nombre, description=tool.__doc__, structured_output=False)(tool)


for _a in REGISTRO.values():
    _publicar(_a)

log.info("Tools publicadas: %s", ", ".join(sorted(REGISTRO)) or "(ninguna)")


if __name__ == "__main__":
    mcp.run(transport="stdio")
