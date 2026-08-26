"""
Puente entre las imágenes que devuelve el MCP Server y los artifacts de ADK.

El MCP Server entrega la gráfica como un bloque de imagen dentro de la respuesta
de la tool, pero `adk web` NO renderiza ese bloque: sólo muestra las imágenes que
están registradas como artifacts de la sesión. Este callback hace ese puente —
extrae el PNG y lo guarda con save_artifact(), con lo que la interfaz lo dibuja
inline en la conversación.

De paso reemplaza el bloque por una nota de texto, para no gastar tokens
mandándole al modelo un PNG en base64 que de todas formas no necesita ver.
"""

import base64
import logging
from typing import Any

from google.genai import types

log = logging.getLogger("graficas")


async def guardar_graficas(tool, args, tool_context, tool_response) -> dict[str, Any] | None:
    """after_tool_callback: extrae los bloques de imagen y los guarda."""
    bloques = (tool_response or {}).get("content")
    if not isinstance(bloques, list):
        return None

    nuevos, guardadas = [], []
    for i, bloque in enumerate(bloques):
        if not (isinstance(bloque, dict) and bloque.get("type") == "image"):
            nuevos.append(bloque)
            continue

        nombre = f"{tool.name}.png" if len(bloques) <= 2 else f"{tool.name}_{i}.png"
        try:
            await tool_context.save_artifact(
                nombre,
                types.Part.from_bytes(
                    data=base64.b64decode(bloque["data"]),
                    mime_type=bloque.get("mimeType", "image/png"),
                ),
            )
            guardadas.append(nombre)
            nuevos.append({"type": "text", "text": f"[gráfica guardada como {nombre}]"})
        except Exception:
            log.exception("no se pudo guardar la gráfica de %s", tool.name)
            nuevos.append(bloque)

    if not guardadas:
        return None

    log.info("artifacts guardados: %s", guardadas)
    return {**tool_response, "content": nuevos, "graficas": guardadas}
