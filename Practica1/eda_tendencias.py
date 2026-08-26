"""
PRACTICA 1 - SISTEMAS ORGANIZACIONALES Y GERENCIALES 2 (2S2026)
ESTUDIANTE 3: ANALISTA EDA Y TENDENCIAS
-----------------------------------------------------------------------------
Script Integral de Analisis Exploratorio de Datos (EDA) y Analisis de Tendencias.
Cubre los Puntos 2 y 3 del alcance de la practica.

Funcionalidades:
1. Estadisticas basicas (Media, Mediana, Moda, Desviacion, Min, Max) para:
   - Venta_total (acumulada cliente)
   - MontoCompra (por transaccion)
   - N_Compras (por cliente)
   - Edad (clientes)
   - Tiempo (sesion de navegacion)
2. Distribucion de ventas por:
   - Metodo de Pago (Efectivo, Tarjeta de Credito, Tarjeta de Debito)
   - Canal / Navegador (Tienda Fisica, Navegador 1, 2, 3, 4)
   - Boletin Informativo (Suscrito vs No Suscrito)
   - Vales Promocionales (Aplico Vale vs Sin Vale)
3. Analisis de Tendencias:
   - Meses con mayores y menores ventas (monto y transacciones)
   - Navegadores web mas y menos utilizados
   - Total de ventas pagadas en efectivo / contra entrega (MetodoPago = 0)
   - Meses con mayor adopcion de boletines y vales promocionales
4. Exportacion de graficos profesionales a 'graficas_eda/'.
"""

import os
import pathlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Configuracion de rutas
BASE_DIR = pathlib.Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
OUTPUT_DIR = BASE_DIR / "graficas_eda"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(ENV_PATH)

# Estilo visual de graficos
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#333333"
plt.rcParams["axes.linewidth"] = 0.8


def obtener_conexion():
    """Obtiene motor de base de datos SQLAlchemy."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL no encontrada en el archivo .env")
    return create_engine(db_url)


def cargar_datos():
    """Carga dataframes desde la base de datos PostgreSQL en AWS RDS."""
    engine = obtener_conexion()
    print("Conectando a AWS RDS PostgreSQL y extrayendo datasets...")

    sql_clientes = """
        SELECT 
            c.id_cliente, 
            c.edad, 
            c.id_genero,
            g.descripcion AS genero,
            c.venta_total, 
            c.n_compras
        FROM clientes c
        LEFT JOIN cat_genero g ON c.id_genero = g.id_genero;
    """

    sql_ventas = """
        SELECT 
            v.id_registro,
            v.id_cliente,
            v.fecha_compra,
            v.monto_compra,
            v.id_metodo_pago,
            mp.descripcion AS metodo_pago,
            v.id_navegador,
            nav.descripcion AS canal_navegador,
            v.tiempo,
            v.boletin,
            v.vale
        FROM ventas v
        LEFT JOIN cat_metodo_pago mp ON v.id_metodo_pago = mp.id_metodo_pago
        LEFT JOIN cat_navegador nav ON v.id_navegador = nav.id_navegador;
    """

    df_clientes = pd.read_sql(sql_clientes, engine)
    df_ventas = pd.read_sql(sql_ventas, engine)
    df_ventas["fecha_compra"] = pd.to_datetime(df_ventas["fecha_compra"])
    df_ventas["mes"] = df_ventas["fecha_compra"].dt.strftime("%Y-%m")
    df_ventas["mes_num"] = df_ventas["fecha_compra"].dt.month

    print(f"Datos cargados exitosamente: {len(df_clientes)} clientes, {len(df_ventas)} transacciones de venta.\n")
    return df_clientes, df_ventas


# =============================================================================
# 1. ESTADISTICAS BASICAS (Punto 2.b)
# =============================================================================

def calcular_estadisticas_basicas(df_clientes, df_ventas):
    """Calcula media, mediana, moda y dispersion de variables numericas."""
    print("=" * 80)
    print("1. ESTADISTICAS BASICAS (PUNTO 2.b)")
    print("=" * 80)

    variables = [
        ("Venta_total (Cliente)", df_clientes["venta_total"]),
        ("MontoCompra (Transaccion)", df_ventas["monto_compra"]),
        ("N_Compras (Cliente)", df_clientes["n_compras"]),
        ("Edad (Cliente)", df_clientes["edad"]),
        ("Tiempo Sesion Segundos (Transaccion)", df_ventas["tiempo"]),
    ]

    resumen = []
    for nombre, serie in variables:
        s = serie.dropna().astype(float)
        media = s.mean()
        mediana = s.median()
        modas = s.mode().tolist()
        moda_str = ", ".join(f"{m:.2f}" if isinstance(m, float) else str(m) for m in modas[:3])
        desv = s.std()
        var = s.var()
        val_min = s.min()
        val_max = s.max()
        q25 = s.quantile(0.25)
        q75 = s.quantile(0.75)
        iqr = q75 - q25

        resumen.append({
            "Variable": nombre,
            "Media": round(media, 4),
            "Mediana": round(mediana, 4),
            "Moda": moda_str,
            "Desv_Std": round(desv, 4),
            "Min": round(val_min, 4),
            "Max": round(val_max, 4),
            "IQR": round(iqr, 4),
        })

    df_stats = pd.DataFrame(resumen)
    print(df_stats.to_string(index=False))
    print("-" * 80)

    # Grafico 1: Histogramas con Media y Mediana
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle("Distribucion de Variables Numericas Principales (Analisis EDA)", fontsize=14, fontweight="bold")

    # Edad
    sns.histplot(df_clientes["edad"], bins=20, kde=True, ax=axes[0, 0], color="#2980b9")
    axes[0, 0].axvline(df_clientes["edad"].mean(), color="red", linestyle="--", label=f"Media: {df_clientes['edad'].mean():.2f}")
    axes[0, 0].axvline(df_clientes["edad"].median(), color="green", linestyle=":", label=f"Mediana: {df_clientes['edad'].median():.2f}")
    axes[0, 0].set_title("Distribucion de Edad de Clientes")
    axes[0, 0].set_xlabel("Edad (Anios)")
    axes[0, 0].set_ylabel("Frecuencia")
    axes[0, 0].legend()

    # Monto Compra
    sns.histplot(df_ventas["monto_compra"], bins=30, kde=True, ax=axes[0, 1], color="#27ae60")
    axes[0, 1].axvline(df_ventas["monto_compra"].mean(), color="red", linestyle="--", label=f"Media: {df_ventas['monto_compra'].mean():.2f}")
    axes[0, 1].axvline(df_ventas["monto_compra"].median(), color="green", linestyle=":", label=f"Mediana: {df_ventas['monto_compra'].median():.2f}")
    axes[0, 1].set_title("Distribucion de Monto de Compra por Transaccion")
    axes[0, 1].set_xlabel("Monto Compra")
    axes[0, 1].set_ylabel("Frecuencia")
    axes[0, 1].legend()

    # Venta Total
    sns.histplot(df_clientes["venta_total"], bins=30, kde=True, ax=axes[1, 0], color="#d35400")
    axes[1, 0].axvline(df_clientes["venta_total"].mean(), color="red", linestyle="--", label=f"Media: {df_clientes['venta_total'].mean():.2f}")
    axes[1, 0].axvline(df_clientes["venta_total"].median(), color="green", linestyle=":", label=f"Mediana: {df_clientes['venta_total'].median():.2f}")
    axes[1, 0].set_title("Distribucion de Venta Total Acumulada por Cliente")
    axes[1, 0].set_xlabel("Venta Total")
    axes[1, 0].set_ylabel("Frecuencia")
    axes[1, 0].legend()

    # N_Compras
    sns.histplot(df_clientes["n_compras"], bins=20, kde=False, ax=axes[1, 1], color="#8e44ad")
    axes[1, 1].axvline(df_clientes["n_compras"].mean(), color="red", linestyle="--", label=f"Media: {df_clientes['n_compras'].mean():.2f}")
    axes[1, 1].axvline(df_clientes["n_compras"].median(), color="green", linestyle=":", label=f"Mediana: {df_clientes['n_compras'].median():.2f}")
    axes[1, 1].set_title("Distribucion de Frecuencia de Compras (N_Compras)")
    axes[1, 1].set_xlabel("N Compras")
    axes[1, 1].set_ylabel("Frecuencia")
    axes[1, 1].legend()

    plt.tight_layout()
    ruta_graf1 = OUTPUT_DIR / "01_distribucion_estadisticas_numericas.png"
    plt.savefig(ruta_graf1, dpi=200)
    plt.close()
    print(f"Grafico guardado: {ruta_graf1.name}")

    return df_stats


# =============================================================================
# 2. DISTRIBUCION DE VENTAS (Punto 2.c)
# =============================================================================

def analizar_distribucion_ventas(df_ventas):
    """Analiza distribucion por metodo de pago, navegador, boletin y vales."""
    print("\n" + "=" * 80)
    print("2. DISTRIBUCION DE VENTAS (PUNTO 2.c)")
    print("=" * 80)

    # 2.1 Metodo de Pago
    print("\n--- 2.1 Distribucion por Metodo de Pago ---")
    pago_df = df_ventas.groupby("metodo_pago").agg(
        transacciones=("id_registro", "count"),
        facturacion_total=("monto_compra", "sum"),
        ticket_promedio=("monto_compra", "mean"),
    ).reset_index()
    total_fac = pago_df["facturacion_total"].sum()
    pago_df["pct_facturacion"] = (pago_df["facturacion_total"] / total_fac * 100).round(2)
    pago_df["pct_transacciones"] = (pago_df["transacciones"] / len(df_ventas) * 100).round(2)
    pago_df = pago_df.sort_values(by="facturacion_total", ascending=False)
    print(pago_df.to_string(index=False))

    # Grafico Metodo de Pago
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    colores_pago = ["#2980b9", "#27ae60", "#f39c12"]

    barras = ax1.bar(pago_df["metodo_pago"], pago_df["facturacion_total"], color=colores_pago, edgecolor="black")
    ax1.set_title("Facturacion Total por Metodo de Pago (2021)", fontweight="bold")
    ax1.set_ylabel("Monto Total Facturado")
    for b in barras:
        ax1.annotate(f"{b.get_height():,.2f}", (b.get_x() + b.get_width() / 2, b.get_height()),
                     ha="center", va="bottom", xytext=(0, 3), textcoords="offset points")

    ax2.pie(pago_df["facturacion_total"], labels=pago_df["metodo_pago"], autopct="%1.1f%%",
            colors=colores_pago, startangle=140, explode=(0.05, 0, 0), shadow=True)
    ax2.set_title("Participacion de Mercado por Metodo de Pago", fontweight="bold")

    plt.tight_layout()
    ruta_graf2 = OUTPUT_DIR / "02_distribucion_metodo_pago.png"
    plt.savefig(ruta_graf2, dpi=200)
    plt.close()
    print(f"Grafico guardado: {ruta_graf2.name}")

    # 2.2 Canal / Navegador
    print("\n--- 2.2 Distribucion por Canal y Navegador ---")
    nav_df = df_ventas.groupby("canal_navegador").agg(
        transacciones=("id_registro", "count"),
        facturacion_total=("monto_compra", "sum"),
        ticket_promedio=("monto_compra", "mean"),
        tiempo_promedio_seg=("tiempo", "mean"),
    ).reset_index().sort_values(by="facturacion_total", ascending=False)
    nav_df["pct_facturacion"] = (nav_df["facturacion_total"] / total_fac * 100).round(2)
    nav_df["pct_transacciones"] = (nav_df["transacciones"] / len(df_ventas) * 100).round(2)
    print(nav_df.to_string(index=False))

    # Grafico Canal / Navegador
    fig, ax = plt.subplots(figsize=(10, 5))
    barras_nav = ax.bar(nav_df["canal_navegador"], nav_df["facturacion_total"], color="#34495e", edgecolor="black")
    ax.set_title("Ventas Totales por Canal de Acceso / Navegador (2021)", fontweight="bold")
    ax.set_xlabel("Canal / Navegador")
    ax.set_ylabel("Monto Total Facturado")
    for b in barras_nav:
        ax.annotate(f"{b.get_height():,.2f}\n({b.get_height()/total_fac*100:.1f}%)",
                    (b.get_x() + b.get_width() / 2, b.get_height()),
                    ha="center", va="bottom", xytext=(0, 3), textcoords="offset points")
    plt.tight_layout()
    ruta_graf3 = OUTPUT_DIR / "03_distribucion_canales_navegadores.png"
    plt.savefig(ruta_graf3, dpi=200)
    plt.close()
    print(f"Grafico guardado: {ruta_graf3.name}")

    # 2.3 Boletin y Vales
    print("\n--- 2.3 Distribucion por Boletin y Vales ---")
    bol_df = df_ventas.groupby("boletin").agg(
        transacciones=("id_registro", "count"),
        facturacion_total=("monto_compra", "sum"),
        ticket_promedio=("monto_compra", "mean")
    ).reset_index()
    bol_df["estado"] = bol_df["boletin"].map({1: "Suscrito", 0: "No Suscrito"})

    val_df = df_ventas.groupby("vale").agg(
        transacciones=("id_registro", "count"),
        facturacion_total=("monto_compra", "sum"),
        ticket_promedio=("monto_compra", "mean")
    ).reset_index()
    val_df["estado"] = val_df["vale"].map({1: "Aplico Vale", 0: "Sin Vale"})

    print("Boletin:")
    print(bol_df[["estado", "transacciones", "facturacion_total", "ticket_promedio"]].to_string(index=False))
    print("\nVales:")
    print(val_df[["estado", "transacciones", "facturacion_total", "ticket_promedio"]].to_string(index=False))

    # Grafico Boletin y Vales
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.bar(bol_df["estado"], bol_df["facturacion_total"], color=["#7f8c8d", "#2ecc71"], edgecolor="black")
    ax1.set_title("Ventas segun Suscripcion a Boletin", fontweight="bold")
    ax1.set_ylabel("Monto Total Facturado")
    for b in ax1.patches:
        ax1.annotate(f"{b.get_height():,.2f}", (b.get_x() + b.get_width() / 2, b.get_height()),
                     ha="center", va="bottom", xytext=(0, 3), textcoords="offset points")

    ax2.bar(val_df["estado"], val_df["facturacion_total"], color=["#95a5a6", "#e74c3c"], edgecolor="black")
    ax2.set_title("Ventas segun Aplicacion de Vales", fontweight="bold")
    ax2.set_ylabel("Monto Total Facturado")
    for b in ax2.patches:
        ax2.annotate(f"{b.get_height():,.2f}", (b.get_x() + b.get_width() / 2, b.get_height()),
                     ha="center", va="bottom", xytext=(0, 3), textcoords="offset points")

    plt.tight_layout()
    ruta_graf4 = OUTPUT_DIR / "04_distribucion_boletin_vales.png"
    plt.savefig(ruta_graf4, dpi=200)
    plt.close()
    print(f"Grafico guardado: {ruta_graf4.name}")


# =============================================================================
# 3. IDENTIFICACION DE TENDENCIAS (Punto 3)
# =============================================================================

def analizar_tendencias(df_ventas):
    """Analiza estacionalidad, popularidad de navegadores, pagos en efectivo y adopcion mensual."""
    print("\n" + "=" * 80)
    print("3. IDENTIFICACION DE TENDENCIAS (PUNTO 3)")
    print("=" * 80)

    # 3.a Meses con mayores y menores ventas
    print("\n--- 3.a Tendencias Mensuales (Mayores y Menores Ventas) ---")
    mensual = df_ventas.groupby("mes").agg(
        transacciones=("id_registro", "count"),
        total_facturado=("monto_compra", "sum"),
        ticket_promedio=("monto_compra", "mean"),
        boletines=("boletin", "sum"),
        vales=("vale", "sum")
    ).reset_index().sort_values(by="total_facturado", ascending=False)

    mensual["ranking_monto"] = range(1, len(mensual) + 1)
    print(mensual[["ranking_monto", "mes", "total_facturado", "transacciones", "ticket_promedio"]].to_string(index=False))

    mes_max = mensual.iloc[0]
    mes_min = mensual.iloc[-1]
    print(f"\nMes con MAYOR venta: {mes_max['mes']} -> Facturacion: {mes_max['total_facturado']:,.2f} ({mes_max['transacciones']} transacciones)")
    print(f"Mes con MENOR venta: {mes_min['mes']} -> Facturacion: {mes_min['total_facturado']:,.2f} ({mes_min['transacciones']} transacciones)")

    # Grafico 5: Tendencia mensual de ventas
    mensual_cron = mensual.sort_values("mes")
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(mensual_cron["mes"], mensual_cron["total_facturado"], marker="o", linewidth=2.5, color="#1a5276", label="Facturacion Mensual")
    promedio_mensual = mensual_cron["total_facturado"].mean()
    ax.axhline(promedio_mensual, color="red", linestyle="--", alpha=0.7, label=f"Media Mensual: {promedio_mensual:,.2f}")

    # Resaltar puntos max y min
    ax.scatter([mes_max["mes"]], [mes_max["total_facturado"]], color="#27ae60", s=140, zorder=5, label=f"Pico Maximo: {mes_max['mes']}")
    ax.scatter([mes_min["mes"]], [mes_min["total_facturado"]], color="#c0392b", s=140, zorder=5, label=f"Punto Minimo: {mes_min['mes']}")

    ax.set_title("Evolucion de Ventas Mensuales a lo Largo de 2021", fontsize=13, fontweight="bold")
    ax.set_xlabel("Mes (2021)")
    ax.set_ylabel("Monto Total Facturado")
    ax.set_xticks(range(len(mensual_cron["mes"])))
    ax.set_xticklabels(mensual_cron["mes"], rotation=45)
    ax.legend(loc="lower left")
    plt.tight_layout()
    ruta_graf5 = OUTPUT_DIR / "05_tendencia_ventas_mensuales_2021.png"
    plt.savefig(ruta_graf5, dpi=200)
    plt.close()
    print(f"Grafico guardado: {ruta_graf5.name}")

    # 3.b Navegador de internet mas y menos utilizado
    print("\n--- 3.b Navegadores Web Mas y Menos Utilizados ---")
    web_df = df_ventas[df_ventas["id_navegador"] >= 1].groupby("canal_navegador").agg(
        sesiones=("id_registro", "count"),
        facturacion=("monto_compra", "sum"),
        ticket_promedio=("monto_compra", "mean"),
    ).reset_index().sort_values(by="sesiones", ascending=False)
    total_web_ses = web_df["sesiones"].sum()
    web_df["pct_web"] = (web_df["sesiones"] / total_web_ses * 100).round(2)
    print(web_df.to_string(index=False))

    nav_mas = web_df.iloc[0]
    nav_menos = web_df.iloc[-1]
    print(f"\nNavegador de internet MAS utilizado: {nav_mas['canal_navegador']} con {nav_mas['sesiones']} sesiones ({nav_mas['pct_web']}% del trafico web).")
    print(f"Navegador de internet MENOS utilizado: {nav_menos['canal_navegador']} con {nav_menos['sesiones']} sesiones ({nav_menos['pct_web']}% del trafico web).")

    # Grafico 6: Ranking Navegadores Web
    fig, ax = plt.subplots(figsize=(9, 5))
    colores_web = ["#27ae60", "#2980b9", "#f39c12", "#c0392b"]
    barras_web = ax.bar(web_df["canal_navegador"], web_df["sesiones"], color=colores_web, edgecolor="black")
    ax.set_title("Preferencia de Uso de Navegadores Web en 2021", fontweight="bold")
    ax.set_xlabel("Navegador Web")
    ax.set_ylabel("Numero de Sesiones / Compras")
    for b in barras_web:
        ax.annotate(f"{int(b.get_height())}\n({b.get_height()/total_web_ses*100:.1f}%)",
                    (b.get_x() + b.get_width() / 2, b.get_height()),
                    ha="center", va="bottom", xytext=(0, 3), textcoords="offset points")
    plt.tight_layout()
    ruta_graf6 = OUTPUT_DIR / "06_ranking_navegadores_preferencia.png"
    plt.savefig(ruta_graf6, dpi=200)
    plt.close()
    print(f"Grafico guardado: {ruta_graf6.name}")

    # 3.c Total de ventas en efectivo o contra entrega (MetodoPago = 0)
    print("\n--- 3.c Ventas en Efectivo o Contra Entrega (MetodoPago = 0) ---")
    efectivo_df = df_ventas[df_ventas["id_metodo_pago"] == 0]
    monto_efectivo = efectivo_df["monto_compra"].sum()
    trans_efectivo = len(efectivo_df)
    monto_total_global = df_ventas["monto_compra"].sum()
    trans_total_global = len(df_ventas)

    pct_monto_efectivo = (monto_efectivo / monto_total_global) * 100
    pct_trans_efectivo = (trans_efectivo / trans_total_global) * 100

    print(f"Total de Transacciones en Efectivo / Contra Entrega: {trans_efectivo} ({pct_trans_efectivo:.2f}% de transacciones totales)")
    print(f"Monto Total Facturado en Efectivo: {monto_efectivo:,.2f} ({pct_monto_efectivo:.2f}% de la facturacion total)")
    print(f"Ticket Promedio en Efectivo: {efectivo_df['monto_compra'].mean():.2f}")

    # 3.d Meses con mayor adopcion de boletines y vales
    print("\n--- 3.d Adopcion Mensual de Boletines y Vales Promocionales ---")
    adopcion_mensual = df_ventas.groupby("mes").agg(
        total_ventas=("id_registro", "count"),
        usuarios_boletin=("boletin", "sum"),
        usuarios_vale=("vale", "sum"),
    ).reset_index().sort_values("mes")

    adopcion_mensual["pct_boletin"] = (adopcion_mensual["usuarios_boletin"] / adopcion_mensual["total_ventas"] * 100).round(2)
    adopcion_mensual["pct_vale"] = (adopcion_mensual["usuarios_vale"] / adopcion_mensual["total_ventas"] * 100).round(2)
    print(adopcion_mensual.to_string(index=False))

    top_bol = adopcion_mensual.sort_values(by="usuarios_boletin", ascending=False).iloc[0]
    top_val = adopcion_mensual.sort_values(by="usuarios_vale", ascending=False).iloc[0]

    print(f"\nMes con MAYOR adopcion de Boletin Informativo: {top_bol['mes']} con {top_bol['usuarios_boletin']} suscriptores ({top_bol['pct_boletin']}% de compras del mes).")
    print(f"Mes con MAYOR adopcion de Vales Promocionales: {top_val['mes']} con {top_val['usuarios_vale']} vales aplicados ({top_val['pct_vale']}% de compras del mes).")

    # Grafico 7: Adopcion mensual de boletines y vales
    fig, ax = plt.subplots(figsize=(11, 5))
    x = np.arange(len(adopcion_mensual["mes"]))
    width = 0.35

    b1 = ax.bar(x - width/2, adopcion_mensual["usuarios_boletin"], width, label="Suscripcion a Boletin", color="#27ae60", edgecolor="black")
    b2 = ax.bar(x + width/2, adopcion_mensual["usuarios_vale"], width, label="Uso de Vales Promocionales", color="#e67e22", edgecolor="black")

    ax.set_title("Adopcion de Campanias Mensuales: Boletines vs Vales (2021)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Mes (2021)")
    ax.set_ylabel("Cantidad de Transacciones / Clientes")
    ax.set_xticks(x)
    ax.set_xticklabels(adopcion_mensual["mes"], rotation=45)
    ax.legend()
    plt.tight_layout()
    ruta_graf7 = OUTPUT_DIR / "07_adopcion_mensual_boletin_vales.png"
    plt.savefig(ruta_graf7, dpi=200)
    plt.close()
    print(f"Grafico guardado: {ruta_graf7.name}")


def main():
    print("=" * 80)
    print("EJECUTANDO PIPELINE EDA Y TENDENCIAS - ESTUDIANTE 3")
    print("=" * 80)
    df_clientes, df_ventas = cargar_datos()
    calcular_estadisticas_basicas(df_clientes, df_ventas)
    analizar_distribucion_ventas(df_ventas)
    analizar_tendencias(df_ventas)
    print("\n" + "=" * 80)
    print("ANALISIS COMPLETADO EXITOSAMENTE. TODAS LAS GRAFICAS HAN SIDO GENERADAS.")
    print("=" * 80)


if __name__ == "__main__":
    main()
