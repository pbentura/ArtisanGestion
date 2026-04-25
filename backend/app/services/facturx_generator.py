"""
Générateur de XML CII (Cross-Industry Invoice) conforme Factur-X EN 16931.

Ce module construit le fichier XML qui sera embarqué dans le PDF/A-3
pour créer un document Factur-X conforme au standard européen EN 16931.
"""

import xml.etree.ElementTree as ET
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict
from typing import Any, List, Optional

# Namespaces CII (Cross-Industry Invoice)
NAMESPACES = {
    "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
    "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
    "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
    "qdt": "urn:un:unece:uncefact:data:standard:QualifiedDataType:100",
}

# Enregistrer les namespaces pour qu'ils soient utilisés avec les bons préfixes
for prefix, uri in NAMESPACES.items():
    ET.register_namespace(prefix, uri)


def _ns(prefix: str, tag: str) -> str:
    """Construit un tag qualifié avec son namespace."""
    return f"{{{NAMESPACES[prefix]}}}{tag}"


def _format_date(d: date) -> str:
    """Formate une date au format CII (YYYYMMDD)."""
    return d.strftime("%Y%m%d")


def _decimal_str(value: Any, places: int = 2) -> str:
    """Convertit une valeur en chaîne décimale arrondie."""
    d = Decimal(str(value)).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)
    return str(d)


def _add_text_element(parent: ET.Element, ns_prefix: str, tag: str, text: str) -> ET.Element:
    """Ajoute un sous-élément avec du texte."""
    elem = ET.SubElement(parent, _ns(ns_prefix, tag))
    elem.text = str(text)
    return elem


def _add_amount_element(
    parent: ET.Element, ns_prefix: str, tag: str, amount: Any, currency: str = None
) -> ET.Element:
    """Ajoute un élément montant. Le currencyID n'est ajouté que si currency est spécifié."""
    elem = ET.SubElement(parent, _ns(ns_prefix, tag))
    elem.text = _decimal_str(amount)
    if currency:
        elem.set("currencyID", currency)
    return elem


def _add_quantity_element(
    parent: ET.Element, ns_prefix: str, tag: str, qty: Any, unit: str = "C62"
) -> ET.Element:
    """Ajoute un élément quantité avec attribut unitCode (C62 = unité)."""
    elem = ET.SubElement(parent, _ns(ns_prefix, tag))
    elem.text = _decimal_str(qty)
    elem.set("unitCode", unit)
    return elem


def generate_cii_xml(
    facture: Any,
    client: Any,
    societe: Any,
    lignes: List[Any],
) -> bytes:
    """
    Génère le XML CII conforme au profil Factur-X EN 16931.

    Args:
        facture: L'objet Facture (SQLAlchemy model)
        client: L'objet Client associé
        societe: L'objet Societe de l'utilisateur
        lignes: Liste des LigneFacture

    Returns:
        bytes: Le contenu XML encodé en UTF-8
    """
    # Racine du document
    root = ET.Element(_ns("rsm", "CrossIndustryInvoice"))

    # ─── 1. ExchangedDocumentContext ─────────────────────────────────
    context = ET.SubElement(root, _ns("rsm", "ExchangedDocumentContext"))

    # Profil Factur-X EN 16931
    guideline = ET.SubElement(context, _ns("ram", "GuidelineSpecifiedDocumentContextParameter"))
    _add_text_element(
        guideline, "ram", "ID",
        "urn:cen.eu:en16931:2017"
    )

    # ─── 2. ExchangedDocument ────────────────────────────────────────
    doc = ET.SubElement(root, _ns("rsm", "ExchangedDocument"))

    # ID = numéro de facture
    _add_text_element(doc, "ram", "ID", facture.numero_facture)

    # TypeCode: 380 = Facture commerciale, 381 = Avoir
    type_code = "381" if getattr(facture, "est_avoir", False) else "380"
    _add_text_element(doc, "ram", "TypeCode", type_code)

    # Date d'émission
    issue_dt = ET.SubElement(doc, _ns("ram", "IssueDateTime"))
    date_string = ET.SubElement(issue_dt, _ns("udt", "DateTimeString"))
    date_string.text = _format_date(facture.date_facture)
    date_string.set("format", "102")

    # Notes (objet de la facture)
    if facture.objet_facture:
        note = ET.SubElement(doc, _ns("ram", "IncludedNote"))
        _add_text_element(note, "ram", "Content", facture.objet_facture)

    # ─── 3. SupplyChainTradeTransaction ──────────────────────────────
    transaction = ET.SubElement(root, _ns("rsm", "SupplyChainTradeTransaction"))

    # ─── 3.1 Lignes de facture ───────────────────────────────────────
    for idx, ligne in enumerate(lignes, start=1):
        line_item = ET.SubElement(transaction, _ns("ram", "IncludedSupplyChainTradeLineItem"))

        # ID de la ligne
        assoc_doc = ET.SubElement(line_item, _ns("ram", "AssociatedDocumentLineDocument"))
        _add_text_element(assoc_doc, "ram", "LineID", str(idx))

        # Produit/Service
        product = ET.SubElement(line_item, _ns("ram", "SpecifiedTradeProduct"))
        _add_text_element(product, "ram", "Name", ligne.description or f"Ligne {idx}")

        # Agreement (prix unitaire)
        agreement = ET.SubElement(line_item, _ns("ram", "SpecifiedLineTradeAgreement"))
        net_price = ET.SubElement(agreement, _ns("ram", "NetPriceProductTradePrice"))
        _add_amount_element(net_price, "ram", "ChargeAmount", ligne.prix_unite_ht)

        # Delivery (quantité)
        delivery = ET.SubElement(line_item, _ns("ram", "SpecifiedLineTradeDelivery"))
        _add_quantity_element(delivery, "ram", "BilledQuantity", ligne.quantite)

        # Settlement (TVA de la ligne + total HT)
        settlement = ET.SubElement(line_item, _ns("ram", "SpecifiedLineTradeSettlement"))

        line_tax = ET.SubElement(settlement, _ns("ram", "ApplicableTradeTax"))
        _add_text_element(line_tax, "ram", "TypeCode", "VAT")
        _add_text_element(line_tax, "ram", "CategoryCode", _get_vat_category(ligne.taux_tva))
        _add_text_element(line_tax, "ram", "RateApplicablePercent", _decimal_str(ligne.taux_tva))

        line_summation = ET.SubElement(
            settlement, _ns("ram", "SpecifiedTradeSettlementLineMonetarySummation")
        )
        _add_amount_element(line_summation, "ram", "LineTotalAmount", ligne.total_ht)

    # ─── 3.2 ApplicableHeaderTradeAgreement (Vendeur / Acheteur) ─────
    agreement = ET.SubElement(transaction, _ns("ram", "ApplicableHeaderTradeAgreement"))

    # --- Vendeur (Société) ---
    seller = ET.SubElement(agreement, _ns("ram", "SellerTradeParty"))
    _add_text_element(seller, "ram", "Name", societe.nom)

    # SIRET vendeur
    if societe.siret:
        seller_id = ET.SubElement(seller, _ns("ram", "SpecifiedLegalOrganization"))
        id_elem = _add_text_element(seller_id, "ram", "ID", societe.siret)
        id_elem.set("schemeID", "0002")  # 0002 = SIRET (FR)

    # Adresse vendeur
    seller_addr = ET.SubElement(seller, _ns("ram", "PostalTradeAddress"))
    if societe.code_postal:
        _add_text_element(seller_addr, "ram", "PostcodeCode", societe.code_postal)
    if societe.adresse:
        _add_text_element(seller_addr, "ram", "LineOne", societe.adresse)
    if societe.ville:
        _add_text_element(seller_addr, "ram", "CityName", societe.ville)
    _add_text_element(seller_addr, "ram", "CountryID", "FR")

    # Email vendeur
    if societe.email:
        seller_contact = ET.SubElement(seller, _ns("ram", "URIUniversalCommunication"))
        uri_id = _add_text_element(seller_contact, "ram", "URIID", societe.email)
        uri_id.set("schemeID", "EM")

    # TVA intracommunautaire vendeur
    if societe.tva_intracommunautaire:
        seller_tax = ET.SubElement(seller, _ns("ram", "SpecifiedTaxRegistration"))
        tax_id = _add_text_element(seller_tax, "ram", "ID", societe.tva_intracommunautaire)
        tax_id.set("schemeID", "VA")

    # --- Acheteur (Client) ---
    buyer = ET.SubElement(agreement, _ns("ram", "BuyerTradeParty"))
    _add_text_element(buyer, "ram", "Name", client.nom)

    # SIRET acheteur
    if client.siret:
        buyer_legal = ET.SubElement(buyer, _ns("ram", "SpecifiedLegalOrganization"))
        buyer_legal_id = _add_text_element(buyer_legal, "ram", "ID", client.siret)
        buyer_legal_id.set("schemeID", "0002")

    # Adresse acheteur
    buyer_addr = ET.SubElement(buyer, _ns("ram", "PostalTradeAddress"))
    if client.code_postal:
        _add_text_element(buyer_addr, "ram", "PostcodeCode", client.code_postal)
    if client.adresse:
        _add_text_element(buyer_addr, "ram", "LineOne", client.adresse)
    if client.ville:
        _add_text_element(buyer_addr, "ram", "CityName", client.ville)
    _add_text_element(buyer_addr, "ram", "CountryID", "FR")

    # Email acheteur
    if client.email:
        buyer_contact = ET.SubElement(buyer, _ns("ram", "URIUniversalCommunication"))
        buyer_uri = _add_text_element(buyer_contact, "ram", "URIID", client.email)
        buyer_uri.set("schemeID", "EM")

    # TVA intracommunautaire acheteur
    tva_intracom_client = getattr(client, "tva_intracommunautaire", None)
    if tva_intracom_client:
        buyer_tax = ET.SubElement(buyer, _ns("ram", "SpecifiedTaxRegistration"))
        buyer_tax_id = _add_text_element(buyer_tax, "ram", "ID", tva_intracom_client)
        buyer_tax_id.set("schemeID", "VA")

    # Référence de l'acheteur (numéro de commande) — vide mais requis structurellement
    # BuyerOrderReferencedDocument non ajouté car non obligatoire en EN 16931

    # ─── 3.3 ApplicableHeaderTradeDelivery ───────────────────────────
    # L'élément est obligatoire dans le schéma mais ne doit pas être vide
    delivery_header = ET.SubElement(transaction, _ns("ram", "ApplicableHeaderTradeDelivery"))
    # Ajouter la date de livraison = date de facture (convention)
    actual_delivery = ET.SubElement(delivery_header, _ns("ram", "ActualDeliverySupplyChainEvent"))
    occ_dt = ET.SubElement(actual_delivery, _ns("ram", "OccurrenceDateTime"))
    delivery_date_string = ET.SubElement(occ_dt, _ns("udt", "DateTimeString"))
    delivery_date_string.text = _format_date(facture.date_facture)
    delivery_date_string.set("format", "102")

    # ─── 3.4 ApplicableHeaderTradeSettlement ─────────────────────────
    settlement = ET.SubElement(transaction, _ns("ram", "ApplicableHeaderTradeSettlement"))

    # Code devise
    _add_text_element(settlement, "ram", "InvoiceCurrencyCode", "EUR")

    # ─── Récapitulatif TVA par taux (doit précéder SpecifiedTradePaymentTerms) ──
    tva_groups = _group_by_tva(lignes)
    for taux, group_data in tva_groups.items():
        tax_elem = ET.SubElement(settlement, _ns("ram", "ApplicableTradeTax"))
        _add_amount_element(tax_elem, "ram", "CalculatedAmount", group_data["tva_amount"])
        _add_text_element(tax_elem, "ram", "TypeCode", "VAT")
        _add_amount_element(tax_elem, "ram", "BasisAmount", group_data["base_ht"])
        _add_text_element(tax_elem, "ram", "CategoryCode", _get_vat_category(taux))
        _add_text_element(tax_elem, "ram", "RateApplicablePercent", _decimal_str(taux))

    # Conditions de paiement (après ApplicableTradeTax)
    if facture.date_echeance:
        payment_terms = ET.SubElement(settlement, _ns("ram", "SpecifiedTradePaymentTerms"))
        if facture.conditions_particulieres:
            _add_text_element(
                payment_terms, "ram", "Description", facture.conditions_particulieres
            )
        due_dt = ET.SubElement(payment_terms, _ns("ram", "DueDateDateTime"))
        due_date_string = ET.SubElement(due_dt, _ns("udt", "DateTimeString"))
        due_date_string.text = _format_date(facture.date_echeance)
        due_date_string.set("format", "102")

    # ─── Totaux du document ──────────────────────────────────────────
    summation = ET.SubElement(
        settlement, _ns("ram", "SpecifiedTradeSettlementHeaderMonetarySummation")
    )

    # Somme des lignes HT
    _add_amount_element(summation, "ram", "LineTotalAmount", facture.sous_total_ht)

    # Total HT (base de calcul TVA)
    _add_amount_element(summation, "ram", "TaxBasisTotalAmount", facture.sous_total_ht)

    # Total TVA
    _add_amount_element(summation, "ram", "TaxTotalAmount", facture.total_tva, "EUR")

    # Total TTC
    _add_amount_element(summation, "ram", "GrandTotalAmount", facture.total_ttc)

    # Montant à payer
    _add_amount_element(summation, "ram", "DuePayableAmount", facture.total_ttc)

    # ─── Sérialisation ───────────────────────────────────────────────
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")

    # Générer le XML avec déclaration
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_body = ET.tostring(root, encoding="unicode", xml_declaration=False)

    return (xml_declaration + xml_body).encode("utf-8")


def _get_vat_category(taux_tva: Any) -> str:
    """
    Retourne le code catégorie TVA selon le taux.
    S = Standard rate
    Z = Zero rated
    E = Exempt
    """
    taux = Decimal(str(taux_tva))
    if taux == Decimal("0"):
        return "E"  # Exonéré
    return "S"  # Taux standard


def _group_by_tva(lignes: List[Any]) -> dict:
    """
    Regroupe les lignes par taux de TVA pour le récapitulatif.
    Retourne un dict {taux: {"base_ht": ..., "tva_amount": ...}}
    """
    groups: dict = defaultdict(lambda: {"base_ht": Decimal("0"), "tva_amount": Decimal("0")})

    for ligne in lignes:
        taux = Decimal(str(ligne.taux_tva))
        base = Decimal(str(ligne.total_ht))
        tva = (base * taux / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        groups[taux]["base_ht"] += base
        groups[taux]["tva_amount"] += tva

    return dict(groups)
