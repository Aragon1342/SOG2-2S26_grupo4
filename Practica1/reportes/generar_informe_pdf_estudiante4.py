"""
Generador de Informe Tecnico en Formato PDF - Estudiante 4: Segmentacion y Correlaciones
Practica 1: Sistemas Organizacionales y Gerenciales 2 (2S2026)
Grupo 4 - Universidad de San Carlos de Guatemala
"""

import os
import pathlib
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
GRAFICAS_DIR = BASE_DIR / "graficas" / "graficas_segmentacion"
PDF_PATH = pathlib.Path(__file__).resolve().parent / "SOG2-2S26_grupo4_Estudiante4_Segmentacion_Correlacion.pdf"


def construir_pdf():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados
    titulo_style = ParagraphStyle(
        "TituloPrincipal",
        parent=styles["Heading1"],
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#1a365d"),
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        spaceAfter=4,
    )

    subtitulo_style = ParagraphStyle(
        "SubtituloPrincipal",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4a5568"),
        alignment=TA_CENTER,
        fontName="Helvetica",
        spaceAfter=12,
    )

    h1_style = ParagraphStyle(
        "SeccionH1",
        parent=styles["Heading2"],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1a365d"),
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=6,
    )

    h2_style = ParagraphStyle(
        "SeccionH2",
        parent=styles["Heading3"],
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#2b6cb0"),
        fontName="Helvetica-Bold",
        spaceBefore=7,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "Cuerpo",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#2d3748"),
        alignment=TA_JUSTIFY,
        fontName="Helvetica",
        spaceAfter=5,
    )

    bullet_style = ParagraphStyle(
        "BulletCustom",
        parent=body_style,
        leftIndent=12,
        bulletIndent=4,
        spaceAfter=3,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.white,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#2d3748"),
        fontName="Helvetica",
        alignment=TA_CENTER,
    )

    table_cell_left = ParagraphStyle(
        "TableCellLeft",
        parent=table_cell_style,
        alignment=TA_LEFT,
    )

    elementos = []

    # =========================================================================
    # ENCABEZADO PRINCIPAL
    # =========================================================================
    elementos.append(Paragraph("INFORME TÉCNICO: SEGMENTACIÓN DE CLIENTES Y CORRELACIONES", titulo_style))
    elementos.append(Paragraph("Práctica 1 — Sistemas Organizacionales y Gerenciales 2 | Grupo 4<br/><b>Estudiante 4: Analista de Segmentación y Correlaciones</b> (Puntos 4, 5 y 6 del Alcance)", subtitulo_style))
    elementos.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1a365d"), spaceAfter=10))

    # =========================================================================
    # SECCION 1: INTRODUCCION Y METODOLOGIA DE VISUALIZACION
    # =========================================================================
    elementos.append(Paragraph("1. INTRODUCCIÓN Y METODOLOGÍA DE VISUALIZACIONES (PUNTO 6)", h1_style))
    elementos.append(Paragraph(
        "El presente informe técnico expone el análisis integral de <b>Segmentación de Clientes (Punto 4)</b>, "
        "<b>Análisis de Correlación e Inferencia Estadística (Punto 5)</b> y la <b>Generación de Visualizaciones (Punto 6)</b> "
        "sobre el dataset de 6,500 transacciones del año 2021 alojado en <b>PostgreSQL en AWS RDS</b>. "
        "Para comunicar con rigor los hallazgos a la gerencia, cada tipo de gráfica fue seleccionado en estricta función "
        "de la tipología de variables evaluadas (continuas, discretas, categóricas nominales y ordinales).",
        body_style
    ))

    datos_metodologia = [
        [Paragraph("Gráfica", table_header_style), Paragraph("Tipo de Gráfico", table_header_style), Paragraph("Variables", table_header_style), Paragraph("Justificación Metodológica", table_header_style)],
        [Paragraph("Gráfica 1", table_cell_left), Paragraph("Barras con Eje Gemelo", table_cell_style), Paragraph("Edad vs Facturación y Ticket", table_cell_style), Paragraph("Permite contrastar simultáneamente volumen agregado ($) e intensidad media unitaria ($).", table_cell_left)],
        [Paragraph("Gráfica 2", table_cell_left), Paragraph("Barras Comparativas", table_cell_style), Paragraph("Género vs Facturación, Ticket, LTV", table_cell_style), Paragraph("Compara magnitudes directas entre dos grupos independientes verificando simetría de mercado.", table_cell_left)],
        [Paragraph("Gráfica 3", table_cell_left), Paragraph("Barras Compuestas 4Q", table_cell_style), Paragraph("Boletín x Vales vs Desempeño", table_cell_style), Paragraph("La orientación horizontal facilita contrastar el impacto económico de 4 combinaciones promocionales.", table_cell_left)],
        [Paragraph("Gráfica 4", table_cell_left), Paragraph("Scatter Plot con OLS", table_cell_style), Paragraph("Edad vs Venta Total Acumulada", table_cell_style), Paragraph("Estándar para evaluar dispersión, homocedasticidad y la recta de regresión con R².", table_cell_left)],
        [Paragraph("Gráfica 5", table_cell_left), Paragraph("Heatmap de Contingencia", table_cell_style), Paragraph("Género x Método de Pago", table_cell_style), Paragraph("Visualiza concentraciones de frecuencias relativas cruzadas entre dos variables cualitativas.", table_cell_left)],
        [Paragraph("Gráfica 6", table_cell_left), Paragraph("Heatmap de Correlación", table_cell_style), Paragraph("10 Variables del Modelo", table_cell_style), Paragraph("Presenta la matriz simétrica de coeficientes de Pearson con paleta divergente centrada en cero.", table_cell_left)],
        [Paragraph("Gráfica 7", table_cell_left), Paragraph("Boxplot con Medias", table_cell_style), Paragraph("Cuadrante Promo vs Monto Compra", table_cell_style), Paragraph("Exhibe medianas, cuartiles (IQR), valores atípicos y dispersión entre tratamientos de fidelización.", table_cell_left)],
    ]

    t_metodo = Table(datos_metodologia, colWidths=[0.8*inch, 1.4*inch, 1.7*inch, 3.1*inch])
    t_metodo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a365d")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
    ]))
    elementos.append(t_metodo)
    elementos.append(Spacer(1, 6))

    # =========================================================================
    # SECCION 2: SEGMENTACION DE CLIENTES (PUNTO 4)
    # =========================================================================
    elementos.append(Paragraph("2. SEGMENTACIÓN DE CLIENTES (PUNTO 4 DEL ALCANCE)", h1_style))
    
    # 2.1 Edad
    elementos.append(Paragraph("2.1 Segmentación por Cohortes de Edad y Hábitos de Compra (Punto 4.a)", h2_style))

    datos_tabla_edad = [
        [Paragraph("Rango de Edad", table_header_style), Paragraph("Clientes", table_header_style), Paragraph("% Clientes", table_header_style), Paragraph("Facturación ($)", table_header_style), Paragraph("% Fact.", table_header_style), Paragraph("Ticket Prom.", table_header_style), Paragraph("Tiempo (s)", table_header_style)],
        [Paragraph("18-25 (Joven / Gen Z)", table_cell_left), Paragraph("1,061", table_cell_style), Paragraph("16.32%", table_cell_style), Paragraph("$41,414.73", table_cell_style), Paragraph("16.01%", table_cell_style), Paragraph("$39.03", table_cell_style), Paragraph("763.51 s", table_cell_style)],
        [Paragraph("26-40 (Adulto Joven / Millennial)", table_cell_left), Paragraph("3,425", table_cell_style), Paragraph("52.69%", table_cell_style), Paragraph("$136,547.45", table_cell_style), Paragraph("52.80%", table_cell_style), Paragraph("$39.87", table_cell_style), Paragraph("770.83 s", table_cell_style)],
        [Paragraph("41-55 (Adulto / Gen X)", table_cell_left), Paragraph("1,607", table_cell_style), Paragraph("24.72%", table_cell_style), Paragraph("$64,300.91", table_cell_style), Paragraph("24.86%", table_cell_style), Paragraph("$40.01", table_cell_style), Paragraph("765.17 s", table_cell_style)],
        [Paragraph("56+ (Adulto Mayor / Boomer)", table_cell_left), Paragraph("407", table_cell_style), Paragraph("6.26%", table_cell_style), Paragraph("$16,352.77", table_cell_style), Paragraph("6.32%", table_cell_style), Paragraph("$40.18", table_cell_style), Paragraph("758.33 s", table_cell_style)],
        [Paragraph("<b>TOTAL</b>", table_cell_left), Paragraph("<b>6,500</b>", table_cell_style), Paragraph("<b>100.00%</b>", table_cell_style), Paragraph("<b>$258,615.86</b>", table_cell_style), Paragraph("<b>100.00%</b>", table_cell_style), Paragraph("<b>$39.79</b>", table_cell_style), Paragraph("<b>767.38 s</b>", table_cell_style)],
    ]
    t_edad = Table(datos_tabla_edad, colWidths=[2.2*inch, 0.8*inch, 0.8*inch, 1.1*inch, 0.7*inch, 0.9*inch, 0.9*inch])
    t_edad.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a365d")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor("#f7fafc")]),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#edf2f7")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
    ]))
    elementos.append(t_edad)
    elementos.append(Spacer(1, 4))

    # Grafica 1
    g1_path = GRAFICAS_DIR / "01_segmentacion_edad_ventas_ticket.png"
    if g1_path.exists():
        elementos.append(Image(str(g1_path), width=6.6*inch, height=2.4*inch))
        elementos.append(Spacer(1, 4))

    elementos.append(Paragraph(
        "<b>Interpretación Técnica y Estadística:</b> La prueba ANOVA de un factor (<i>F = 0.9419, p = 0.4193</i>) confirma que el ticket promedio es homogéneo entre edades (~$40). "
        "No obstante, el <b>52.8% de los ingresos totales ($136,547.45)</b> se concentra en la cohorte de <b>26 a 40 años</b>, consolidando a los Millennials como el motor financiero prioritario.",
        body_style
    ))

    # 2.2 Genero
    elementos.append(Paragraph("2.2 Comparación de Comportamiento de Compra según Género (Punto 4.b)", h2_style))

    datos_tabla_genero = [
        [Paragraph("Género", table_header_style), Paragraph("Clientes", table_header_style), Paragraph("% Base", table_header_style), Paragraph("Facturación ($)", table_header_style), Paragraph("% Fact.", table_header_style), Paragraph("Ticket Prom.", table_header_style), Paragraph("LTV Prom.", table_header_style), Paragraph("Tiempo (s)", table_header_style)],
        [Paragraph("Masculino (0)", table_cell_left), Paragraph("3,372", table_cell_style), Paragraph("51.88%", table_cell_style), Paragraph("$133,861.26", table_cell_style), Paragraph("51.76%", table_cell_style), Paragraph("$39.70", table_cell_style), Paragraph("$204.46", table_cell_style), Paragraph("765.89 s", table_cell_style)],
        [Paragraph("Femenino (1)", table_cell_left), Paragraph("3,128", table_cell_style), Paragraph("48.12%", table_cell_style), Paragraph("$124,754.61", table_cell_style), Paragraph("48.24%", table_cell_style), Paragraph("$39.88", table_cell_style), Paragraph("$208.16", table_cell_style), Paragraph("768.98 s", table_cell_style)],
    ]
    t_gen = Table(datos_tabla_genero, colWidths=[1.6*inch, 0.8*inch, 0.8*inch, 1.2*inch, 0.8*inch, 0.9*inch, 0.9*inch, 0.9*inch])
    t_gen.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a365d")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
    ]))
    elementos.append(t_gen)
    elementos.append(Spacer(1, 4))

    # Grafica 2
    g2_path = GRAFICAS_DIR / "02_segmentacion_genero_comportamiento.png"
    if g2_path.exists():
        elementos.append(Image(str(g2_path), width=6.6*inch, height=2.2*inch))
        elementos.append(Spacer(1, 4))

    elementos.append(Paragraph(
        "<b>Inferencia Estadística:</b> La prueba <i>t de Welch</i> (<i>t = -0.3818, p = 0.7026</i>) y la prueba no paramétrica <i>U de Mann-Whitney</i> (<i>U = 5,271,528.0, p = 0.9759</i>) "
        "demuestran que no existe diferencia significativa entre géneros. La clientela presenta paridad en ticket ($39.70 vs $39.88) y valor de vida acumulado ($204.46 vs $208.16).",
        body_style
    ))

    # 2.3 Fidelizacion (Boletin y Vales)
    elementos.append(Paragraph("2.3 Segmentación en 4 Cuadrantes: Boletín y Vales Promocionales (Punto 4.c)", h2_style))

    datos_tabla_promo = [
        [Paragraph("Cuadrante Promocional", table_header_style), Paragraph("Transacciones", table_header_style), Paragraph("% Trans.", table_header_style), Paragraph("Facturación ($)", table_header_style), Paragraph("% Fact.", table_header_style), Paragraph("Ticket Prom.", table_header_style), Paragraph("Mediana ($)", table_header_style)],
        [Paragraph("1. Ambos (Boletín + Vale)", table_cell_left), Paragraph("811", table_cell_style), Paragraph("12.48%", table_cell_style), Paragraph("$37,047.64", table_cell_style), Paragraph("14.33%", table_cell_style), Paragraph("<b>$45.68</b>", table_cell_style), Paragraph("$41.48", table_cell_style)],
        [Paragraph("2. Solo Vale", table_cell_left), Paragraph("443", table_cell_style), Paragraph("6.82%", table_cell_style), Paragraph("$19,323.17", table_cell_style), Paragraph("7.47%", table_cell_style), Paragraph("<b>$43.62</b>", table_cell_style), Paragraph("$39.76", table_cell_style)],
        [Paragraph("3. Solo Boletín", table_cell_left), Paragraph("2,110", table_cell_style), Paragraph("32.46%", table_cell_style), Paragraph("$82,246.25", table_cell_style), Paragraph("31.80%", table_cell_style), Paragraph("$38.98", table_cell_style), Paragraph("$35.10", table_cell_style)],
        [Paragraph("4. Ninguno (Orgánico)", table_cell_left), Paragraph("3,136", table_cell_style), Paragraph("48.25%", table_cell_style), Paragraph("$119,998.80", table_cell_style), Paragraph("46.40%", table_cell_style), Paragraph("$38.26", table_cell_style), Paragraph("$34.58", table_cell_style)],
    ]
    t_promo = Table(datos_tabla_promo, colWidths=[2.2*inch, 0.9*inch, 0.8*inch, 1.2*inch, 0.7*inch, 1.0*inch, 1.0*inch])
    t_promo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a365d")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
    ]))
    elementos.append(t_promo)
    elementos.append(Spacer(1, 4))

    # Grafica 3
    g3_path = GRAFICAS_DIR / "03_segmentacion_boletin_vales_cuadrantes.png"
    if g3_path.exists():
        elementos.append(Image(str(g3_path), width=6.6*inch, height=2.2*inch))
        elementos.append(Spacer(1, 4))

    elementos.append(Paragraph(
        "<b>Impacto Económico del Vale:</b> La prueba ANOVA multigrupo (<i>F = 38.5465, p = 1.1054e-24</i>) demuestra una diferencia altamente significativa. "
        "El uso de vales eleva el ticket promedio en un <b>+19.4%</b> con boletín ($45.68) y un <b>+14.0%</b> sin boletín ($43.62) frente a las compras orgánicas ($38.26).",
        body_style
    ))

    # =========================================================================
    # SECCION 3: ANALISIS DE CORRELACIONES Y PRUEBAS ESTADISTICAS (PUNTO 5)
    # =========================================================================
    elementos.append(Paragraph("3. ANÁLISIS DE CORRELACIONES Y PRUEBAS ESTADÍSTICAS (PUNTO 5)", h1_style))

    # 3.1 Edad vs Venta
    elementos.append(Paragraph("3.1 Correlación entre Edad del Cliente y Venta Total (Punto 5.a)", h2_style))

    # Grafica 4
    g4_path = GRAFICAS_DIR / "04_scatter_edad_vs_venta_total_regresion.png"
    if g4_path.exists():
        elementos.append(Image(str(g4_path), width=6.6*inch, height=2.3*inch))
        elementos.append(Spacer(1, 4))

    elementos.append(Paragraph(
        "<b>Parámetros Calculados (N=6,500):</b> Coeficiente de Pearson <i>r = -0.0252</i> (<i>p = 0.0419</i>), Spearman <i>ρ = -0.0298</i> (<i>p = 0.0162</i>), "
        "Recta OLS: <i>Venta_Total = -0.4787 * Edad + 223.62</i>, con <i>R² = 0.000637</i>. "
        "<b>Conclusión:</b> La edad no determina el gasto acumulado (explica menos del 0.07% de la varianza); el consumo es transversal a todas las generaciones.",
        body_style
    ))

    # 3.2 Genero vs Metodo Pago
    elementos.append(Paragraph("3.2 Influencia del Género en el Método de Pago Preferido (Punto 5.b)", h2_style))

    # Grafica 5
    g5_path = GRAFICAS_DIR / "05_heatmap_genero_vs_metodo_pago.png"
    if g5_path.exists():
        elementos.append(Image(str(g5_path), width=6.6*inch, height=2.2*inch))
        elementos.append(Spacer(1, 4))

    elementos.append(Paragraph(
        "<b>Resultados Chi-cuadrado:</b> Estadístico <i>χ² = 3.7338</i>, grados de libertad <i>dof = 2</i>, valor <i>p = 0.1546</i>, V de Cramér <i>V = 0.0240</i>. "
        "Dado que <i>p > 0.05</i>, se concluye que <b>el género y el método de pago son estadísticamente independientes</b>. Ambos sexos eligen mayoritariamente Tarjeta de Crédito (~58-60%).",
        body_style
    ))

    # 3.3 Boletin vs Vales
    elementos.append(Paragraph("3.3 Correlación entre Suscripción al Boletín y Uso de Vales (Punto 5.c)", h2_style))
    elementos.append(Paragraph(
        "- <b>Tasa de Redención de Vales:</b> 27.76% en clientes suscritos al boletín (811 de 2,921) vs. 12.38% en clientes no suscritos (443 de 3,579).<br/>"
        "- <b>Coeficiente Phi (Φ):</b> <i>+0.1940</i> (<i>p = 3.93e-56</i>) | <b>Chi-cuadrado (Yates):</b> <i>χ² = 243.57</i> (<i>p = 6.57e-55</i>).<br/>"
        "- <b>Odds Ratio (Razón de Momios):</b> <b>2.7209</b>. Un cliente suscrito al boletín tiene <b>2.72 veces más probabilidades</b> de utilizar un vale de descuento frente a uno no suscrito.",
        body_style
    ))

    # Grafica 6 y 7
    g6_path = GRAFICAS_DIR / "06_heatmap_matriz_correlacion_multivariable.png"
    if g6_path.exists():
        elementos.append(Image(str(g6_path), width=6.6*inch, height=2.7*inch))
        elementos.append(Spacer(1, 4))

    g7_path = GRAFICAS_DIR / "07_boxplot_monto_compra_por_fidelizacion.png"
    if g7_path.exists():
        elementos.append(Image(str(g7_path), width=6.6*inch, height=2.3*inch))
        elementos.append(Spacer(1, 4))

    # =========================================================================
    # SECCION 4: CONCLUSIONES Y RECOMENDACIONES (PUNTOS 7 Y 8)
    # =========================================================================
    elementos.append(Paragraph("4. CONCLUSIONES CLAVE Y RECOMENDACIONES ESTRATÉGICAS", h1_style))

    elementos.append(Paragraph("4.1 Conclusiones Clave del Análisis de Segmentación y Correlaciones", h2_style))
    elementos.append(Paragraph(
        "1. <b>Concentración del Ingreso en la Cohorte de 26 a 40 Años (Millennials):</b> "
        "El análisis demográfico evidenció que más del 52.8% de la facturación global anual ($136,547.45 USD) es generada por clientes entre 26 y 40 años. "
        "Si bien el ticket promedio unitario se mantiene uniforme en ~$40 a lo largo de todas las edades (ANOVA p = 0.4193), la densidad y masa transaccional "
        "de este grupo lo convierte en el pilar crítico de ingresos. Cualquier estrategia de expansión hacia la sucursal física debe priorizar productos y experiencias adaptadas a este segmento.",
        body_style
    ))
    elementos.append(Paragraph(
        "2. <b>Homogeneidad de Comportamiento Comercial entre Géneros:</b> "
        "La evaluación cuantitativa entre hombres (51.88% de la base) y mujeres (48.12%) demostró paridad estadística absoluta en volumen de facturación ($133.9k vs $124.8k), "
        "ticket promedio ($39.70 vs $39.88, prueba t p = 0.7026), valor acumulado del cliente ($204.46 vs $208.16) y preferencias de medios de pago (Chi² p = 0.1546). "
        "Esto valida que el catálogo de productos y la propuesta comercial de la empresa poseen un atractivo universal y neutral sin sesgos de género.",
        body_style
    ))
    elementos.append(Paragraph(
        "3. <b>Poder de Expansión del Ticket mediante Vales Promocionales:</b> "
        "El uso de vales de descuento demostró ser la palanca de mayor impacto estadísticamente comprobado sobre el monto de compra (ANOVA F = 38.55, p = 1.10e-24). "
        "Los clientes que redimen vales incrementan su ticket promedio a $45.68 (con boletín) y $43.62 (sin boletín), lo que representa un aumento de hasta un +19.4% "
        "en comparación con el cliente orgánico ($38.26). El vale no actúa como un mero descuento erosivo de margen, sino como un acelerador del volumen de la canasta de compra.",
        body_style
    ))
    elementos.append(Paragraph(
        "4. <b>Sinergia Exponencial entre Boletín Informativo y Redención de Vales:</b> "
        "Se confirmó una relación de asociación altamente significativa (Phi = +0.1940, Chi² = 243.57, p < 10^-50) y un Odds Ratio de 2.72. "
        "Los suscriptores del boletín tienen casi el triple de propensión a canjear vales frente a los no suscritos. El boletín funge como un canal de distribución "
        "estratégico que monetiza de forma efectiva las campañas comerciales dirigidas.",
        body_style
    ))

    elementos.append(Paragraph("4.2 Acciones Concretas Propuestas (Estudiante 4)", h2_style))
    elementos.append(Paragraph(
        "1. <b>Campaña de Captación de Boletín con Vale de Bienvenida para el Segmento 26-40:</b> "
        "Diseñar un flujo automatizado de onboarding digital y en la nueva sucursal física que ofrezca un vale del 10% de descuento en la siguiente compra "
        "a cambio de la suscripción al boletín. Dado que los suscriptores tienen un Odds Ratio de 2.72 y un ticket medio superior ($45.68), la estrategia maximizará el LTV corporativo.",
        body_style
    ))
    elementos.append(Paragraph(
        "2. <b>Alianzas con Emisores de Tarjetas de Crédito y Checkout Físico Omnicanal:</b> "
        "Al constatar que casi el 60% de los clientes de ambos géneros utiliza tarjeta de crédito, se recomienda negociar acuerdos con procesadores de pago "
        "para ofrecer cuotas sin recargo y terminales de cobro contactless unificadas tanto en la tienda física como en la web, reduciendo la fricción de pago.",
        body_style
    ))

    elementos.append(Paragraph("4.3 Respuestas a Preguntas Estratégicas (Punto 8 del Alcance)", h2_style))
    elementos.append(Paragraph(
        "<b>a. Diferenciación de la Competencia:</b> La hiper-personalización de promociones basadas en cuadrantes de fidelización permite ofrecer vales condicionados a umbrales de compra mínima ($50+), maximizando el margen frente a competidores con descuentos genéricos.<br/>"
        "<b>b. Decisiones Estratégicas:</b> Unificar el sistema de fidelización entre el canal online y la nueva tienda física para que los vales emitidos por boletín sean canjeables en ambos entornos.<br/>"
        "<b>c. Ahorro de Costos y Eficiencia:</b> Reducir gastos en campañas masivas no segmentadas por género y enfocar el presupuesto en retención por email marketing a la cohorte de 26-40 años.<br/>"
        "<b>d. Datos Adicionales Futuros:</b> Integrar categorías de producto (SKUs), margen bruto por producto, canal de adquisición publicitaria (CAC) y tasa de retorno/devoluciones.<br/>"
        "<b>e. Impacto del Chat Conversacional de IA:</b> La integración de IA conversacional y servidores FastMCP permitirá al comité directivo consultar en tiempo real métricas de correlación y segmentación de clientes en lenguaje natural sin demoras de reportería tradicional.",
        body_style
    ))

    # Construir documento
    doc.build(elementos)
    print(f"-> Documento PDF generado exitosamente en: {PDF_PATH}")


if __name__ == "__main__":
    construir_pdf()
