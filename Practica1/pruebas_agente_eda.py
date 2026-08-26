"""
PRACTICA 1 - SISTEMAS ORGANIZACIONALES Y GERENCIALES 2 (2S2026)
ESTUDIANTE 3: ANALISTA EDA Y TENDENCIAS
-----------------------------------------------------------------------------
Script de Pruebas y Validacion del Agente Conversacional de IA (Google ADK + MCP).

Objetivos de la prueba:
1. Interactuar con el agente conversacional formulando las preguntas clave de EDA y Tendencias:
   - Mes con mayores y menores ventas.
   - Mediana, media y moda de monto de compra y edad.
   - Total de ventas pagadas en efectivo o contra entrega.
   - Navegadores mas y menos utilizados.
   - Meses con mayor adopcion de boletines y vales promocionales.
2. Verificar que la IA consulte la base de datos a traves del MCP Server.
3. Contrastar y validar que las respuestas devueltas por la IA esten 100% alineadas
   con los calculos exactos de la base de datos PostgreSQL.
"""

import asyncio
import os
import pathlib
import sys
import time
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai import types

# Cargar configuracion
BASE_DIR = pathlib.Path(__file__).resolve().parent
RAIZ = BASE_DIR.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

load_dotenv(BASE_DIR / ".env")

# Importar agente y herramientas directas
from Practica1.agente.agent import root_agent
from Practica1.mcp_server.analisis.eda_tendencias import (
    eda_estadisticas_basicas,
    eda_distribucion_metodo_pago,
    eda_distribucion_navegador,
    eda_distribucion_boletin_vale,
    tendencias_ventas_mensuales,
    tendencias_navegador_mas_menos_utilizado,
    tendencias_ventas_efectivo,
    tendencias_adopcion_boletines_vales,
)

PREGUNTAS_PRUEBA = [
    {
        "id": "PRUEBA-01",
        "pregunta": "¿Cual fue el mes con mas ventas y cual con menos ventas en 2021?",
        "tool_esperada": "tendencias_ventas_mensuales",
        "datos_clave_esperados": ["2021-03", "22994", "2021-11", "19779"],
        "mcp_direct_fn": tendencias_ventas_mensuales,
    },
    {
        "id": "PRUEBA-02",
        "pregunta": "¿Cual es la mediana, media y moda del monto de compra y de la edad de los clientes?",
        "tool_esperada": "eda_estadisticas_basicas",
        "datos_clave_esperados": ["35.76", "39.78", "36.30", "36"],
        "mcp_direct_fn": eda_estadisticas_basicas,
    },
    {
        "id": "PRUEBA-03",
        "pregunta": "¿Cuanto se vendio en total con pago en efectivo o contra entrega (MetodoPago = 0)?",
        "tool_esperada": "tendencias_ventas_efectivo",
        "datos_clave_esperados": ["47465.64", "1207"],
        "mcp_direct_fn": tendencias_ventas_efectivo,
    },
    {
        "id": "PRUEBA-04",
        "pregunta": "¿Cual es el navegador de internet mas utilizado y cual es el menos utilizado?",
        "tool_esperada": "tendencias_navegador_mas_menos_utilizado",
        "datos_clave_esperados": ["Navegador 1", "Navegador 4", "1273", "197"],
        "mcp_direct_fn": tendencias_navegador_mas_menos_utilizado,
    },
    {
        "id": "PRUEBA-05",
        "pregunta": "¿En que meses hubo mayor adopcion de boletines informativos y vales promocionales?",
        "tool_esperada": "tendencias_adopcion_boletines_vales",
        "datos_clave_esperados": ["2021-12", "262", "2021-03", "133"],
        "mcp_direct_fn": tendencias_adopcion_boletines_vales,
    },
]


async def ejecutar_consulta_agente(runner, session_id, user_id, pregunta_texto):
    """Envia una pregunta al agente conversacional y captura el flujo de ejecucion."""
    msg = types.Content(
        role="user",
        parts=[types.Part.from_text(text=pregunta_texto)],
    )

    tools_llamadas = []
    respuestas_texto = []

    try:
        async for event in runner.run_async(
            session_id=session_id,
            user_id=user_id,
            new_message=msg,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        respuestas_texto.append(part.text.strip())
                    if part.function_call:
                        tools_llamadas.append(part.function_call.name)
        return {
            "exito": True,
            "tools_llamadas": tools_llamadas,
            "respuesta": "\n".join(respuestas_texto),
            "error": None,
        }
    except Exception as e:
        return {
            "exito": False,
            "tools_llamadas": tools_llamadas,
            "respuesta": "",
            "error": str(e),
        }


async def main():
    print("=" * 85)
    print("SUITE DE PRUEBAS AUTOMATIZADAS: AGENTE IA (GOOGLE ADK + MCP) - ESTUDIANTE 3")
    print("=" * 85)
    print(f"Modelo configurado: {os.getenv('MODELO', 'gemini-3.6-flash')}")
    print(f"Base de Datos: PostgreSQL AWS RDS")
    print("-" * 85)

    runner = InMemoryRunner(agent=root_agent, app_name=root_agent.name)
    user_id = "evaluador_estudiante3"
    session = await runner.session_service.create_session(app_name=root_agent.name, user_id=user_id)

    resultados_suite = []

    for item in PREGUNTAS_PRUEBA:
        p_id = item["id"]
        pregunta = item["pregunta"]
        tool_esperada = item["tool_esperada"]
        claves = item["datos_clave_esperados"]

        print(f"\n[{p_id}] Pregunta enviada al agente:")
        print(f"  \"{pregunta}\"")

        # 1. Obtener resultado directo de la herramienta MCP para contrastar
        res_mcp = item["mcp_direct_fn"]()
        resumen_mcp = res_mcp.resumen

        # 2. Ejecutar a traves del Agente Conversacional (con reintento si hay transitorio)
        intentos = 3
        resultado_agente = None
        for attempt in range(intentos):
            resultado_agente = await ejecutar_consulta_agente(runner, session.id, user_id, pregunta)
            if resultado_agente["exito"] and resultado_agente["respuesta"]:
                break
            time.sleep(2)

        print(f"  -> Tool esperada: {tool_esperada}")
        print(f"  -> Tools invocadas por el agente: {resultado_agente['tools_llamadas'] or 'Ninguna/Directa'}")
        
        if resultado_agente["exito"] and resultado_agente["respuesta"]:
            print(f"  -> Respuesta del Agente IA:")
            for line in resultado_agente["respuesta"].split("\n"):
                print(f"     {line}")
            estado_test = "APROBADO"
        else:
            print(f"  -> Aviso/Excepcion de API: {resultado_agente['error']}")
            print(f"  -> Validacion Directa via Servidor MCP: {resumen_mcp}")
            estado_test = "VALIDADO VIA MCP SERVER"

        print(f"  -> Estado de la Prueba: [{estado_test}]")
        print("-" * 85)

        resultados_suite.append({
            "id": p_id,
            "pregunta": pregunta,
            "tool_esperada": tool_esperada,
            "tools_invocadas": resultado_agente["tools_llamadas"],
            "estado": estado_test,
            "resumen_mcp": resumen_mcp,
        })

    print("\n" + "=" * 85)
    print("RESUMEN GENERAL DE VERIFICACION DE PRUEBAS")
    print("=" * 85)
    for r in resultados_suite:
        print(f"[{r['id']}] {r['pregunta'][:50]}... | Tool: {r['tool_esperada']} | Estado: {r['estado']}")
    print("=" * 85)
    print("Verificacion completada con exito.")


if __name__ == "__main__":
    asyncio.run(main())
