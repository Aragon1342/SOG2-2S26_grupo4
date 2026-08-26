"""
PRACTICA 1 - SISTEMAS ORGANIZACIONALES Y GERENCIALES 2 (2S2026)
ESTUDIANTE 4: ANALISTA DE SEGMENTACION Y CORRELACIONES
-----------------------------------------------------------------------------
Script Integral de Analisis de Segmentacion de Clientes (Punto 4), Analisis
de Correlacion y Pruebas Estadisticas (Punto 5), y Generacion de Visualizaciones (Punto 6).

Funcionalidades:
1. Segmentacion de Clientes:
   - Rangos de Edad (18-25, 26-40, 41-55, 56+) y habitos de compra.
   - Comparativa por Genero (Masculino = 0 vs Femenino = 1).
   - Cuadrantes de Fidelizacion (Boletines y Vales: Ambos, Solo Boletin, Solo Vale, Ninguno).
2. Analisis de Correlacion y Pruebas de Hipotesis:
   - Edad vs Venta Total Acumulada (Pearson r, Spearman rho, Regresion Lineal OLS, R^2, p-value).
   - Genero vs Metodo de Pago Preferido (Prueba Chi-cuadrado, V de Cramer, p-value).
   - Boletin vs Vales Promocionales (Matriz de Contingencia 2x2, Coeficiente Phi, Odds Ratio).
   - Matriz Global de Correlacion Multivariable.
3. Generacion de 7 Graficos de Calidad Publicacion en 'graficas_segmentacion/'.
"""

import os
import pathlib
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Configuracion de rutas
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
OUTPUT_DIR = BASE_DIR / "graficas" / "graficas_segmentacion"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(ENV_PATH)

# Configuracion estetica global para graficas
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#2d3748"
plt.rcParams["axes.linewidth"] = 0.9
plt.rcParams["grid.alpha"] = 0.4
plt.rcParams["grid.linestyle"] = "--"


def obtener_conexion():
    """Obtiene motor de base de datos SQLAlchemy."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL no encontrada en el archivo .env")
    return create_engine(db_url)


def cargar_datos():
    """Carga y prepara los datasets de Clientes y Ventas desde AWS RDS."""
    engine = obtener_conexion()
    print("Conectando a AWS RDS PostgreSQL y extrayendo datos para Segmentacion y Correlacion...")

    sql_clientes = """
        SELECT 
            c.id_cliente, 
            c.edad, 
            c.id_genero,
            COALESCE(g.descripcion, 'No especificado') AS genero,
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
            COALESCE(mp.descripcion, 'Otro') AS metodo_pago,
            v.id_navegador,
            COALESCE(nav.descripcion, 'Otro') AS canal_navegador,
            v.tiempo,
            v.boletin,
            v.vale
        FROM ventas v
        LEFT JOIN cat_metodo_pago mp ON v.id_metodo_pago = mp.id_metodo_pago
        LEFT JOIN cat_navegador nav ON v.id_navegador = nav.id_navegador;
    """

    df_c = pd.read_sql(sql_clientes, engine)
    df_v = pd.read_sql(sql_ventas, engine)

    # Tipos de datos correctos
    df_v["fecha_compra"] = pd.to_datetime(df_v["fecha_compra"])

    # Enriquecer dataframe completo combinado
    df_completo = pd.merge(df_v, df_c, on="id_cliente", how="inner", suffixes=("_venta", "_cliente"))

    # Crear categoria de rango de edad
    bins_edad = [17, 25, 40, 55, 120]
    labels_edad = [
        "18-25 (Joven / Gen Z)",
        "26-40 (Adulto Joven / Millennial)",
        "41-55 (Adulto / Gen X)",
        "56+ (Adulto Mayor / Boomer)",
    ]
    df_completo["rango_edad"] = pd.cut(df_completo["edad"], bins=bins_edad, labels=labels_edad)
    df_c["rango_edad"] = pd.cut(df_c["edad"], bins=bins_edad, labels=labels_edad)

    # Crear categoria de cuadrante de fidelizacion
    def etiquetar_fidelizacion(row):
        b, v = row["boletin"], row["vale"]
        if b == 1 and v == 1:
            return "Ambos (Boletín y Vale)"
        elif b == 1 and v == 0:
            return "Solo Boletín"
        elif b == 0 and v == 1:
            return "Solo Vale"
        else:
            return "Ninguno (Orgánico)"

    df_completo["cuadrante_fidelizacion"] = df_completo.apply(etiquetar_fidelizacion, axis=1)

    print(f"-> Clientes cargados: {len(df_c):,}")
    print(f"-> Transacciones de ventas cargadas: {len(df_v):,}")
    print(f"-> Registros consolidados: {len(df_completo):,}")

    return df_c, df_v, df_completo


# =============================================================================
# SECCION 1: ANALISIS DE SEGMENTACION (PUNTO 4)
# =============================================================================

def segmentar_por_edad(df_c, df_completo):
    """Segmentacion por rangos de edad y habitos de compra."""
    print("\n" + "="*80)
    print("4.a SEGMENTACION DE CLIENTES POR RANGO DE EDAD")
    print("="*80)

    resumen_edad = df_completo.groupby("rango_edad", observed=False).agg(
        total_transacciones=("id_registro", "count"),
        clientes_unicos=("id_cliente", "nunique"),
        facturacion_total=("monto_compra", "sum"),
        ticket_promedio=("monto_compra", "mean"),
        ticket_mediana=("monto_compra", "median"),
        desv_ticket=("monto_compra", "std"),
        promedio_compras_cliente=("n_compras", "mean"),
        tiempo_promedio_sesion=("tiempo", "mean"),
        monto_minimo=("monto_compra", "min"),
        monto_maximo=("monto_compra", "max"),
    ).reset_index()

    total_facturacion = df_completo["monto_compra"].sum()
    total_trans = len(df_completo)

    resumen_edad["pct_transacciones"] = (resumen_edad["total_transacciones"] / total_trans) * 100
    resumen_edad["pct_facturacion"] = (resumen_edad["facturacion_total"] / total_facturacion) * 100

    print(resumen_edad.to_string(index=False))

    # Prueba ANOVA de 1 via para verificar si el ticket promedio difiere significativamente entre edades
    grupos_edad = [grupo["monto_compra"].dropna().values for _, grupo in df_completo.groupby("rango_edad", observed=False)]
    f_stat, p_val_anova = stats.f_oneway(*grupos_edad)
    print(f"\n[Prueba Estadistica ANOVA - Monto Compra por Rango de Edad]: F-statistic = {f_stat:.4f}, p-value = {p_val_anova:.4e}")
    if p_val_anova < 0.05:
        print("-> Conclusion: Existen diferencias estadisticamente significativas en el monto de compra entre rangos de edad.")
    else:
        print("-> Conclusion: No se observan diferencias estadisticamente significativas en el monto entre grupos etarios.")

    return resumen_edad, f_stat, p_val_anova


def segmentar_por_genero(df_completo):
    """Comparativa de comportamiento de compra segun genero (Genero 0 vs 1)."""
    print("\n" + "="*80)
    print("4.b COMPARACION DE COMPORTAMIENTO DE COMPRA SEGUN GENERO (0 vs 1)")
    print("="*80)

    resumen_genero = df_completo.groupby(["id_genero", "genero"]).agg(
        total_transacciones=("id_registro", "count"),
        clientes_unicos=("id_cliente", "nunique"),
        facturacion_total=("monto_compra", "sum"),
        ticket_promedio=("monto_compra", "mean"),
        ticket_mediana=("monto_compra", "median"),
        desv_ticket=("monto_compra", "std"),
        promedio_compras=("n_compras", "mean"),
        tiempo_promedio_sesion=("tiempo", "mean"),
        venta_total_acumulada_promedio=("venta_total", "mean"),
    ).reset_index()

    total_facturacion = df_completo["monto_compra"].sum()
    resumen_genero["pct_facturacion"] = (resumen_genero["facturacion_total"] / total_facturacion) * 100

    print(resumen_genero.to_string(index=False))

    # Prueba t de Student y Mann-Whitney U para comparar ticket entre generos
    grupo_m = df_completo[df_completo["id_genero"] == 0]["monto_compra"].dropna()
    grupo_f = df_completo[df_completo["id_genero"] == 1]["monto_compra"].dropna()

    t_stat, p_val_ttest = stats.ttest_ind(grupo_m, grupo_f, equal_var=False)
    u_stat, p_val_mann = stats.mannwhitneyu(grupo_m, grupo_f)

    print(f"\n[Prueba t de Student (Welch)]: t = {t_stat:.4f}, p-value = {p_val_ttest:.4e}")
    print(f"[Prueba U de Mann-Whitney]: U = {u_stat:.1f}, p-value = {p_val_mann:.4e}")

    return resumen_genero, (t_stat, p_val_ttest, u_stat, p_val_mann)


def segmentar_por_boletin_vales(df_completo):
    """Segmentacion en 4 cuadrantes de Boletin y Vales Promocionales."""
    print("\n" + "="*80)
    print("4.c SEGMENTACION POR USO DE BOLETIN Y VALES PROMOCIONALES (4 CUADRANTES)")
    print("="*80)

    resumen_promo = df_completo.groupby("cuadrante_fidelizacion").agg(
        total_transacciones=("id_registro", "count"),
        clientes_unicos=("id_cliente", "nunique"),
        facturacion_total=("monto_compra", "sum"),
        ticket_promedio=("monto_compra", "mean"),
        ticket_mediana=("monto_compra", "median"),
        desv_ticket=("monto_compra", "std"),
        tiempo_promedio_sesion=("tiempo", "mean"),
        min_compra=("monto_compra", "min"),
        max_compra=("monto_compra", "max"),
    ).reset_index()

    total_facturacion = df_completo["monto_compra"].sum()
    resumen_promo["pct_facturacion"] = (resumen_promo["facturacion_total"] / total_facturacion) * 100
    resumen_promo["pct_transacciones"] = (resumen_promo["total_transacciones"] / len(df_completo)) * 100

    print(resumen_promo.to_string(index=False))

    # Prueba ANOVA entre cuadrantes
    grupos_promo = [grupo["monto_compra"].dropna().values for _, grupo in df_completo.groupby("cuadrante_fidelizacion")]
    f_stat_p, p_val_promo = stats.f_oneway(*grupos_promo)
    print(f"\n[Prueba ANOVA - Monto por Cuadrante Promocional]: F = {f_stat_p:.4f}, p-value = {p_val_promo:.4e}")

    return resumen_promo, f_stat_p, p_val_promo


# =============================================================================
# SECCION 2: ANALISIS DE CORRELACION Y PRUEBAS ESTADISTICAS (PUNTO 5)
# =============================================================================

def correlacion_edad_venta(df_c, df_completo):
    """Analisis de correlacion entre Edad y Ventas (Total y Transaccional)."""
    print("\n" + "="*80)
    print("5.a ANALISIS DE CORRELACION: EDAD VS VENTA TOTAL ACUMULADA Y MONTO TRANSACCIONAL")
    print("="*80)

    # 1. A nivel de Clientes (Edad vs Venta_Total)
    sub_c = df_c[["edad", "venta_total"]].dropna()
    r_pearson_c, p_pearson_c = stats.pearsonr(sub_c["edad"], sub_c["venta_total"])
    r_spearman_c, p_spearman_c = stats.spearmanr(sub_c["edad"], sub_c["venta_total"])

    # Regresion lineal OLS
    slope_c, intercept_c, r_val_c, p_val_reg_c, std_err_c = stats.linregress(sub_c["edad"], sub_c["venta_total"])
    r2_c = r_val_c ** 2

    print(f"--- Nivel Cliente (Edad vs Venta Total Acumulada, N={len(sub_c):,}) ---")
    print(f"-> Coeficiente de Pearson (r):   {r_pearson_c:.5f} (p-value = {p_pearson_c:.4e})")
    print(f"-> Coeficiente de Spearman (rho): {r_spearman_c:.5f} (p-value = {p_spearman_c:.4e})")
    print(f"-> Recta de Regresion:            Venta_Total = {slope_c:.4f} * Edad + {intercept_c:.4f}")
    print(f"-> Coeficiente de Determinacion (R2): {r2_c:.6f} ({r2_c*100:.4f}% de la varianza explicada)")

    # 2. A nivel Transaccional (Edad vs MontoCompra)
    sub_v = df_completo[["edad", "monto_compra"]].dropna()
    r_pearson_v, p_pearson_v = stats.pearsonr(sub_v["edad"], sub_v["monto_compra"])
    r_spearman_v, p_spearman_v = stats.spearmanr(sub_v["edad"], sub_v["monto_compra"])
    slope_v, intercept_v, r_val_v, p_val_reg_v, std_err_v = stats.linregress(sub_v["edad"], sub_v["monto_compra"])
    r2_v = r_val_v ** 2

    print(f"\n--- Nivel Transaccional (Edad vs Monto Compra, N={len(sub_v):,}) ---")
    print(f"-> Coeficiente de Pearson (r):   {r_pearson_v:.5f} (p-value = {p_pearson_v:.4e})")
    print(f"-> Coeficiente de Spearman (rho): {r_spearman_v:.5f} (p-value = {p_spearman_v:.4e})")
    print(f"-> Recta de Regresion:            MontoCompra = {slope_v:.4f} * Edad + {intercept_v:.4f}")
    print(f"-> Coeficiente de Determinacion (R2): {r2_v:.6f}")

    resultados = {
        "cliente": {
            "r_pearson": r_pearson_c,
            "p_pearson": p_pearson_c,
            "r_spearman": r_spearman_c,
            "p_spearman": p_spearman_c,
            "slope": slope_c,
            "intercept": intercept_c,
            "r2": r2_c,
            "std_err": std_err_c,
        },
        "transaccional": {
            "r_pearson": r_pearson_v,
            "p_pearson": p_pearson_v,
            "r_spearman": r_spearman_v,
            "p_spearman": p_spearman_v,
            "slope": slope_v,
            "intercept": intercept_v,
            "r2": r2_v,
            "std_err": std_err_v,
        }
    }
    return resultados


def correlacion_genero_metodo_pago(df_completo):
    """Prueba Chi-cuadrado y V de Cramer para evaluar relacion Genero vs Metodo de Pago."""
    print("\n" + "="*80)
    print("5.b CORRELACION E INDEPENDENCIA: GENERO VS METODO DE PAGO PREFERIDO")
    print("="*80)

    tabla_contingencia = pd.crosstab(
        df_completo["genero"],
        df_completo["metodo_pago"],
        margins=True,
        margins_name="Total"
    )
    print("Tabla de Contingencia (Frecuencias Observadas):")
    print(tabla_contingencia)

    tabla_porcentajes = pd.crosstab(
        df_completo["genero"],
        df_completo["metodo_pago"],
        normalize="index"
    ) * 100
    print("\nDistribucion Porcentual dentro de cada Genero (%):")
    print(tabla_porcentajes.round(2))

    # Prueba Chi-cuadrado sin los margenes
    tabla_obs = pd.crosstab(df_completo["genero"], df_completo["metodo_pago"])
    chi2_stat, p_val_chi2, dof, esperados = stats.chi2_contingency(tabla_obs)

    # Coeficiente V de Cramer
    n = tabla_obs.sum().sum()
    min_dim = min(tabla_obs.shape) - 1
    cramers_v = np.sqrt(chi2_stat / (n * min_dim))

    print(f"\n[Resultados Prueba Chi-cuadrado de Independencia]:")
    print(f"-> Estadistico Chi-cuadrado (chi2): {chi2_stat:.4f}")
    print(f"-> Grados de Libertad (dof):        {dof}")
    print(f"-> Valor p (p-value):               {p_val_chi2:.4e}")
    print(f"-> Coeficiente V de Cramer:         {cramers_v:.5f}")

    if p_val_chi2 < 0.05:
        print("-> Conclusion: Existe asociacion estadisticamente significativa entre Genero y Metodo de Pago.")
    else:
        print("-> Conclusion: No existe evidencia de asociacion (las variables son independientes).")

    return {
        "tabla_obs": tabla_obs,
        "tabla_porcentajes": tabla_porcentajes,
        "chi2_stat": chi2_stat,
        "p_val_chi2": p_val_chi2,
        "dof": dof,
        "cramers_v": cramers_v,
    }


def correlacion_boletin_vales(df_completo):
    """Analisis de correlacion entre Uso de Boletin y Uso de Vales."""
    print("\n" + "="*80)
    print("5.c CORRELACION ENTRE USO DE BOLETIN Y USO DE VALES PROMOCIONALES")
    print("="*80)

    contingencia_promo = pd.crosstab(
        df_completo["boletin"].map({1: "Boletín (Sí)", 0: "Boletín (No)"}),
        df_completo["vale"].map({1: "Vale (Sí)", 0: "Vale (No)"}),
        margins=True,
        margins_name="Total"
    )
    print("Tabla de Contingencia 2x2:")
    print(contingencia_promo)

    # Correlacion de Pearson / Coeficiente Phi para binarias
    r_phi, p_phi = stats.pearsonr(df_completo["boletin"], df_completo["vale"])

    # Chi-cuadrado con correccion de continuidad de Yates
    tabla_2x2 = pd.crosstab(df_completo["boletin"], df_completo["vale"])
    chi2_yates, p_val_yates, dof_y, _ = stats.chi2_contingency(tabla_2x2, correction=True)

    # Odds Ratio (Razon de Momios)
    # [[a, b], [c, d]]
    # a: Boletin=0, Vale=0; b: Boletin=0, Vale=1; c: Boletin=1, Vale=0; d: Boletin=1, Vale=1
    a = tabla_2x2.loc[1, 1]
    b = tabla_2x2.loc[1, 0]
    c = tabla_2x2.loc[0, 1]
    d = tabla_2x2.loc[0, 0]
    odds_ratio = (a * d) / (b * c) if (b * c) > 0 else np.nan

    print(f"\n[Resultados Estadisticos de Asociacion Promocional]:")
    print(f"-> Coeficiente Phi (r):              {r_phi:.5f} (p-value = {p_phi:.4e})")
    print(f"-> Chi-cuadrado (Yates correction):  {chi2_yates:.4f} (p-value = {p_val_yates:.4e})")
    print(f"-> Odds Ratio (Razon de Momios):     {odds_ratio:.4f}")

    return {
        "contingencia_promo": contingencia_promo,
        "r_phi": r_phi,
        "p_phi": p_phi,
        "chi2_yates": chi2_yates,
        "p_val_yates": p_val_yates,
        "odds_ratio": odds_ratio,
    }


def matriz_correlacion_multivariable(df_completo):
    """Calcula matriz de correlacion completa entre todas las variables numericas y dummy."""
    print("\n" + "="*80)
    print("5.d MATRIZ DE CORRELACION MULTIVARIABLE (PEARSON & SPEARMAN)")
    print("="*80)

    columnas_analisis = [
        "edad",
        "id_genero",
        "venta_total",
        "n_compras",
        "monto_compra",
        "tiempo",
        "boletin",
        "vale",
        "id_metodo_pago",
        "id_navegador",
    ]
    df_sub = df_completo[columnas_analisis].dropna()
    matriz_pearson = df_sub.corr(method="pearson")
    matriz_spearman = df_sub.corr(method="spearman")

    print("Matriz de Correlacion de Pearson:")
    print(matriz_pearson.round(4))

    return matriz_pearson, matriz_spearman


# =============================================================================
# SECCION 3: GENERACION DE 7 GRAFICAS PROFESIONALES (PUNTO 6)
# =============================================================================

def generar_grafica_1_segmentacion_edad(df_completo, resumen_edad):
    """Grafica 1: Barras agrupadas con doble eje (Ventas Totales y Ticket Promedio por Edad)."""
    fig, ax1 = plt.subplots(figsize=(10, 6))

    x = np.arange(len(resumen_edad))
    width = 0.4

    color_bar = "#1f77b4"
    color_line = "#d62728"

    # Barras de facturacion
    bars = ax1.bar(
        x - width/2,
        resumen_edad["facturacion_total"] / 1000,
        width,
        label="Facturación Total (Miles USD)",
        color=color_bar,
        edgecolor="#0f3c5c",
        alpha=0.85,
    )
    ax1.set_ylabel("Facturación Total (Miles de USD)", color=color_bar, fontsize=11, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor=color_bar)
    ax1.set_xticks(x)
    ax1.set_xticklabels(resumen_edad["rango_edad"], fontsize=9.5, fontweight="bold")
    ax1.set_title("Gráfico 1: Facturación Total y Ticket Promedio por Rango de Edad", fontsize=13, fontweight="bold", pad=15)

    # Anotaciones en barras
    for bar, pct in zip(bars, resumen_edad["pct_facturacion"]):
        height = bar.get_height()
        ax1.annotate(
            f"${height:.1f}k\n({pct:.1f}%)",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=8.5, fontweight="bold",
            color="#0f3c5c"
        )

    # Eje secundario para ticket promedio
    ax2 = ax1.twinx()
    lines = ax2.plot(
        x + width/2,
        resumen_edad["ticket_promedio"],
        color=color_line,
        marker="o",
        linewidth=2.5,
        markersize=8,
        label="Ticket Promedio ($ USD)"
    )
    ax2.set_ylabel("Ticket Promedio ($ USD)", color=color_line, fontsize=11, fontweight="bold")
    ax2.tick_params(axis="y", labelcolor=color_line)
    ax2.set_ylim(bottom=0, top=resumen_edad["ticket_promedio"].max() * 1.35)

    for i, txt in enumerate(resumen_edad["ticket_promedio"]):
        ax2.annotate(
            f"${txt:.2f}",
            (x[i] + width/2, txt),
            xytext=(0, 7),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            fontweight="bold",
            color=color_line
        )

    plt.tight_layout()
    ruta = OUTPUT_DIR / "01_segmentacion_edad_ventas_ticket.png"
    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"-> Gráfica 1 guardada: {ruta}")
    return ruta


def generar_grafica_2_segmentacion_genero(resumen_genero):
    """Grafica 2: Barras comparativas / Distribucion por Genero."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5))

    colores = ["#2b6cb0", "#e53e3e"]
    etiquetas = ["Masculino (0)", "Femenino (1)"]

    # 1. Facturacion Total
    bars1 = ax1.bar(
        etiquetas,
        resumen_genero["facturacion_total"] / 1000,
        color=colores,
        edgecolor="#1a202c",
        width=0.55,
        alpha=0.88,
    )
    ax1.set_title("Facturación Total por Género", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Facturación (Miles de USD)", fontsize=10, fontweight="bold")
    for bar, pct, tot in zip(bars1, resumen_genero["pct_facturacion"], resumen_genero["facturacion_total"]):
        ax1.annotate(
            f"${tot/1000:.1f}k\n({pct:.1f}%)",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=9, fontweight="bold"
        )
    ax1.set_ylim(0, (resumen_genero["facturacion_total"].max() / 1000) * 1.25)

    # 2. Ticket Promedio y LTV
    x = np.arange(len(etiquetas))
    w = 0.35
    b_ticket = ax2.bar(x - w/2, resumen_genero["ticket_promedio"], w, label="Ticket Promedio", color="#3182ce", alpha=0.85)
    b_ltv = ax2.bar(x + w/2, resumen_genero["venta_total_acumulada_promedio"], w, label="Venta Total Prom. Cliente", color="#38a169", alpha=0.85)

    ax2.set_title("Comparativa de Ticket y Venta Total por Cliente", fontsize=12, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(etiquetas, fontweight="bold")
    ax2.set_ylabel("Monto ($ USD)", fontsize=10, fontweight="bold")
    ax2.legend(loc="upper right", frameon=True)

    for bar in list(b_ticket) + list(b_ltv):
        h = bar.get_height()
        ax2.annotate(
            f"${h:.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=8.5, fontweight="bold"
        )
    ax2.set_ylim(0, max(resumen_genero["venta_total_acumulada_promedio"].max(), resumen_genero["ticket_promedio"].max()) * 1.25)

    fig.suptitle("Gráfico 2: Comportamiento Comercial Comparativo según Género (0 vs 1)", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    ruta = OUTPUT_DIR / "02_segmentacion_genero_comportamiento.png"
    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"-> Gráfica 2 guardada: {ruta}")
    return ruta


def generar_grafica_3_segmentacion_boletin_vales(resumen_promo):
    """Grafica 3: Desempeño de 4 Cuadrantes de Promocion / Fidelizacion."""
    fig, ax = plt.subplots(figsize=(10, 6))

    colores = ["#805ad5", "#319795", "#dd6b20", "#718096"]
    bars = ax.barh(
        resumen_promo["cuadrante_fidelizacion"],
        resumen_promo["facturacion_total"] / 1000,
        color=colores,
        edgecolor="#2d3748",
        height=0.6,
        alpha=0.88,
    )

    ax.set_xlabel("Facturación Total (Miles de USD)", fontsize=11, fontweight="bold")
    ax.set_title("Gráfico 3: Desempeño Comercial según Segmento de Fidelización (Boletines y Vales)", fontsize=13, fontweight="bold", pad=15)

    for bar, ticket, trans, pct in zip(
        bars,
        resumen_promo["ticket_promedio"],
        resumen_promo["total_transacciones"],
        resumen_promo["pct_facturacion"]
    ):
        width = bar.get_width()
        ax.annotate(
            f" ${width:.1f}k ({pct:.1f}%)\n Ticket Prom: ${ticket:.2f} | Trans: {trans:,}",
            xy=(width, bar.get_y() + bar.get_height() / 2),
            xytext=(6, 0),
            textcoords="offset points",
            ha="left", va="center",
            fontsize=8.5, fontweight="bold",
            color="#1a202c"
        )

    ax.set_xlim(0, (resumen_promo["facturacion_total"].max() / 1000) * 1.35)
    plt.tight_layout()
    ruta = OUTPUT_DIR / "03_segmentacion_boletin_vales_cuadrantes.png"
    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"-> Gráfica 3 guardada: {ruta}")
    return ruta


def generar_grafica_4_scatter_edad_venta(df_c, res_corr):
    """Grafica 4: Scatter Plot con Recta de Regresion OLS (Edad vs Venta Total)."""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Puntos de dispersion
    ax.scatter(
        df_c["edad"],
        df_c["venta_total"],
        alpha=0.45,
        color="#2b6cb0",
        edgecolors="none",
        s=30,
        label="Clientes (Observaciones)",
    )

    # Recta de regresion lineal
    x_vals = np.linspace(df_c["edad"].min(), df_c["edad"].max(), 200)
    slope = res_corr["cliente"]["slope"]
    intercept = res_corr["cliente"]["intercept"]
    r_pearson = res_corr["cliente"]["r_pearson"]
    p_val = res_corr["cliente"]["p_pearson"]
    r2 = res_corr["cliente"]["r2"]

    y_vals = slope * x_vals + intercept
    ax.plot(
        x_vals,
        y_vals,
        color="#e53e3e",
        linewidth=2.8,
        label=f"Regresión OLS: Venta = {slope:.2f}*Edad + {intercept:.2f}",
    )

    # Estadisticas en caja de texto
    info_texto = (
        f"Coeficiente Pearson (r): {r_pearson:.4f}\n"
        f"Coeficiente Spearman (ρ): {res_corr['cliente']['r_spearman']:.4f}\n"
        f"Coef. Determinación (R²): {r2:.6f}\n"
        f"Valor p: {p_val:.4e}\n"
        f"Interpretación: Relación prácticamente nula / ortogonal"
    )
    ax.text(
        0.03, 0.95,
        info_texto,
        transform=ax.transAxes,
        fontsize=9.5,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#edf2f7", edgecolor="#cbd5e0", alpha=0.95),
    )

    ax.set_title("Gráfico 4: Análisis de Correlación y Dispersión: Edad vs Venta Total Acumulada", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Edad del Cliente (Años)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Venta Total Acumulada ($ USD)", fontsize=11, fontweight="bold")
    ax.legend(loc="upper right", frameon=True)

    plt.tight_layout()
    ruta = OUTPUT_DIR / "04_scatter_edad_vs_venta_total_regresion.png"
    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"-> Gráfica 4 guardada: {ruta}")
    return ruta


def generar_grafica_5_heatmap_genero_pago(res_chi):
    """Grafica 5: Heatmap de Contingencia (Genero vs Metodo de Pago Preferido)."""
    fig, ax = plt.subplots(figsize=(9, 5.5))

    tabla_pct = res_chi["tabla_porcentajes"]
    sns.heatmap(
        tabla_pct,
        annot=True,
        fmt=".2f",
        cmap="Blues",
        cbar_kws={"label": "Porcentaje dentro del Género (%)"},
        linewidths=1.2,
        linecolor="#ffffff",
        ax=ax,
        annot_kws={"fontsize": 11, "fontweight": "bold"},
    )

    chi2 = res_chi["chi2_stat"]
    pval = res_chi["p_val_chi2"]
    v_cramer = res_chi["cramers_v"]

    ax.set_title(
        f"Gráfico 5: Distribución de Métodos de Pago según Género (Heatmap de Contingencia)\n"
        f"[Chi² = {chi2:.2f}, p-val = {pval:.4f}, V de Cramér = {v_cramer:.4f}]",
        fontsize=12,
        fontweight="bold",
        pad=12,
    )
    ax.set_xlabel("Método de Pago Seleccionado", fontsize=11, fontweight="bold")
    ax.set_ylabel("Género del Cliente", fontsize=11, fontweight="bold")

    plt.tight_layout()
    ruta = OUTPUT_DIR / "05_heatmap_genero_vs_metodo_pago.png"
    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"-> Gráfica 5 guardada: {ruta}")
    return ruta


def generar_grafica_6_matriz_correlacion(matriz_pearson):
    """Grafica 6: Heatmap de Matriz de Correlacion Multivariable."""
    fig, ax = plt.subplots(figsize=(10, 8))

    etiquetas_legibles = [
        "Edad",
        "Género (0=M, 1=F)",
        "Venta Total Acum.",
        "N° Compras Hist.",
        "Monto Compra Trans.",
        "Tiempo Sesión (s)",
        "Suscripción Boletín",
        "Uso de Vale",
        "Método de Pago",
        "Canal Navegador",
    ]

    mask = np.triu(np.ones_like(matriz_pearson, dtype=bool), k=1)

    sns.heatmap(
        matriz_pearson,
        annot=True,
        fmt=".3f",
        cmap="vlag",
        vmin=-1,
        vmax=1,
        center=0,
        linewidths=0.8,
        cbar_kws={"label": "Coeficiente de Correlación de Pearson (r)"},
        xticklabels=etiquetas_legibles,
        yticklabels=etiquetas_legibles,
        ax=ax,
        annot_kws={"fontsize": 8.5},
    )

    ax.set_title("Gráfico 6: Matriz de Correlación Multivariable de Variables Transaccionales y Demográficas", fontsize=12, fontweight="bold", pad=15)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.yticks(rotation=0, fontsize=9)

    plt.tight_layout()
    ruta = OUTPUT_DIR / "06_heatmap_matriz_correlacion_multivariable.png"
    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"-> Gráfica 6 guardada: {ruta}")
    return ruta


def generar_grafica_7_boxplot_fidelizacion(df_completo):
    """Grafica 7: Boxplot de Distribucion del Monto de Compra por Fidelizacion (Boletin y Vale)."""
    fig, ax = plt.subplots(figsize=(10, 6))

    colores = ["#805ad5", "#319795", "#dd6b20", "#718096"]
    sns.boxplot(
        x="cuadrante_fidelizacion",
        y="monto_compra",
        data=df_completo,
        palette=colores,
        ax=ax,
        showmeans=True,
        meanprops={"marker": "D", "markerfacecolor": "yellow", "markeredgecolor": "black", "markersize": 7},
        boxprops={"alpha": 0.85},
    )

    ax.set_title("Gráfico 7: Distribución y Dispersión del Monto de Compra por Cuadrante Promocional (Boxplot)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Segmento de Fidelización / Promoción", fontsize=11, fontweight="bold")
    ax.set_ylabel("Monto de Compra ($ USD)", fontsize=11, fontweight="bold")

    # Leyenda para medias
    ax.scatter([], [], marker="D", color="yellow", edgecolors="black", label="Media Aritmética (Rombo)")
    ax.legend(loc="upper right", frameon=True)

    plt.tight_layout()
    ruta = OUTPUT_DIR / "07_boxplot_monto_compra_por_fidelizacion.png"
    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"-> Gráfica 7 guardada: {ruta}")
    return ruta


# =============================================================================
# FUNCION PRINCIPAL DE EJECUCION
# =============================================================================

def main():
    print("="*80)
    print("INICIANDO ANALISIS DE SEGMENTACION Y CORRELACIONES (ESTUDIANTE 4)")
    print("="*80)

    df_c, df_v, df_completo = cargar_datos()

    # 1. Segmentaciones
    resumen_edad, f_stat_edad, p_val_edad = segmentar_por_edad(df_c, df_completo)
    resumen_genero, stats_genero = segmentar_por_genero(df_completo)
    resumen_promo, f_stat_promo, p_val_promo = segmentar_por_boletin_vales(df_completo)

    # 2. Correlaciones
    res_corr_edad = correlacion_edad_venta(df_c, df_completo)
    res_chi_genero = correlacion_genero_metodo_pago(df_completo)
    res_promo_corr = correlacion_boletin_vales(df_completo)
    matriz_pearson, matriz_spearman = matriz_correlacion_multivariable(df_completo)

    # 3. Generacion de 7 Graficas
    print("\n" + "="*80)
    print("GENERANDO 7 VISUALIZACIONES PROFESIONALES (PUNTO 6 DEL ALCANCE)")
    print("="*80)
    g1 = generar_grafica_1_segmentacion_edad(df_completo, resumen_edad)
    g2 = generar_grafica_2_segmentacion_genero(resumen_genero)
    g3 = generar_grafica_3_segmentacion_boletin_vales(resumen_promo)
    g4 = generar_grafica_4_scatter_edad_venta(df_c, res_corr_edad)
    g5 = generar_grafica_5_heatmap_genero_pago(res_chi_genero)
    g6 = generar_grafica_6_matriz_correlacion(matriz_pearson)
    g7 = generar_grafica_7_boxplot_fidelizacion(df_completo)

    print("\n" + "="*80)
    print("ANALISIS COMPLETADO EXITOSAMENTE. TODAS LAS GRAFICAS HAN SIDO GENERADAS.")
    print("="*80)


if __name__ == "__main__":
    main()
