"""
Generador de Informe Tecnico en Formato PDF - Estudiante 3: EDA y Tendencias
Practica 1: Sistemas Organizacionales y Gerenciales 2 (2S2026)
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
GRAFICAS_DIR = BASE_DIR / "graficas" / "graficas_eda"
PDF_PATH = pathlib.Path(__file__).resolve().parent / "SOG2-2S26_grupo4_Estudiante3_EDA_Tendencias.pdf"


def construir_pdf():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados
    titulo_style = ParagraphStyle(
        "TituloPrincipal",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1a365d"),
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        spaceAfter=6,
    )

    subtitulo_style = ParagraphStyle(
        "SubtituloPrincipal",
        parent=styles["Normal"],
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#4a5568"),
        alignment=TA_CENTER,
        fontName="Helvetica",
        spaceAfter=15,
    )

    h1_style = ParagraphStyle(
        "SeccionH1",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1a365d"),
        fontName="Helvetica-Bold",
        spaceBefore=12,
        spaceAfter=8,
    )

    h2_style = ParagraphStyle(
        "SeccionH2",
        parent=styles["Heading3"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#2b6cb0"),
        fontName="Helvetica-Bold",
        spaceBefore=8,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "Cuerpo",
        parent=styles["Normal"],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#2d3748"),
        alignment=TA_JUSTIFY,
        fontName="Helvetica",
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "BulletCustom",
        parent=body_style,
        leftIndent=15,
        bulletIndent=5,
        spaceAfter=4,
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontSize=8,
        leading=10.5,
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

    # Encabezado del Documento
    elementos.append(Paragraph("INFORME TECNICO Y MEMORIA DE ANALISIS: EDA Y TENDENCIAS", titulo_style))
    elementos.append(Paragraph("Practica 1 - Sistemas Organizacionales y Gerenciales 2 | Grupo 4<br/>Estudiante 3: Analista EDA y Tendencias", subtitulo_style))
    elementos.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1a365d"), spaceAfter=12))

    # 1. Introduccion
    elementos.append(Paragraph("1. INTRODUCCION Y ALCANCE DEL ROL", h1_style))
    elementos.append(Paragraph(
        "El presente informe detalla los resultados, procedimientos y desafios metodologicos abordados "
        "en el rol de <b>Estudiante 3: Analista EDA y Tendencias</b>. El trabajo abarca la exploracion inicial "
        "de datos (Punto 2 del alcance), la identificacion de patrones y tendencias temporales (Punto 3 del alcance), "
        "la implementacion del modulo MCP Server (FastMCP) para exponer herramientas analiticas, y las pruebas "
        "de integracion con el Agente Conversacional de Inteligencia Artificial basado en Google ADK.",
        body_style
    ))

    # 2. Estadisticas Basicas
    elementos.append(Paragraph("2. ANALISIS EXPLORATORIO DE DATOS (PUNTO 2 DEL ALCANCE)", h1_style))
    elementos.append(Paragraph("2.1 Estadisticas Basicas de Variables Numericas (Punto 2.b)", h2_style))
    elementos.append(Paragraph(
        "Se extrajeron los 6,500 registros de clientes y ventas desde PostgreSQL en AWS RDS. "
        "A continuacion se presentan las medidas descriptivas calculadas:",
        body_style
    ))

    datos_tabla_stats = [
        [Paragraph("Variable", table_header_style),
         Paragraph("Media", table_header_style),
         Paragraph("Mediana", table_header_style),
         Paragraph("Moda", table_header_style),
         Paragraph("Desv. Std", table_header_style),
         Paragraph("Min", table_header_style),
         Paragraph("Max", table_header_style),
         Paragraph("IQR", table_header_style)],
        [Paragraph("Venta_total (Cliente)", table_cell_left), Paragraph("206.24", table_cell_style), Paragraph("137.35", table_cell_style), Paragraph("98.00", table_cell_style), Paragraph("215.55", table_cell_style), Paragraph("9.00", table_cell_style), Paragraph("3169.00", table_cell_style), Paragraph("197.50", table_cell_style)],
        [Paragraph("MontoCompra (Transaccion)", table_cell_left), Paragraph("39.79", table_cell_style), Paragraph("35.76", table_cell_style), Paragraph("37.15", table_cell_style), Paragraph("19.52", table_cell_style), Paragraph("7.24", table_cell_style), Paragraph("199.35", table_cell_style), Paragraph("22.34", table_cell_style)],
        [Paragraph("N_Compras (Cliente)", table_cell_left), Paragraph("5.09", table_cell_style), Paragraph("4.00", table_cell_style), Paragraph("2.00", table_cell_style), Paragraph("3.96", table_cell_style), Paragraph("1.00", table_cell_style), Paragraph("25.00", table_cell_style), Paragraph("5.00", table_cell_style)],
        [Paragraph("Edad (Cliente)", table_cell_left), Paragraph("36.31", table_cell_style), Paragraph("36.00", table_cell_style), Paragraph("18.00", table_cell_style), Paragraph("11.36", table_cell_style), Paragraph("18.00", table_cell_style), Paragraph("79.00", table_cell_style), Paragraph("16.00", table_cell_style)],
        [Paragraph("Tiempo Sesion (Segundos)", table_cell_left), Paragraph("767.38", table_cell_style), Paragraph("768.00", table_cell_style), Paragraph("852.00", table_cell_style), Paragraph("181.75", table_cell_style), Paragraph("180.00", table_cell_style), Paragraph("1443.00", table_cell_style), Paragraph("241.00", table_cell_style)],
    ]

    t_stats = Table(datos_tabla_stats, colWidths=[1.8*inch, 0.7*inch, 0.7*inch, 0.65*inch, 0.8*inch, 0.6*inch, 0.8*inch, 0.7*inch])
    t_stats.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a365d")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elementos.append(t_stats)
    elementos.append(Spacer(1, 8))

    # Grafica 1
    graf1_path = GRAFICAS_DIR / "01_distribucion_estadisticas_numericas.png"
    if graf1_path.exists():
        elementos.append(Image(str(graf1_path), width=6.5*inch, height=3.5*inch))
        elementos.append(Spacer(1, 8))

    # 2.2 Distribucion de Ventas
    elementos.append(Paragraph("2.2 Distribucion de Ventas por Metodo de Pago, Canal y Campanias (Punto 2.c)", h2_style))
    elementos.append(Paragraph(
        "- <b>Metodo de Pago</b>: Tarjeta de Credito lidera con 3,827 compras (58.88% de transacciones y $152,601.47), "
        "seguida de Tarjeta de Debito con 1,466 compras (22.55% y $58,548.74) y Efectivo con 1,207 compras (18.57% y $47,465.64).<br/>"
        "- <b>Canal y Navegadores</b>: La Tienda Fisica concentra el 54.20% del total ($140,332.26). Dentro de los navegadores web, "
        "el <b>Navegador 1</b> domina con 1,273 sesiones (42.76% del trafico web y $51,323.34), mientras que el <b>Navegador 4</b> "
        "es el menos usado con 197 compras (6.62% del trafico web y $8,142.10).<br/>"
        "- <b>Boletin y Vales</b>: Los usuarios suscritos a boletines muestran un ticket promedio superior ($40.84 vs $38.93). "
        "Asimismo, el uso de vales eleva el ticket promedio en un 16.6% ($44.95 vs $38.55).",
        body_style
    ))

    # Graficas 2 y 3
    graf2_path = GRAFICAS_DIR / "02_distribucion_metodo_pago.png"
    if graf2_path.exists():
        elementos.append(Image(str(graf2_path), width=6.5*inch, height=2.5*inch))
        elementos.append(Spacer(1, 8))

    # 3. Tendencias
    elementos.append(Paragraph("3. IDENTIFICACION DE TENDENCIAS (PUNTO 3 DEL ALCANCE)", h1_style))
    elementos.append(Paragraph(
        "A traves de consultas agrupadas por periodo mensual y variables de clasificacion, se identificaron los siguientes patrones clave:<br/>"
        "1. <b>Mes con Mayor Venta</b>: <b>Marzo 2021 (2021-03)</b> con <b>$22,994.34</b> facturados en 569 transacciones, "
        "seguido por <b>Diciembre 2021</b> con $22,778.09 y 577 transacciones.<br/>"
        "2. <b>Mes con Menor Venta</b>: <b>Noviembre 2021 (2021-11)</b> con <b>$19,779.24</b> en 493 transacciones, "
        "seguido por <b>Septiembre 2021</b> con $20,074.82.<br/>"
        "3. <b>Ventas en Efectivo / Contra Entrega (MetodoPago = 0)</b>: Un total acumulado de <b>$47,465.64</b> en 1,207 operaciones "
        "(18.35% de la facturacion anual y 18.57% del volumen transaccional).<br/>"
        "4. <b>Picos de Adopcion de Campanias</b>: Mayor suscripcion a boletines en Diciembre (262 usuarios) y mayor redencion "
        "de vales en Marzo (133 vales redimidos), coincidiendo exactamente con los dos meses de mayores ventas del anio.",
        body_style
    ))

    graf5_path = GRAFICAS_DIR / "05_tendencia_ventas_mensuales_2021.png"
    if graf5_path.exists():
        elementos.append(Image(str(graf5_path), width=6.5*inch, height=2.6*inch))
        elementos.append(Spacer(1, 8))

    graf7_path = GRAFICAS_DIR / "07_adopcion_mensual_boletin_vales.png"
    if graf7_path.exists():
        elementos.append(Image(str(graf7_path), width=6.5*inch, height=2.6*inch))
        elementos.append(Spacer(1, 8))

    # 4. Desafios y Soluciones
    elementos.append(Paragraph("4. DESAFIOS TECNICOS ENCONTRADOS Y RESOLUCION", h1_style))
    elementos.append(Paragraph(
        "- <b>Desafio 1 (Calculo de Mediana y Moda en SQL)</b>: PostgreSQL no cuenta con funciones nativas simples de mediana en el SELECT basico. "
        "Se resolvio empleando funciones de agregacion ordenada: <code>PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY ...)</code> y "
        "<code>MODE() WITHIN GROUP (ORDER BY ...)</code>.<br/>"
        "- <b>Desafio 2 (Ambiguedad Semantica de Canales)</b>: La columna 'navegador' contenia la Tienda Fisica (id=0) junto a los navegadores web (1-4). "
        "Se implemento una segmentacion dual en Python y SQL para no distorsionar la metrica de navegadores web.<br/>"
        "- <b>Desafio 3 (Optimizacion de Prompts y Tools MCP)</b>: Se calibraron las firmas y docstrings en <code>mcp_server/analisis/eda_tendencias.py</code> "
        "para que el LLM de Google ADK mapee de inmediato cada pregunta gerencial a la funcion exacta sin alucinaciones.",
        body_style
    ))

    # 5. Conclusiones
    elementos.append(Paragraph("5. CONCLUSIONES Y RECOMENDACIONES", h1_style))
    elementos.append(Paragraph(
        "1. <b>Impulso de Campanias en Meses Valle</b>: Implementar cupones de descuento previos a septiembre y noviembre para contrarrestar la caida de ventas.<br/>"
        "2. <b>Focalizacion en Navegador 1</b>: Garantizar la maxima optimizacion tecnica de la tienda online para Navegador 1 al concentrar el 42.76% del trafico web.<br/>"
        "3. <b>Sinergia Boletin - Vale</b>: La suscripcion a boletines genera clientes con mayor ticket promedio ($40.84 vs $38.93); se recomienda incentivar el registro mediante vales de primera compra.",
        body_style
    ))

    doc.build(elementos)
    print(f"Informe PDF generado exitosamente en: {PDF_PATH}")


if __name__ == "__main__":
    construir_pdf()
