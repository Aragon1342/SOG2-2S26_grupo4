"""
Modulo de Analisis Exploratorio de Datos (EDA) y Tendencias.
Estudiante 3: Analista EDA y Tendencias (Puntos 2 y 3 del alcance).

Este modulo expone herramientas registradas con @analisis para que el servidor
MCP y el agente conversacional de Google ADK puedan responder preguntas sobre
estadisticas descriptivas, distribucion de ventas y patrones temporales.
"""

from typing import Optional
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..contrato import Resultado, analisis
from ..db import consultar


@analisis(
    nombre="eda_estadisticas_basicas",
    descripcion=(
        "Calcula las estadisticas basicas descriptivas (media, mediana, moda, "
        "minimo, maximo y desviacion estandar) de las variables numericas principales: "
        "Venta_total, MontoCompra, N_Compras, Edad y Tiempo de sesion."
    ),
    punto="2.b",
)
def eda_estadisticas_basicas(variable: Optional[str] = None) -> Resultado:
    """Calcula media, mediana y moda para variables numericas."""
    sql_clientes = "SELECT edad, venta_total, n_compras FROM clientes;"
    sql_ventas = "SELECT monto_compra, tiempo FROM ventas;"

    df_c = consultar(sql_clientes)
    df_v = consultar(sql_ventas)

    metricas = []

    mapeo = {
        "edad": (df_c["edad"], "Edad (Clientes)"),
        "venta_total": (df_c["venta_total"], "Venta Total Acumulada (Clientes)"),
        "n_compras": (df_c["n_compras"], "Numero de Compras (Clientes)"),
        "monto_compra": (df_v["monto_compra"], "Monto Compra por Transaccion"),
        "tiempo": (df_v["tiempo"], "Tiempo de Navegacion (Segundos)"),
    }

    if variable and variable.lower() in mapeo:
        items = [(variable.lower(), mapeo[variable.lower()])]
    else:
        items = list(mapeo.items())

    resumen_lineas = ["Estadisticas basicas de las variables numericas:"]

    for clave, (serie, etiqueta) in items:
        serie_limpia = serie.dropna().astype(float)
        media_val = float(serie_limpia.mean())
        mediana_val = float(serie_limpia.median())
        modas = serie_limpia.mode().tolist()
        moda_val = modas[0] if modas else None
        min_val = float(serie_limpia.min())
        max_val = float(serie_limpia.max())
        std_val = float(serie_limpia.std())

        registro = {
            "variable": clave,
            "etiqueta": etiqueta,
            "media": round(media_val, 4),
            "mediana": round(mediana_val, 4),
            "moda": round(moda_val, 4) if moda_val is not None else None,
            "minimo": round(min_val, 4),
            "maximo": round(max_val, 4),
            "desviacion_estandar": round(std_val, 4),
        }
        metricas.append(registro)
        resumen_lineas.append(
            f"- {etiqueta}: Media = {media_val:.2f}, Mediana = {mediana_val:.2f}, "
            f"Moda = {moda_val}, Min = {min_val:.2f}, Max = {max_val:.2f}, Desv = {std_val:.2f}"
        )

    # Grafico de distribucion
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    fig.suptitle("Distribucion de Variables Numericas Principales (EDA)", fontsize=14, fontweight="bold")

    axes[0, 0].hist(df_c["edad"].dropna(), bins=20, color="#2b5c8f", edgecolor="black", alpha=0.8)
    axes[0, 0].axvline(df_c["edad"].mean(), color="red", linestyle="--", label=f"Media: {df_c['edad'].mean():.1f}")
    axes[0, 0].axvline(df_c["edad"].median(), color="green", linestyle=":", label=f"Mediana: {df_c['edad'].median():.1f}")
    axes[0, 0].set_title("Distribucion de Edad")
    axes[0, 0].set_xlabel("Edad (Anios)")
    axes[0, 0].set_ylabel("Frecuencia")
    axes[0, 0].legend()

    axes[0, 1].hist(df_v["monto_compra"].dropna(), bins=25, color="#1e824c", edgecolor="black", alpha=0.8)
    axes[0, 1].axvline(df_v["monto_compra"].mean(), color="red", linestyle="--", label=f"Media: {df_v['monto_compra'].mean():.1f}")
    axes[0, 1].axvline(df_v["monto_compra"].median(), color="green", linestyle=":", label=f"Mediana: {df_v['monto_compra'].median():.1f}")
    axes[0, 1].set_title("Distribucion de Monto de Compra")
    axes[0, 1].set_xlabel("Monto Compra")
    axes[0, 1].set_ylabel("Frecuencia")
    axes[0, 1].legend()

    axes[1, 0].hist(df_c["venta_total"].dropna(), bins=25, color="#d35400", edgecolor="black", alpha=0.8)
    axes[1, 0].axvline(df_c["venta_total"].mean(), color="red", linestyle="--", label=f"Media: {df_c['venta_total'].mean():.1f}")
    axes[1, 0].axvline(df_c["venta_total"].median(), color="green", linestyle=":", label=f"Mediana: {df_c['venta_total'].median():.1f}")
    axes[1, 0].set_title("Distribucion de Venta Total Acumulada por Cliente")
    axes[1, 0].set_xlabel("Venta Total")
    axes[1, 0].set_ylabel("Frecuencia")
    axes[1, 0].legend()

    axes[1, 1].hist(df_c["n_compras"].dropna(), bins=20, color="#8e44ad", edgecolor="black", alpha=0.8)
    axes[1, 1].axvline(df_c["n_compras"].mean(), color="red", linestyle="--", label=f"Media: {df_c['n_compras'].mean():.1f}")
    axes[1, 1].axvline(df_c["n_compras"].median(), color="green", linestyle=":", label=f"Mediana: {df_c['n_compras'].median():.1f}")
    axes[1, 1].set_title("Distribucion de Numero de Compras")
    axes[1, 1].set_xlabel("N Compras")
    axes[1, 1].set_ylabel("Frecuencia")
    axes[1, 1].legend()

    plt.tight_layout()

    return Resultado(
        datos=metricas,
        resumen="\n".join(resumen_lineas),
        figura=fig,
    )


@analisis(
    nombre="eda_distribucion_metodo_pago",
    descripcion=(
        "Analiza como se distribuyen las ventas y transacciones segun el metodo de pago "
        "(Efectivo, Tarjeta de Credito, Tarjeta de Debito), calculando totales y porcentajes."
    ),
    punto="2.c",
)
def eda_distribucion_metodo_pago() -> Resultado:
    """Distribucion de ventas segun metodo de pago."""
    sql = """
        SELECT 
            COALESCE(mp.descripcion, 'Desconocido') AS metodo_pago,
            COUNT(v.id_registro) AS transacciones,
            ROUND(SUM(v.monto_compra), 2) AS total_facturado,
            ROUND(AVG(v.monto_compra), 2) AS ticket_promedio
        FROM ventas v
        LEFT JOIN cat_metodo_pago mp ON v.id_metodo_pago = mp.id_metodo_pago
        GROUP BY mp.descripcion
        ORDER BY total_facturado DESC;
    """
    df = consultar(sql)
    total_ventas = df["total_facturado"].sum()
    df["porcentaje_facturacion"] = (df["total_facturado"] / total_ventas * 100).round(2)

    resumen = (
        f"Distribucion por Metodo de Pago: "
        + ", ".join([f"{r['metodo_pago']}: {r['total_facturado']} ({r['porcentaje_facturacion']}%, {r['transacciones']} transacciones)" for _, r in df.iterrows()])
    )

    fig, ax1 = plt.subplots(figsize=(8, 5))
    barras = ax1.bar(df["metodo_pago"], df["total_facturado"], color=["#2980b9", "#27ae60", "#f39c12"], edgecolor="black")
    ax1.set_title("Facturacion Total por Metodo de Pago (2021)", fontsize=13, fontweight="bold")
    ax1.set_xlabel("Metodo de Pago")
    ax1.set_ylabel("Monto Total Facturado")
    for b in barras:
        altura = b.get_height()
        ax1.annotate(f"{altura:,.2f}", (b.get_x() + b.get_width() / 2, altura),
                     ha="center", va="bottom", xytext=(0, 3), textcoords="offset points")
    plt.tight_layout()

    return Resultado(
        datos=df.to_dict(orient="records"),
        resumen=resumen,
        figura=fig,
    )


@analisis(
    nombre="eda_distribucion_navegador",
    descripcion=(
        "Analiza el comportamiento de las ventas y sesiones segun el navegador utilizado "
        "o canal de compra (Tienda Fisica, Navegador 1, Navegador 2, Navegador 3, Navegador 4)."
    ),
    punto="2.c",
)
def eda_distribucion_navegador() -> Resultado:
    """Distribucion de ventas por canal o navegador."""
    sql = """
        SELECT 
            COALESCE(nav.descripcion, 'Desconocido') AS canal_navegador,
            COUNT(v.id_registro) AS transacciones,
            ROUND(SUM(v.monto_compra), 2) AS total_facturado,
            ROUND(AVG(v.monto_compra), 2) AS ticket_promedio,
            ROUND(AVG(v.tiempo), 2) AS tiempo_promedio_segundos
        FROM ventas v
        LEFT JOIN cat_navegador nav ON v.id_navegador = nav.id_navegador
        GROUP BY nav.descripcion
        ORDER BY total_facturado DESC;
    """
    df = consultar(sql)
    total_ventas = df["total_facturado"].sum()
    df["porcentaje_ventas"] = (df["total_facturado"] / total_ventas * 100).round(2)

    resumen = (
        f"Distribucion de ventas por canal/navegador: "
        + ", ".join([f"{r['canal_navegador']}: {r['total_facturado']} ({r['porcentaje_ventas']}%)" for _, r in df.iterrows()])
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    barras = ax.bar(df["canal_navegador"], df["total_facturado"], color="#34495e", edgecolor="black")
    ax.set_title("Ventas Totales por Canal / Navegador (2021)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Canal / Navegador")
    ax.set_ylabel("Monto Total Facturado")
    for b in barras:
        altura = b.get_height()
        ax.annotate(f"{altura:,.2f}", (b.get_x() + b.get_width() / 2, altura),
                    ha="center", va="bottom", xytext=(0, 3), textcoords="offset points")
    plt.tight_layout()

    return Resultado(
        datos=df.to_dict(orient="records"),
        resumen=resumen,
        figura=fig,
    )


@analisis(
    nombre="eda_distribucion_boletin_vale",
    descripcion=(
        "Analiza como se comportan las ventas segun el uso de boletines y vales promocionales, "
        "comparando usuarios suscritos/no suscritos y usuarios con/sin vale."
    ),
    punto="2.c",
)
def eda_distribucion_boletin_vale() -> Resultado:
    """Distribucion de ventas por boletin y vale."""
    sql_boletin = """
        SELECT 
            CASE WHEN boletin = 1 THEN 'Suscrito' ELSE 'No Suscrito' END AS estado_boletin,
            COUNT(id_registro) AS transacciones,
            ROUND(SUM(monto_compra), 2) AS total_facturado,
            ROUND(AVG(monto_compra), 2) AS ticket_promedio
        FROM ventas
        GROUP BY boletin;
    """
    sql_vale = """
        SELECT 
            CASE WHEN vale = 1 THEN 'Aplico Vale' ELSE 'Sin Vale' END AS estado_vale,
            COUNT(id_registro) AS transacciones,
            ROUND(SUM(monto_compra), 2) AS total_facturado,
            ROUND(AVG(monto_compra), 2) AS ticket_promedio
        FROM ventas
        GROUP BY vale;
    """
    df_bol = consultar(sql_boletin)
    df_val = consultar(sql_vale)

    datos = {
        "boletin": df_bol.to_dict(orient="records"),
        "vale": df_val.to_dict(orient="records"),
    }

    resumen = (
        f"Uso de Boletin: "
        + ", ".join([f"{r['estado_boletin']}: {r['total_facturado']} ({r['transacciones']} transacciones)" for _, r in df_bol.iterrows()])
        + " | Uso de Vales: "
        + ", ".join([f"{r['estado_vale']}: {r['total_facturado']} ({r['transacciones']} transacciones)" for _, r in df_val.iterrows()])
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    ax1.bar(df_bol["estado_boletin"], df_bol["total_facturado"], color=["#7f8c8d", "#2ecc71"], edgecolor="black")
    ax1.set_title("Ventas segun Suscripcion a Boletin", fontweight="bold")
    ax1.set_ylabel("Monto Facturado")

    ax2.bar(df_val["estado_vale"], df_val["total_facturado"], color=["#e74c3c", "#95a5a6"], edgecolor="black")
    ax2.set_title("Ventas segun Uso de Vales Promocionales", fontweight="bold")
    ax2.set_ylabel("Monto Facturado")

    plt.tight_layout()

    return Resultado(
        datos=datos,
        resumen=resumen,
        figura=fig,
    )


@analisis(
    nombre="tendencias_ventas_mensuales",
    descripcion=(
        "Identifica los meses con mayores y menores ventas del anio 2021, "
        "indicando el ranking mensual de facturacion y transacciones."
    ),
    punto="3.a",
)
def tendencias_ventas_mensuales() -> Resultado:
    """Meses con mayores y menores ventas."""
    sql = """
        SELECT 
            TO_CHAR(fecha_compra, 'YYYY-MM') AS mes,
            COUNT(id_registro) AS transacciones,
            ROUND(SUM(monto_compra), 2) AS total_facturado,
            ROUND(AVG(monto_compra), 2) AS ticket_promedio
        FROM ventas
        GROUP BY TO_CHAR(fecha_compra, 'YYYY-MM')
        ORDER BY mes ASC;
    """
    df = consultar(sql)
    df_ordenado = df.sort_values(by="total_facturado", ascending=False)
    mes_max = df_ordenado.iloc[0]
    mes_min = df_ordenado.iloc[-1]

    resumen = (
        f"El mes con MAYOR venta fue {mes_max['mes']} con {mes_max['total_facturado']} en facturacion "
        f"({mes_max['transacciones']} transacciones). "
        f"El mes con MENOR venta fue {mes_min['mes']} con {mes_min['total_facturado']} en facturacion "
        f"({mes_min['transacciones']} transacciones)."
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["mes"], df["total_facturado"], marker="o", color="#2c3e50", linewidth=2.5, label="Facturacion Mensual")
    ax.axhline(df["total_facturado"].mean(), color="gray", linestyle="--", label=f"Promedio: {df['total_facturado'].mean():,.2f}")
    
    # Resaltar maximo y minimo
    ax.scatter([mes_max["mes"]], [mes_max["total_facturado"]], color="green", s=120, zorder=5, label=f"Max: {mes_max['mes']}")
    ax.scatter([mes_min["mes"]], [mes_min["total_facturado"]], color="red", s=120, zorder=5, label=f"Min: {mes_min['mes']}")

    ax.set_title("Tendencia Mensual de Ventas (2021)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Monto Total Facturado")
    ax.set_xticks(range(len(df["mes"])))
    ax.set_xticklabels(df["mes"], rotation=45)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend()
    plt.tight_layout()

    return Resultado(
        datos=df_ordenado.to_dict(orient="records"),
        resumen=resumen,
        figura=fig,
    )


@analisis(
    nombre="tendencias_navegador_mas_menos_utilizado",
    descripcion=(
        "Identifica cual es el navegador de internet o canal mas preferido/utilizado "
        "y cual es el menos popular entre los clientes."
    ),
    punto="3.b",
)
def tendencias_navegador_mas_menos_utilizado() -> Resultado:
    """Navegador mas y menos utilizado."""
    sql = """
        SELECT 
            v.id_navegador,
            COALESCE(nav.descripcion, 'Desconocido') AS canal_navegador,
            COUNT(v.id_registro) AS total_sesiones,
            ROUND(SUM(v.monto_compra), 2) AS total_facturado
        FROM ventas v
        LEFT JOIN cat_navegador nav ON v.id_navegador = nav.id_navegador
        GROUP BY v.id_navegador, nav.descripcion
        ORDER BY total_sesiones DESC;
    """
    df = consultar(sql)
    canal_top = df.iloc[0]
    canal_bottom = df.iloc[-1]

    # Filtrar estrictamente navegadores web (id_navegador >= 1)
    df_web = df[df["id_navegador"] >= 1].sort_values(by="total_sesiones", ascending=False)
    web_top = df_web.iloc[0]
    web_bottom = df_web.iloc[-1]

    resumen = (
        f"A nivel general de canal, el mas utilizado es '{canal_top['canal_navegador']}' con {canal_top['total_sesiones']} sesiones "
        f"y el menos utilizado es '{canal_bottom['canal_navegador']}' con {canal_bottom['total_sesiones']} sesiones. "
        f"Entre los navegadores web especificos (excluyendo Tienda Fisica), el navegador mas utilizado es '{web_top['canal_navegador']}' "
        f"({web_top['total_sesiones']} sesiones) y el menos utilizado es '{web_bottom['canal_navegador']}' ({web_bottom['total_sesiones']} sesiones)."
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    colores = ["#27ae60" if x == web_top["canal_navegador"] else ("#e74c3c" if x == web_bottom["canal_navegador"] else "#3498db") for x in df["canal_navegador"]]
    barras = ax.bar(df["canal_navegador"], df["total_sesiones"], color=colores, edgecolor="black")
    ax.set_title("Popularidad y Uso por Canal / Navegador (2021)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Canal / Navegador")
    ax.set_ylabel("Numero de Sesiones / Transacciones")
    for b in barras:
        altura = b.get_height()
        ax.annotate(f"{int(altura)}", (b.get_x() + b.get_width() / 2, altura),
                    ha="center", va="bottom", xytext=(0, 3), textcoords="offset points")
    plt.tight_layout()

    return Resultado(
        datos=df.to_dict(orient="records"),
        resumen=resumen,
        figura=fig,
    )


@analisis(
    nombre="tendencias_ventas_efectivo",
    descripcion=(
        "Calcula el total de ventas que fueron pagadas en efectivo o pago contra entrega "
        "(MetodoPago = 0), indicando monto total, transacciones y porcentaje sobre el total."
    ),
    punto="3.c",
)
def tendencias_ventas_efectivo() -> Resultado:
    """Total de ventas pagadas contra entrega o en efectivo."""
    sql = """
        SELECT 
            COUNT(id_registro) AS total_transacciones_efectivo,
            ROUND(SUM(monto_compra), 2) AS monto_total_efectivo,
            ROUND(AVG(monto_compra), 2) AS ticket_promedio_efectivo,
            ROUND((COUNT(id_registro) * 100.0 / (SELECT COUNT(*) FROM ventas)), 2) AS pct_transacciones,
            ROUND((SUM(monto_compra) * 100.0 / (SELECT SUM(monto_compra) FROM ventas)), 2) AS pct_facturacion
        FROM ventas
        WHERE id_metodo_pago = 0;
    """
    df = consultar(sql)
    fila = df.iloc[0]

    resumen = (
        f"Ventas realizadas en efectivo o contra entrega (MetodoPago = 0): "
        f"Monto total = {fila['monto_total_efectivo']}, Transacciones = {int(fila['total_transacciones_efectivo'])}, "
        f"Ticket promedio = {fila['ticket_promedio_efectivo']}, Representa el {fila['pct_transacciones']}% del volumen "
        f"y el {fila['pct_facturacion']}% de la facturacion total."
    )

    return Resultado(
        datos=df.to_dict(orient="records"),
        resumen=resumen,
        figura=None,
    )


@analisis(
    nombre="tendencias_adopcion_boletines_vales",
    descripcion=(
        "Identifica los meses donde se registro la mayor adopcion y uso de boletines "
        "y vales promocionales durante el anio 2021."
    ),
    punto="3.d",
)
def tendencias_adopcion_boletines_vales() -> Resultado:
    """Meses con mayor adopcion de boletines y vales."""
    sql = """
        SELECT 
            TO_CHAR(fecha_compra, 'YYYY-MM') AS mes,
            COUNT(id_registro) AS total_transacciones,
            SUM(CASE WHEN boletin = 1 THEN 1 ELSE 0 END) AS adopcion_boletin,
            SUM(CASE WHEN vale = 1 THEN 1 ELSE 0 END) AS adopcion_vale
        FROM ventas
        GROUP BY TO_CHAR(fecha_compra, 'YYYY-MM')
        ORDER BY mes ASC;
    """
    df = consultar(sql)
    mes_top_bol = df.sort_values(by="adopcion_boletin", ascending=False).iloc[0]
    mes_top_val = df.sort_values(by="adopcion_vale", ascending=False).iloc[0]

    resumen = (
        f"El mes con mayor suscripcion a boletines fue {mes_top_bol['mes']} con {mes_top_bol['adopcion_boletin']} usuarios. "
        f"El mes con mayor uso de vales promocionales fue {mes_top_val['mes']} con {mes_top_val['adopcion_vale']} vales aplicados."
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(df["mes"]))
    ancho = 0.35

    ax.bar(x - ancho/2, df["adopcion_boletin"], ancho, label="Suscripcion Boletin", color="#27ae60")
    ax.bar(x + ancho/2, df["adopcion_vale"], ancho, label="Uso de Vales", color="#e67e22")

    ax.set_title("Adopcion Mensual de Boletines y Vales Promocionales (2021)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Cantidad de Usuarios / Transacciones")
    ax.set_xticks(x)
    ax.set_xticklabels(df["mes"], rotation=45)
    ax.legend()
    ax.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()

    return Resultado(
        datos=df.to_dict(orient="records"),
        resumen=resumen,
        figura=fig,
    )
