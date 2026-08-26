"""Agente conversacional con Google ADK conectado al MCP Server del grupo."""

import os
import pathlib
import sys

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StdioConnectionParams,
    StdioServerParameters,
)

from .graficas import guardar_graficas

PRACTICA = pathlib.Path(__file__).resolve().parents[1]
RAIZ = PRACTICA.parent

load_dotenv(PRACTICA / ".env")

root_agent = LlmAgent(
    model=os.getenv("MODELO", "gemini-3.6-flash"),
    name="analista_ventas",
    instruction=(
        "Eres un analista de datos que responde sobre las ventas de 2021 de la "
        "empresa. Responde SIEMPRE consultando las herramientas disponibles; "
        "nunca inventes cifras ni las estimes de memoria. Cuando una herramienta "
        "genere una gráfica, esta se muestra automáticamente en la conversación: "
        "no anuncies dónde está, simplemente interpreta lo que muestra. "
        "Los montos no tienen moneda asociada, así que preséntalos como cifras "
        "sin símbolo de dólar ni de euro. "
        "Responde en español, de forma breve y concreta."
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=sys.executable,
                    args=["-m", "Practica1.mcp_server.server"],
                    cwd=str(RAIZ),
                ),
                timeout=60.0,
            )
        )
    ],
    after_tool_callback=guardar_graficas,
)
