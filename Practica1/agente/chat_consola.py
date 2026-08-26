"""
Chat Interactivo de Consola con el Agente de IA (Google ADK + FastMCP).
Permite a cualquier usuario o evaluador conversar directamente con el agente
en la terminal y obtener análisis, cifras y gráficas en tiempo real.
"""

import asyncio
import os
import pathlib
import sys
from dotenv import load_dotenv

# Configuración de rutas
AGENTE_DIR = pathlib.Path(__file__).resolve().parent
PRACTICA = AGENTE_DIR.parent
RAIZ = PRACTICA.parent

if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
if str(PRACTICA) not in sys.path:
    sys.path.insert(0, str(PRACTICA))

load_dotenv(PRACTICA / ".env")

from google.adk.runners import InMemoryRunner
from google.genai import types
from Practica1.agente.agent import root_agent


async def iniciar_chat():
    print("=" * 80)
    print("🤖 CHAT INTERACTIVO: AGENTE ANALISTA DE VENTAS 2021 (GOOGLE ADK + FASTMCP)")
    print("=" * 80)
    print("Conectado a: AWS RDS PostgreSQL (Base de datos de Ventas)")
    print("Modelo IA:   ", os.getenv("MODELO", "gemini-2.5-flash"))
    print("\nEscribe tu pregunta sobre ventas, clientes, tendencias o segmentación.")
    print("Escribe 'salir' o 'exit' para terminar la sesión.")
    print("=" * 80)

    runner = InMemoryRunner(agent=root_agent, app_name=root_agent.name)
    user_id = "usuario_demo"
    session = await runner.session_service.create_session(app_name=root_agent.name, user_id=user_id)

    while True:
        try:
            pregunta = input("\n👤 Tú: ").strip()
            if not pregunta:
                continue
            if pregunta.lower() in ["salir", "exit", "quit", "q"]:
                print("\n👋 ¡Sesión finalizada con éxito!")
                break

            print("\n⏳ Analizando en la base de datos...")
            msg = types.Content(
                role="user",
                parts=[types.Part.from_text(text=pregunta)],
            )

            async for event in runner.run_async(
                session_id=session.id,
                user_id=user_id,
                new_message=msg,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(f"\n🤖 Agente: {part.text}")
                        if part.function_call:
                            print(f"   ⚙️ [Invocando Tool MCP en AWS RDS]: {part.function_call.name}")

        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Sesión terminada.")
            break
        except Exception as e:
            print(f"\n⚠️ Error al procesar consulta: {e}")


if __name__ == "__main__":
    asyncio.run(iniciar_chat())
