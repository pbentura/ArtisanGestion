"""
Générateur de PDF côté serveur pour les factures ArtisanGestion.

Utilise ReportLab pour produire un PDF de haute qualité,
répliquant le design du frontend pour une cohérence visuelle.
"""

from io import BytesIO
from decimal import Decimal
from typing import Any, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER


# ── Couleurs du thème (alignées sur le design frontend) ─────────────
COLOR_DARK = colors.HexColor("#0f172a")
COLOR_TEXT = colors.HexColor("#1f2937")
COLOR_MUTED = colors.HexColor("#475569")
COLOR_LIGHT_MUTED = colors.HexColor("#64748b")
COLOR_GRAY = colors.HexColor("#6b7280")
COLOR_PRIMARY = colors.HexColor("#2563eb")
COLOR_BORDER = colors.HexColor("#e2e8f0")
COLOR_BG_LIGHT = colors.HexColor("#f8fafc")
COLOR_HEADER_BORDER = colors.HexColor("#cbd5e1")


def _format_date(d: Any) -> str:
    """Formate une date en format français DD/MM/YYYY."""
    if d is None:
        return "-"
    if hasattr(d, "strftime"):
        return d.strftime("%d/%m/%Y")
    return str(d)


def _decimal_fmt(value: Any) -> str:
    """Formate un nombre décimal avec 2 décimales."""
    return str(Decimal(str(value)).quantize(Decimal("0.01")))


def generate_invoice_pdf(
    facture: Any,
    client: Any,
    societe: Any,
    lignes: List[Any],
) -> bytes:
    """
    Génère un PDF de facture côté serveur avec ReportLab.

    Args:
        facture: Objet Facture
        client: Objet Client
        societe: Objet Societe
        lignes: Liste des LigneFacture

    Returns:
        bytes: Le contenu PDF
    """
    buffer = BytesIO()

    # Pied de page société
    texte_pied = getattr(societe, "texte_pied_page", None) or ""
    bottom_margin = 25 * mm if texte_pied else 15 * mm

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=25 * mm,
        rightMargin=25 * mm,
        topMargin=25 * mm,
        bottomMargin=bottom_margin + 10 * mm,
        title=f"{getattr(facture, 'titre_document_pdf', 'FACTURE')} {facture.numero_facture}",
        author=getattr(societe, "nom", "ArtisanGestion"),
    )

    # Styles
    styles = getSampleStyleSheet()

    style_normal = ParagraphStyle(
        "CustomNormal", parent=styles["Normal"],
        fontName="Helvetica", fontSize=9, textColor=COLOR_TEXT, leading=13,
    )
    style_bold = ParagraphStyle(
        "CustomBold", parent=style_normal,
        fontName="Helvetica-Bold",
    )
    style_small = ParagraphStyle(
        "CustomSmall", parent=style_normal,
        fontSize=8, textColor=COLOR_GRAY, leading=11,
    )
    style_small_muted = ParagraphStyle(
        "CustomSmallMuted", parent=style_normal,
        fontSize=7.5, textColor=COLOR_LIGHT_MUTED, leading=10,
    )
    style_title = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=18, textColor=COLOR_DARK,
        spaceAfter=2 * mm, leading=22,
    )
    style_subtitle = ParagraphStyle(
        "CustomSubtitle", parent=style_normal,
        fontName="Helvetica-Bold", fontSize=10, textColor=COLOR_MUTED,
    )
    style_right = ParagraphStyle(
        "CustomRight", parent=style_normal,
        alignment=TA_RIGHT,
    )
    style_right_bold = ParagraphStyle(
        "CustomRightBold", parent=style_right,
        fontName="Helvetica-Bold",
    )
    style_label = ParagraphStyle(
        "CustomLabel", parent=style_normal,
        fontName="Helvetica-Bold", fontSize=7, textColor=COLOR_LIGHT_MUTED,
        leading=9,
    )
    style_value = ParagraphStyle(
        "CustomValue", parent=style_normal,
        fontName="Helvetica-Bold", fontSize=9, textColor=COLOR_DARK,
    )

    elements = []

    # ── EN-TÊTE : Société + Client ──────────────────────────────────
    adresse_societe_parts = [
        getattr(societe, "adresse", None),
        getattr(societe, "code_postal", None),
        getattr(societe, "ville", None),
    ]
    adresse_societe = " ".join(p for p in adresse_societe_parts if p)

    # Bloc société
    societe_content = []
    societe_content.append(
        Paragraph(f"<b>{societe.nom}</b>", ParagraphStyle(
            "SocieteName", parent=style_normal,
            fontName="Helvetica-Bold", fontSize=14, textColor=COLOR_PRIMARY, leading=18,
        ))
    )
    societe_content.append(Spacer(1, 2 * mm))
    societe_content.append(Paragraph(f"<b>{societe.nom}</b>", style_bold))
    societe_content.append(Paragraph(adresse_societe, style_small))
    societe_content.append(Paragraph(
        f"Tél: {getattr(societe, 'telephone', '-') or '-'}", style_small
    ))
    societe_content.append(Paragraph(
        f"Email: {getattr(societe, 'email', '-') or '-'}", style_small
    ))
    if getattr(societe, "siret", None):
        societe_content.append(Paragraph(f"SIRET: {societe.siret}", style_small_muted))

    # Bloc client
    adresse_client_ville = " ".join(
        p for p in [
            getattr(client, "code_postal", None),
            getattr(client, "ville", None),
        ] if p
    )

    client_content = []
    client_content.append(Paragraph("FACTURÉ À", ParagraphStyle(
        "ClientLabel", parent=style_normal,
        fontName="Helvetica-Bold", fontSize=7, textColor=COLOR_LIGHT_MUTED, leading=9,
    )))
    client_content.append(Spacer(1, 1 * mm))
    client_content.append(Paragraph(
        f"<b>{client.nom}</b>",
        ParagraphStyle("ClientName", parent=style_normal,
                       fontName="Helvetica-Bold", fontSize=10, textColor=COLOR_DARK)
    ))
    client_content.append(Spacer(1, 1 * mm))
    client_content.append(Paragraph(
        f"{getattr(client, 'adresse', '') or ''}<br/>{adresse_client_ville}",
        ParagraphStyle("ClientAddr", parent=style_normal, fontSize=8, textColor=COLOR_MUTED)
    ))
    if getattr(client, "siret", None):
        client_content.append(Paragraph(f"SIRET: {client.siret}", style_small_muted))
    if getattr(client, "telephone", None):
        client_content.append(Paragraph(f"Tél: {client.telephone}", style_small))

    # Tableau d'en-tête avec les 2 blocs
    header_table = Table(
        [[societe_content, client_content]],
        colWidths=[doc.width * 0.55, doc.width * 0.45],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (-1, -1), (-1, -1), 0),
        # Fond gris clair pour le bloc client
        ("BACKGROUND", (1, 0), (1, 0), COLOR_BG_LIGHT),
        ("BOX", (1, 0), (1, 0), 0.5, COLOR_BORDER),
        ("TOPPADDING", (1, 0), (1, 0), 8),
        ("BOTTOMPADDING", (1, 0), (1, 0), 8),
        ("LEFTPADDING", (1, 0), (1, 0), 10),
        ("RIGHTPADDING", (1, 0), (1, 0), 10),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8 * mm))

    # ── TITRE FACTURE + INFOS ───────────────────────────────────────
    titre = getattr(facture, "titre_document_pdf", "FACTURE")

    titre_left = []
    titre_left.append(Paragraph(titre, style_title))
    if facture.objet_facture:
        titre_left.append(Paragraph(
            f"Objet : {facture.objet_facture}", style_subtitle
        ))

    titre_right = []
    titre_right.append(Paragraph("RÉFÉRENCE", style_label))
    titre_right.append(Paragraph(facture.numero_facture, style_value))
    titre_right.append(Spacer(1, 2 * mm))
    titre_right.append(Paragraph("DATE", style_label))
    titre_right.append(Paragraph(_format_date(facture.date_facture), style_value))

    titre_table = Table(
        [[titre_left, titre_right]],
        colWidths=[doc.width * 0.6, doc.width * 0.4],
    )
    titre_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (-1, -1), (-1, -1), 0),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    elements.append(titre_table)

    # Ligne séparatrice
    elements.append(Spacer(1, 3 * mm))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_BORDER))
    elements.append(Spacer(1, 6 * mm))

    # ── TABLEAU DES LIGNES ──────────────────────────────────────────
    style_cell = ParagraphStyle(
        "CellStyle", parent=style_normal, fontSize=8, leading=11,
    )
    style_cell_right = ParagraphStyle(
        "CellRightStyle", parent=style_cell, alignment=TA_RIGHT,
    )
    style_header_cell = ParagraphStyle(
        "HeaderCell", parent=style_normal,
        fontName="Helvetica-Bold", fontSize=8, textColor=colors.HexColor("#334155"), leading=11,
    )
    style_header_right = ParagraphStyle(
        "HeaderRight", parent=style_header_cell, alignment=TA_RIGHT,
    )

    table_data = [[
        Paragraph("Description", style_header_cell),
        Paragraph("Qté", style_header_right),
        Paragraph("Prix U. HT", style_header_right),
        Paragraph("TVA", style_header_right),
        Paragraph("Total HT", style_header_right),
    ]]

    for ligne in lignes:
        prix_ht = _decimal_fmt(ligne.prix_unite_ht)
        total_ht = _decimal_fmt(ligne.total_ht)
        quantite = _decimal_fmt(ligne.quantite)
        taux = _decimal_fmt(ligne.taux_tva)

        table_data.append([
            Paragraph(str(ligne.description), style_cell),
            Paragraph(quantite, style_cell_right),
            Paragraph(f"{prix_ht} €", style_cell_right),
            Paragraph(f"{taux}%", style_cell_right),
            Paragraph(f"{total_ht} €", style_cell_right),
        ])

    col_widths = [doc.width * 0.45, doc.width * 0.1, doc.width * 0.15,
                  doc.width * 0.1, doc.width * 0.2]

    line_table = Table(table_data, colWidths=col_widths)

    line_table_style = [
        # En-tête
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_BG_LIGHT),
        ("LINEBELOW", (0, 0), (-1, 0), 1.5, COLOR_HEADER_BORDER),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        # Lignes
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    line_table.setStyle(TableStyle(line_table_style))
    elements.append(line_table)
    elements.append(Spacer(1, 8 * mm))

    # ── ENCART DES TOTAUX ───────────────────────────────────────────
    sous_total = _decimal_fmt(facture.sous_total_ht)
    total_tva = _decimal_fmt(facture.total_tva)
    total_ttc = _decimal_fmt(facture.total_ttc)

    style_totaux_label = ParagraphStyle(
        "TotauxLabel", parent=style_normal,
        fontName="Helvetica-Bold", fontSize=9, textColor=COLOR_MUTED,
    )
    style_totaux_value = ParagraphStyle(
        "TotauxValue", parent=style_normal,
        fontName="Helvetica-Bold", fontSize=9, textColor=COLOR_TEXT, alignment=TA_RIGHT,
    )
    style_total_final_label = ParagraphStyle(
        "TotalFinalLabel", parent=style_normal,
        fontName="Helvetica-Bold", fontSize=11, textColor=COLOR_DARK,
    )
    style_total_final_value = ParagraphStyle(
        "TotalFinalValue", parent=style_normal,
        fontName="Helvetica-Bold", fontSize=11, textColor=COLOR_PRIMARY, alignment=TA_RIGHT,
    )

    totaux_data = [
        [Paragraph("Total HT", style_totaux_label),
         Paragraph(f"{sous_total} €", style_totaux_value)],
        [Paragraph("Total TVA", style_totaux_label),
         Paragraph(f"{total_tva} €", style_totaux_value)],
        [Paragraph("Net à Payer (TTC)", style_total_final_label),
         Paragraph(f"{total_ttc} €", style_total_final_value)],
    ]

    totaux_width = 70 * mm
    totaux_table = Table(totaux_data, colWidths=[totaux_width * 0.55, totaux_width * 0.45])
    totaux_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), COLOR_BG_LIGHT),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        # Ligne au dessus du TTC
        ("LINEABOVE", (0, 2), (-1, 2), 0.5, COLOR_HEADER_BORDER),
        ("TOPPADDING", (0, 2), (-1, 2), 6),
        ("BOTTOMPADDING", (0, 2), (-1, 2), 6),
        ("BOX", (0, 0), (-1, -1), 0, COLOR_BG_LIGHT),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))

    # Aligner le tableau des totaux à droite
    wrapper = Table([[totaux_table]], colWidths=[doc.width])
    wrapper.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    elements.append(wrapper)
    elements.append(Spacer(1, 10 * mm))

    # ── CONDITIONS & ÉCHÉANCE ───────────────────────────────────────
    if facture.conditions_particulieres:
        elements.append(Paragraph(
            "<b>Conditions particulières et informations :</b>",
            ParagraphStyle("CondLabel", parent=style_normal,
                           fontName="Helvetica-Bold", fontSize=8, textColor=COLOR_DARK)
        ))
        elements.append(Spacer(1, 1 * mm))
        elements.append(Paragraph(
            facture.conditions_particulieres.replace("\n", "<br/>"),
            ParagraphStyle("CondText", parent=style_normal,
                           fontSize=7.5, textColor=COLOR_MUTED, leading=10)
        ))
        elements.append(Spacer(1, 3 * mm))

    if facture.date_echeance:
        nb_jours = getattr(facture, "nb_jours_echeance", 30)
        elements.append(Paragraph(
            f"<b>Date d'échéance : {_format_date(facture.date_echeance)} ({nb_jours} jours)</b>",
            ParagraphStyle("Echeance", parent=style_normal,
                           fontName="Helvetica-Bold", fontSize=7.5, textColor=COLOR_MUTED)
        ))

    # ── Pied de page ────────────────────────────────────────────────
    def footer_callback(canvas, doc_ref):
        page_width, page_height = A4
        canvas.saveState()
        
        # 1. Ligne de séparation élégante (Bleu Primaire)
        canvas.setStrokeColor(COLOR_PRIMARY)
        canvas.setLineWidth(1)
        canvas.setStrokeAlpha(0.6)
        canvas.line(15 * mm, 20 * mm, page_width - 15 * mm, 20 * mm)
        canvas.setStrokeAlpha(1.0)

        # 2. Informations société (Centrées)
        if texte_pied:
            canvas.setFont("Helvetica", 7)
            canvas.setFillColor(COLOR_GRAY)
            text_lines = texte_pied.strip().split("\n")
            y = 15 * mm
            for line in reversed(text_lines):
                canvas.drawCentredString(page_width / 2, y, line.strip())
                y += 3.5 * mm

        # 3. Numérotation de page (Bas Droite)
        page_num = canvas.getPageNumber()
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(COLOR_PRIMARY)
        canvas.drawRightString(page_width - 15 * mm, 10 * mm, f"Page {page_num}")

        # 4. Petit branding (Bas Gauche - optionnel mais pro)
        canvas.setFont("Helvetica-Oblique", 6)
        canvas.setFillColor(COLOR_LIGHT_MUTED)
        canvas.drawString(15 * mm, 10 * mm, "Généré via ArtisanGestion")

        canvas.restoreState()

    doc.build(elements, onFirstPage=footer_callback, onLaterPages=footer_callback)

    return buffer.getvalue()


def generate_rapport_pdf(
    rapport: Any,
    client: Any,
    societe: Any,
) -> bytes:
    """
    Génère un PDF de rapport côté serveur avec ReportLab.
    """
    buffer = BytesIO()

    texte_pied = getattr(societe, "texte_pied_page", None) or ""
    bottom_margin = 25 * mm if texte_pied else 15 * mm

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=25 * mm,
        rightMargin=25 * mm,
        topMargin=25 * mm,
        bottomMargin=bottom_margin + 10 * mm,
        title=getattr(rapport, "titre_document_pdf", "RAPPORT"),
        author=getattr(societe, "nom", "ArtisanGestion"),
    )

    styles = getSampleStyleSheet()

    style_normal = ParagraphStyle(
        "CustomNormal", parent=styles["Normal"],
        fontName="Helvetica", fontSize=9, textColor=COLOR_TEXT, leading=13,
    )
    style_bold = ParagraphStyle(
        "CustomBold", parent=style_normal,
        fontName="Helvetica-Bold",
    )
    style_small = ParagraphStyle(
        "CustomSmall", parent=style_normal,
        fontSize=8, textColor=COLOR_GRAY, leading=11,
    )
    style_small_muted = ParagraphStyle(
        "CustomSmallMuted", parent=style_normal,
        fontSize=7.5, textColor=COLOR_LIGHT_MUTED, leading=10,
    )
    style_title = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=18, textColor=COLOR_DARK,
        spaceAfter=2 * mm, leading=22,
    )
    style_label = ParagraphStyle(
        "CustomLabel", parent=style_normal,
        fontName="Helvetica-Bold", fontSize=7, textColor=COLOR_LIGHT_MUTED,
        leading=9,
    )
    style_value = ParagraphStyle(
        "CustomValue", parent=style_normal,
        fontName="Helvetica-Bold", fontSize=9, textColor=COLOR_DARK,
    )

    elements = []

    # ── EN-TÊTE : Société + Client ──────────────────────────────────
    adresse_societe_parts = [
        getattr(societe, "adresse", None),
        getattr(societe, "code_postal", None),
        getattr(societe, "ville", None),
    ]
    adresse_societe = " ".join(p for p in adresse_societe_parts if p)

    societe_content = []
    societe_content.append(
        Paragraph(f"<b>{societe.nom}</b>", ParagraphStyle(
            "SocieteName", parent=style_normal,
            fontName="Helvetica-Bold", fontSize=14, textColor=COLOR_PRIMARY, leading=18,
        ))
    )
    societe_content.append(Spacer(1, 2 * mm))
    societe_content.append(Paragraph(f"<b>{societe.nom}</b>", style_bold))
    societe_content.append(Paragraph(adresse_societe, style_small))
    societe_content.append(Paragraph(
        f"Tél: {getattr(societe, 'telephone', '-') or '-'}", style_small
    ))
    societe_content.append(Paragraph(
        f"Email: {getattr(societe, 'email', '-') or '-'}", style_small
    ))
    if getattr(societe, "siret", None):
        societe_content.append(Paragraph(f"SIRET: {societe.siret}", style_small_muted))

    client_content = []
    if client:
        adresse_client_ville = " ".join(
            p for p in [
                getattr(client, "code_postal", None),
                getattr(client, "ville", None),
            ] if p
        )
        client_content.append(Paragraph("CLIENT", ParagraphStyle(
            "ClientLabel", parent=style_normal,
            fontName="Helvetica-Bold", fontSize=7, textColor=COLOR_LIGHT_MUTED, leading=9,
        )))
        client_content.append(Spacer(1, 1 * mm))
        client_content.append(Paragraph(
            f"<b>{client.nom}</b>",
            ParagraphStyle("ClientName", parent=style_normal,
                           fontName="Helvetica-Bold", fontSize=10, textColor=COLOR_DARK)
        ))
        client_content.append(Spacer(1, 1 * mm))
        client_content.append(Paragraph(
            f"{getattr(client, 'adresse', '') or ''}<br/>{adresse_client_ville}",
            ParagraphStyle("ClientAddr", parent=style_normal, fontSize=8, textColor=COLOR_MUTED)
        ))
        if getattr(client, "siret", None):
            client_content.append(Paragraph(f"SIRET: {client.siret}", style_small_muted))
        if getattr(client, "telephone", None):
            client_content.append(Paragraph(f"Tél: {client.telephone}", style_small))

    header_table = Table(
        [[societe_content, client_content]],
        colWidths=[doc.width * 0.55, doc.width * 0.45],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (-1, -1), (-1, -1), 0),
        ("BACKGROUND", (1, 0), (1, 0), COLOR_BG_LIGHT),
        ("BOX", (1, 0), (1, 0), 0.5, COLOR_BORDER),
        ("TOPPADDING", (1, 0), (1, 0), 8),
        ("BOTTOMPADDING", (1, 0), (1, 0), 8),
        ("LEFTPADDING", (1, 0), (1, 0), 10),
        ("RIGHTPADDING", (1, 0), (1, 0), 10),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8 * mm))

    # ── TITRE RAPPORT + INFOS ───────────────────────────────────────
    titre = getattr(rapport, "titre_document_pdf", "RAPPORT")

    titre_left = []
    titre_left.append(Paragraph(titre, style_title))

    titre_right = []
    titre_right.append(Paragraph("DATE D'INTERVENTION", style_label))
    titre_right.append(Paragraph(_format_date(rapport.date_intervention), style_value))

    titre_table = Table(
        [[titre_left, titre_right]],
        colWidths=[doc.width * 0.6, doc.width * 0.4],
    )
    titre_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (-1, -1), (-1, -1), 0),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))
    elements.append(titre_table)
    elements.append(Spacer(1, 3 * mm))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_BORDER))
    elements.append(Spacer(1, 6 * mm))

    # ── CONTENU DU RAPPORT ──────────────────────────────────────────
    if rapport.contenu:
        # Remplacer les retours à la ligne par des balises <br/> pour ReportLab
        contenu_formate = str(rapport.contenu).replace('\n', '<br/>')
        elements.append(Paragraph(
            contenu_formate,
            ParagraphStyle("ContenuText", parent=style_normal,
                           fontSize=10, textColor=COLOR_TEXT, leading=15)
        ))
        elements.append(Spacer(1, 10 * mm))

    # ── Pied de page ────────────────────────────────────────────────
    def footer_callback(canvas, doc_ref):
        page_width, page_height = A4
        canvas.saveState()
        canvas.setStrokeColor(COLOR_PRIMARY)
        canvas.setLineWidth(1)
        canvas.setStrokeAlpha(0.6)
        canvas.line(15 * mm, 20 * mm, page_width - 15 * mm, 20 * mm)
        canvas.setStrokeAlpha(1.0)
        if texte_pied:
            canvas.setFont("Helvetica", 7)
            canvas.setFillColor(COLOR_GRAY)
            text_lines = texte_pied.strip().split("\n")
            y = 15 * mm
            for line in reversed(text_lines):
                canvas.drawCentredString(page_width / 2, y, line.strip())
                y += 3.5 * mm
        page_num = canvas.getPageNumber()
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(COLOR_PRIMARY)
        canvas.drawRightString(page_width - 15 * mm, 10 * mm, f"Page {page_num}")
        canvas.setFont("Helvetica-Oblique", 6)
        canvas.setFillColor(COLOR_LIGHT_MUTED)
        canvas.drawString(15 * mm, 10 * mm, "Généré via ArtisanGestion")
        canvas.restoreState()

    doc.build(elements, onFirstPage=footer_callback, onLaterPages=footer_callback)
    return buffer.getvalue()
