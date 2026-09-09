"""Generación del PDF de la factura con un diseño profesional."""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models import Factura

AZUL_OSCURO = colors.HexColor("#1F3A5F")
GRIS_CLARO = colors.HexColor("#F2F4F7")
GRIS_TEXTO = colors.HexColor("#4A4A4A")


def _moneda(valor: float) -> str:
    return f"RD$ {valor:,.2f}"


def _pie_de_pagina(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRIS_TEXTO)
    canvas.drawCentredString(
        doc.pagesize[0] / 2, 1.2 * cm, f"Página {doc.page} · Generado con Generador de Facturas"
    )
    canvas.restoreState()


def generar_pdf(factura: Factura, destino: Path) -> Path:
    """Genera el PDF de `factura` en la ruta `destino` y la devuelve."""
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(destino),
        pagesize=letter,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        title=f"Factura {factura.numero}",
    )

    styles = getSampleStyleSheet()
    estilo_empresa = ParagraphStyle(
        "Empresa", parent=styles["Normal"], fontSize=10, leading=13, textColor=GRIS_TEXTO
    )
    estilo_titulo = ParagraphStyle(
        "TituloFactura",
        parent=styles["Normal"],
        fontSize=22,
        leading=26,
        textColor=AZUL_OSCURO,
        alignment=TA_RIGHT,
        fontName="Helvetica-Bold",
    )
    estilo_meta = ParagraphStyle(
        "Meta", parent=styles["Normal"], fontSize=10, leading=14, alignment=TA_RIGHT, textColor=GRIS_TEXTO
    )
    estilo_seccion = ParagraphStyle(
        "Seccion", parent=styles["Normal"], fontSize=9, textColor=colors.white, fontName="Helvetica-Bold"
    )
    estilo_cliente = ParagraphStyle(
        "Cliente", parent=styles["Normal"], fontSize=10, leading=14, textColor=GRIS_TEXTO
    )

    story = []

    # --- Encabezado: logo/empresa a la izquierda, título y meta a la derecha ---
    empresa = factura.empresa
    datos_empresa = [Paragraph(f"<b>{empresa.nombre}</b>", estilo_empresa)]
    for linea in (empresa.direccion, empresa.telefono, empresa.email, empresa.rnc and f"RNC: {empresa.rnc}"):
        if linea:
            datos_empresa.append(Paragraph(linea, estilo_empresa))

    if empresa.logo_path and Path(empresa.logo_path).is_file():
        try:
            logo = Image(empresa.logo_path, width=3.2 * cm, height=3.2 * cm)
            logo.hAlign = "LEFT"
            columna_izquierda = Table([[logo], [Spacer(1, 6)], *[[p] for p in datos_empresa]])
            columna_izquierda.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0)]))
        except Exception:
            columna_izquierda = datos_empresa
    else:
        columna_izquierda = datos_empresa

    meta_lineas = [
        Paragraph("FACTURA", estilo_titulo),
        Paragraph(f"No. {factura.numero}", estilo_meta),
        Paragraph(f"Fecha: {factura.fecha.strftime('%d/%m/%Y')}", estilo_meta),
    ]
    if factura.ncf:
        meta_lineas.append(Paragraph(f"NCF: {factura.ncf}", estilo_meta))

    encabezado = Table(
        [[columna_izquierda, meta_lineas]],
        colWidths=[10 * cm, 7.4 * cm],
    )
    encabezado.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(encabezado)
    story.append(Spacer(1, 18))

    # --- Bloque "Facturar a" ---
    cliente = factura.cliente
    datos_cliente = [Paragraph(f"<b>{cliente.nombre}</b>", estilo_cliente)]
    for linea in (cliente.direccion, cliente.telefono, cliente.rnc_cedula and f"RNC/Cédula: {cliente.rnc_cedula}"):
        if linea:
            datos_cliente.append(Paragraph(linea, estilo_cliente))

    bloque_cliente = Table(
        [[Paragraph("FACTURAR A", estilo_seccion)], *[[p] for p in datos_cliente]],
        colWidths=[9 * cm],
    )
    bloque_cliente.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), AZUL_OSCURO),
                ("BACKGROUND", (0, 1), (-1, -1), GRIS_CLARO),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("TOPPADDING", (0, 1), (-1, -1), 8),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(bloque_cliente)
    story.append(Spacer(1, 22))

    # --- Tabla de ítems ---
    encabezados = ["Descripción", "Cantidad", "Precio unitario", "Subtotal"]
    filas = [encabezados]
    for item in factura.items:
        filas.append(
            [
                item.descripcion,
                f"{item.cantidad:g}",
                _moneda(item.precio_unitario),
                _moneda(item.subtotal),
            ]
        )

    tabla_items = Table(filas, colWidths=[8 * cm, 2.8 * cm, 3.3 * cm, 3.3 * cm], repeatRows=1)
    estilo_tabla = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL_OSCURO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#DDDDDD")),
        ("LINEBELOW", (0, -1), (-1, -1), 1, AZUL_OSCURO),
    ]
    for i in range(1, len(filas)):
        if i % 2 == 0:
            estilo_tabla.append(("BACKGROUND", (0, i), (-1, i), GRIS_CLARO))
    tabla_items.setStyle(TableStyle(estilo_tabla))
    story.append(tabla_items)
    story.append(Spacer(1, 14))

    # --- Totales ---
    filas_totales = [
        ["Subtotal", _moneda(factura.subtotal)],
        [f"ITBIS ({factura.impuesto_pct:g}%)", _moneda(factura.impuesto)],
        ["TOTAL", _moneda(factura.total)],
    ]
    tabla_totales = Table(filas_totales, colWidths=[4 * cm, 3.3 * cm], hAlign="RIGHT")
    tabla_totales.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, -1), (-1, -1), 12),
                ("TEXTCOLOR", (0, -1), (-1, -1), AZUL_OSCURO),
                ("LINEABOVE", (0, -1), (-1, -1), 1, AZUL_OSCURO),
                ("TOPPADDING", (0, -1), (-1, -1), 6),
            ]
        )
    )
    story.append(tabla_totales)

    if factura.notas:
        story.append(Spacer(1, 24))
        story.append(Paragraph("<b>Notas</b>", estilo_cliente))
        story.append(Paragraph(factura.notas.replace("\n", "<br/>"), estilo_cliente))

    story.append(Spacer(1, 30))
    story.append(
        Paragraph(
            "Gracias por su preferencia.",
            ParagraphStyle("Gracias", parent=styles["Normal"], fontSize=10, alignment=TA_CENTER, textColor=GRIS_TEXTO),
        )
    )

    doc.build(story, onFirstPage=_pie_de_pagina, onLaterPages=_pie_de_pagina)
    return destino
