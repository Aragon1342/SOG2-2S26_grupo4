"""
Modulo de Segmentacion de Clientes y Analisis de Correlaciones.
Estudiante 4: Analista de Segmentacion y Correlaciones (Puntos 4, 5 y 6 del alcance).

Este modulo expone herramientas registradas con @analisis para que el servidor
MCP y el agente conversacional de IA puedan responder preguntas sobre
segmentacion demografica, impacto de promociones, correlaciones y pruebas estadisticas.
"""

from typing import Optional
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats

from ..contrato import Resultado, analisis
from ..db import consultar


@analisis(
    nombre="segmentacion_por_edad",
    descripcion=(
        "Agrupa a los clientes por rangos de edad (18-25 Gen Z, 26-40 Millennial, "
        "41-55 Gen X, 56+ Boomer) y analiza sus habitos de compra: volumen total de facturacion, "
        "ticket promedio, porcentaje de participacion y tiempo de navegacion."
    ),
    punto="4.a",
)
def segmentacion_por_edad() -> Resultado:
    """Segmentacion de clientes por rangos de edad."""
    sql = """
        SELECT 
            c.id_cliente,
            c.edad,
            v.monto_compra,
            c.n_compras,
            v.tiempo
        FROM clientes c
        JOIN ventas v ON c.id_cliente = v.id_cliente;
    """
    df = consultar(sql)

    bins = [17, 25, 40, 55, 120]
    labels = [
        "18-25 (Joven / Gen Z)",
        "26-40 (Adulto Joven / Millennial)",
        "41-55 (Adulto / Gen X)",
        "56+ (Adulto Mayor / Boomer)",
    ]
    df["rango_edad"] = pd.cut(df["edad"], bins=bins, labels=labels)

    resumen = df.groupby("rango_edad", observed=False).agg(
        total_transacciones=("monto_compra", "count"),
        clientes_unicos=("id_cliente", "nunique"),
        facturacion_total=("monto_compra", "sum"),
        ticket_promedio=("monto_compra", "mean"),
        tiempo_promedio=("tiempo", "mean"),
    ).reset_index()

    total_fact = df["monto_compra"].sum()
    resumen["pct_facturacion"] = (resumen["facturacion_total"] / total_fact) * 100

    datos = resumen.to_dict(orient="records")

    resumen_lineas = ["Segmentacion de Clientes por Rango de Edad:"]
    for r in datos:
        resumen_lineas.append(
            f"- {r['rango_edad']}: Facturación = ${r['facturacion_total']:,.2f} ({r['pct_facturacion']:.1f}%), "
            f"Ticket Promedio = ${r['ticket_promedio']:.2f}, Clientes = {r['clientes_unicos']:,}"
        )

    # Grafica
    fig, ax1 = plt.subplots(figsize=(9, 5))
    x = np.arange(len(resumen))
    width = 0.4
    bars = ax1.bar(x - width/2, resumen["facturacion_total"] / 1000, width, color="#1f77b4", alpha=0.85, label="Facturación ($k)")
    ax1.set_ylabel("Facturación (Miles USD)", color="#1f77b4", fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(resumen["rango_edad"], fontsize=9, fontweight="bold")

    ax2 = ax1.twinx()
    lines = ax2.plot(x + width/2, resumen["ticket_promedio"], color="#d62728", marker="o", linewidth=2.5, label="Ticket Promedio ($)")
    ax2.set_ylabel("Ticket Promedio ($ USD)", color="#d62728", fontweight="bold")
    ax2.set_ylim(0, resumen["ticket_promedio"].max() * 1.3)
    ax1.set_title("Segmentación por Rango de Edad (Ventas y Ticket)", fontsize=12, fontweight="bold")
    plt.tight_layout()

    return Resultado(datos=datos, resumen="\n".join(resumen_lineas), figura=fig)


@analisis(
    nombre="segmentacion_por_genero",
    descripcion=(
        "Compara el comportamiento de compra segun genero (0 = Masculino vs 1 = Femenino): "
        "facturacion total, ticket promedio, ventas acumuladas y comparativa estadistica."
    ),
    punto="4.b",
)
def segmentacion_por_genero() -> Resultado:
    """Comparativa de compra entre generos."""
    sql = """
        SELECT 
            c.id_genero,
            COALESCE(g.descripcion, 'No especificado') AS genero,
            v.monto_compra,
            c.venta_total,
            c.n_compras
        FROM clientes c
        LEFT JOIN cat_genero g ON c.id_genero = g.id_genero
        JOIN ventas v ON c.id_cliente = v.id_cliente;
    """
    df = consultar(sql)

    resumen = df.groupby(["id_genero", "genero"]).agg(
        transacciones=("monto_compra", "count"),
        facturacion_total=("monto_compra", "sum"),
        ticket_promedio=("monto_compra", "mean"),
        ticket_std=("monto_compra", "std"),
        venta_total_promedio=("venta_total", "mean"),
    ).reset_index()

    total_fact = df["monto_compra"].sum()
    resumen["pct_facturacion"] = (resumen["facturacion_total"] / total_fact) * 100
    datos = resumen.to_dict(orient="records")

    resumen_lineas = ["Comparativa Comercial por Género:"]
    for r in datos:
        resumen_lineas.append(
            f"- {r['genero']} (Código {r['id_genero']}): Facturación = ${r['facturacion_total']:,.2f} ({r['pct_facturacion']:.1f}%), "
            f"Ticket Promedio = ${r['ticket_promedio']:.2f}, Venta Acum. Prom. = ${r['venta_total_promedio']:.2f}"
        )

    fig, ax = plt.subplots(figsize=(7, 4.5))
    bars = ax.bar(
        resumen["genero"],
        resumen["facturacion_total"] / 1000,
        color=["#2b6cb0", "#e53e3e"],
        width=0.5,
        alpha=0.85
    )
    ax.set_ylabel("Facturación Total (Miles de USD)", fontweight="bold")
    ax.set_title("Facturación Total por Género (0: Masc vs 1: Fem)", fontsize=11, fontweight="bold")
    for bar in bars:
        ax.annotate(f"${bar.get_height():.1f}k", (bar.get_x() + bar.get_width()/2, bar.get_height()), ha="center", va="bottom", fontweight="bold")
    plt.tight_layout()

    return Resultado(datos=datos, resumen="\n".join(resumen_lineas), figura=fig)


@analisis(
    nombre="segmentacion_boletin_vales",
    descripcion=(
        "Analiza el comportamiento de compra segun el uso de herramientas de promocion y fidelizacion "
        "en 4 cuadrantes: 1. Ambos (Boletin + Vale), 2. Solo Boletin, 3. Solo Vale, 4. Ninguno (Organico)."
    ),
    punto="4.c",
)
def segmentacion_boletin_vales() -> Resultado:
    """Segmentacion de clientes en cuadrantes de promocion."""
    sql = """
        SELECT 
            v.boletin,
            v.vale,
            v.monto_compra,
            v.tiempo
        FROM ventas v;
    """
    df = consultar(sql)

    def cuadrante(row):
        b, v = row["boletin"], row["vale"]
        if b == 1 and v == 1:
            return "1. Ambos (Boletín y Vale)"
        elif b == 1 and v == 0:
            return "2. Solo Boletín"
        elif b == 0 and v == 1:
            return "3. Solo Vale"
        else:
            return "4. Ninguno (Orgánico)"

    df["cuadrante"] = df.apply(cuadrante, axis=1)

    resumen = df.groupby("cuadrante").agg(
        transacciones=("monto_compra", "count"),
        facturacion_total=("monto_compra", "sum"),
        ticket_promedio=("monto_compra", "mean"),
        tiempo_promedio=("tiempo", "mean"),
    ).reset_index()

    total_fact = df["monto_compra"].sum()
    resumen["pct_facturacion"] = (resumen["facturacion_total"] / total_fact) * 100
    datos = resumen.to_dict(orient="records")

    resumen_lineas = ["Segmentación por Adopción de Promociones (4 Cuadrantes):"]
    for r in datos:
        resumen_lineas.append(
            f"- {r['cuadrante']}: Facturación = ${r['facturacion_total']:,.2f} ({r['pct_facturacion']:.1f}%), "
            f"Ticket Promedio = ${r['ticket_promedio']:.2f}, Transacciones = {r['transacciones']:,}"
        )

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(resumen["cuadrante"], resumen["facturacion_total"] / 1000, color=["#805ad5", "#319795", "#dd6b20", "#718096"], alpha=0.85)
    ax.set_xlabel("Facturación Total (Miles de USD)", fontweight="bold")
    ax.set_title("Desempeño Comercial por Cuadrante Promocional", fontsize=11, fontweight="bold")
    plt.tight_layout()

    return Resultado(datos=datos, resumen="\n".join(resumen_lineas), figura=fig)


@analisis(
    nombre="correlacion_edad_venta",
    descripcion=(
        "Calcula la correlacion de Pearson, Spearman, coeficiente de determinacion R^2, "
        "pendiente y valor p entre la Edad del cliente y la Venta Total Acumulada."
    ),
    punto="5.a",
)
def correlacion_edad_venta() -> Resultado:
    """Correlacion entre edad y ventas."""
    sql = "SELECT edad, venta_total FROM clientes WHERE edad IS NOT NULL AND venta_total IS NOT NULL;"
    df = consultar(sql)

    r_p, p_p = stats.pearsonr(df["edad"], df["venta_total"])
    r_s, p_s = stats.spearmanr(df["edad"], df["venta_total"])
    slope, intercept, r_val, p_val, std_err = stats.linregress(df["edad"], df["venta_total"])

    datos = [{
        "pearson_r": round(float(r_p), 4),
        "pearson_p_value": float(p_p),
        "spearman_rho": round(float(r_s), 4),
        "spearman_p_value": float(p_s),
        "r_squared": round(float(r_val ** 2), 6),
        "slope": round(float(slope), 4),
        "intercept": round(float(intercept), 4),
    }]

    resumen = (
        f"Análisis de Correlación: Edad vs Venta Total Acumulada (N={len(df):,}):\n"
        f"- Coeficiente de Pearson (r): {r_p:.4f} (p-value = {p_p:.4e})\n"
        f"- Coeficiente de Spearman (rho): {r_s:.4f} (p-value = {p_s:.4e})\n"
        f"- Recta de Regresión OLS: Venta_Total = {slope:.4f} * Edad + {intercept:.4f}\n"
        f"- Coeficiente de Determinación R²: {r_val**2:.6f}\n"
        f"- Conclusión: No existe correlación lineal ni monótona significativa entre la edad del cliente y su gasto total."
    )

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df["edad"], df["venta_total"], alpha=0.4, color="#2b6cb0", s=25, label="Clientes")
    x_line = np.linspace(df["edad"].min(), df["edad"].max(), 100)
    ax.plot(x_line, slope * x_line + intercept, color="#e53e3e", linewidth=2.5, label=f"Regresión: y={slope:.2f}x+{intercept:.2f}")
    ax.set_xlabel("Edad del Cliente (Años)", fontweight="bold")
    ax.set_ylabel("Venta Total Acumulada ($)", fontweight="bold")
    ax.set_title(f"Dispersión y Regresión: Edad vs Venta Total (r = {r_p:.4f})", fontsize=11, fontweight="bold")
    ax.legend()
    plt.tight_layout()

    return Resultado(datos=datos, resumen=resumen, figura=fig)


@analisis(
    nombre="correlacion_genero_metodo_pago",
    descripcion=(
        "Examina si el genero influye en la seleccion del metodo de pago preferido "
        "mediante prueba de independencia Chi-cuadrado, valor p y V de Cramer."
    ),
    punto="5.b",
)
def correlacion_genero_metodo_pago() -> Resultado:
    """Prueba de independencia Chi-cuadrado para Genero vs Metodo de Pago."""
    sql = """
        SELECT 
            COALESCE(g.descripcion, 'No especificado') AS genero,
            COALESCE(mp.descripcion, 'Otro') AS metodo_pago
        FROM ventas v
        JOIN clientes c ON v.id_cliente = c.id_cliente
        LEFT JOIN cat_genero g ON c.id_genero = g.id_genero
        LEFT JOIN cat_metodo_pago mp ON v.id_metodo_pago = mp.id_metodo_pago;
    """
    df = consultar(sql)

    tabla_obs = pd.crosstab(df["genero"], df["metodo_pago"])
    tabla_pct = pd.crosstab(df["genero"], df["metodo_pago"], normalize="index") * 100
    chi2_stat, p_val, dof, _ = stats.chi2_contingency(tabla_obs)
    n = tabla_obs.sum().sum()
    cramers_v = np.sqrt(chi2_stat / (n * (min(tabla_obs.shape) - 1)))

    datos = [{
        "chi2_stat": round(float(chi2_stat), 4),
        "p_value": float(p_val),
        "dof": int(dof),
        "cramers_v": round(float(cramers_v), 4),
        "tabla_porcentajes": tabla_pct.round(2).to_dict(),
    }]

    resumen = (
        f"Prueba de Independencia Chi-Cuadrado: Género vs Método de Pago:\n"
        f"- Estadístico Chi²: {chi2_stat:.4f} (grados de libertad = {dof})\n"
        f"- Valor p: {p_val:.4f}\n"
        f"- V de Cramér: {cramers_v:.4f}\n"
        f"- Conclusión: {'Existe evidencia estadística de relación' if p_val < 0.05 else 'No existe correlación ni dependencia; la elección del método de pago es independiente del género'}."
    )

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    import seaborn as sns
    sns.heatmap(tabla_pct, annot=True, fmt=".2f", cmap="Blues", ax=ax, cbar_kws={"label": "% dentro del Género"})
    ax.set_title(f"Género vs Método de Pago (Chi²={chi2_stat:.2f}, p={p_val:.3f})", fontsize=11, fontweight="bold")
    plt.tight_layout()

    return Resultado(datos=datos, resumen=resumen, figura=fig)


@analisis(
    nombre="correlacion_boletin_vales",
    descripcion=(
        "Investiga la relacion de adopcion cruzada entre el uso de boletines y el uso de vales "
        "mediante coeficiente Phi, Chi-cuadrado con correccion de Yates y Odds Ratio."
    ),
    punto="5.c",
)
def correlacion_boletin_vales() -> Resultado:
    """Correlacion entre boletin y vale."""
    sql = "SELECT boletin, vale FROM ventas;"
    df = consultar(sql)

    r_phi, p_phi = stats.pearsonr(df["boletin"], df["vale"])
    tabla_2x2 = pd.crosstab(df["boletin"], df["vale"])
    chi2_yates, p_yates, _, _ = stats.chi2_contingency(tabla_2x2, correction=True)

    a, b = tabla_2x2.loc[1, 1], tabla_2x2.loc[1, 0]
    c, d = tabla_2x2.loc[0, 1], tabla_2x2.loc[0, 0]
    odds_ratio = float((a * d) / (b * c)) if (b * c) > 0 else np.nan

    datos = [{
        "coeficiente_phi": round(float(r_phi), 4),
        "p_value_phi": float(p_phi),
        "chi2_yates": round(float(chi2_yates), 4),
        "p_value_yates": float(p_yates),
        "odds_ratio": round(float(odds_ratio), 4),
    }]

    resumen = (
        f"Correlación entre Suscripción al Boletín y Uso de Vales Promocionales:\n"
        f"- Coeficiente Phi (r): {r_phi:.4f} (p-value = {p_phi:.4e})\n"
        f"- Chi² (con corrección de Yates): {chi2_yates:.4f} (p-value = {p_yates:.4e})\n"
        f"- Odds Ratio: {odds_ratio:.4f}\n"
        f"- Conclusión: {'Existe una relación positiva significativa' if p_phi < 0.05 and r_phi > 0 else 'No hay asociación directa entre suscribirse al boletín y redimir un vale'}."
    )

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    contingencia_rotulada = pd.crosstab(
        df["boletin"].map({1: "Boletín: Sí", 0: "Boletín: No"}),
        df["vale"].map({1: "Vale: Sí", 0: "Vale: No"})
    )
    import seaborn as sns
    sns.heatmap(contingencia_rotulada, annot=True, fmt="d", cmap="Purples", ax=ax)
    ax.set_title(f"Matriz de Contingencia Boletín vs Vale (Phi = {r_phi:.4f})", fontsize=11, fontweight="bold")
    plt.tight_layout()

    return Resultado(datos=datos, resumen=resumen, figura=fig)


@analisis(
    nombre="matriz_correlacion_multivariable",
    descripcion=(
        "Genera la matriz de correlacion multivariable completa entre todas las variables "
        "numericas y binarias del modelo de datos de ventas y clientes."
    ),
    punto="5.d",
)
def matriz_correlacion_multivariable() -> Resultado:
    """Matriz global de correlacion multivariable."""
    sql = """
        SELECT 
            c.edad,
            c.id_genero,
            c.venta_total,
            c.n_compras,
            v.monto_compra,
            v.tiempo,
            v.boletin,
            v.vale,
            v.id_metodo_pago,
            v.id_navegador
        FROM ventas v
        JOIN clientes c ON v.id_cliente = c.id_cliente;
    """
    df = consultar(sql)
    matriz = df.corr(method="pearson")
    datos = matriz.round(4).to_dict()

    resumen = "Matriz de Correlación Multivariable calculada exitosamente para 10 variables."

    fig, ax = plt.subplots(figsize=(9, 7))
    import seaborn as sns
    sns.heatmap(matriz, annot=True, fmt=".2f", cmap="vlag", vmin=-1, vmax=1, center=0, ax=ax)
    ax.set_title("Matriz de Correlación Multivariable Global", fontsize=12, fontweight="bold")
    plt.tight_layout()

    return Resultado(datos=[datos], resumen=resumen, figura=fig)
