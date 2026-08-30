"""
Signature électronique des devis.

Niveau visé : signature électronique *simple* au sens du règlement eIDAS.
Elle n'a pas la présomption de fiabilité d'une signature qualifiée, mais reste
recevable en preuve dès lors qu'on peut établir qui a signé, quand, et que le
document n'a pas changé depuis. C'est ce que ce module fabrique :

- un lien à jeton aléatoire, à durée de vie limitée, envoyé au client ;
- un faisceau d'indices consigné au moment de la signature (nom, email, IP,
  navigateur, horodatage serveur) ;
- une empreinte SHA-256 du contenu contractuel, qui permet plus tard de
  démontrer que le devis signé est bien celui qu'on présente.
"""

import hashlib
import secrets
from decimal import Decimal
from typing import Optional

from starlette.requests import Request

# Durée de validité du lien de signature, en jours.
VALIDITE_LIEN_JOURS = 30


def generer_token() -> str:
    """Jeton d'URL imprévisible (256 bits d'entropie)."""
    return secrets.token_urlsafe(32)


def _fmt(valeur) -> str:
    """Normalise les montants pour que l'empreinte soit stable."""
    if valeur is None:
        return ""
    if isinstance(valeur, Decimal):
        return f"{valeur:.2f}"
    return str(valeur)


def calculer_empreinte(devis, lignes) -> str:
    """
    Empreinte SHA-256 du contenu contractuel du devis.

    On n'inclut que ce qui engage les parties — numéro, date, montants et
    détail des lignes. Les champs de suivi (statut, dates de modification)
    en sont exclus : ils bougent après la signature sans changer l'accord.
    """
    parts = [
        _fmt(devis.numero_devis),
        _fmt(devis.date_devis),
        _fmt(devis.objet_devis),
        _fmt(devis.sous_total_ht),
        _fmt(devis.total_tva),
        _fmt(devis.total_ttc),
        _fmt(devis.conditions_particulieres),
        _fmt(devis.id_client),
    ]
    for ligne in sorted(lignes, key=lambda l: l.id or 0):
        parts += [
            _fmt(ligne.description),
            _fmt(ligne.quantite),
            _fmt(ligne.prix_unite_ht),
            _fmt(ligne.taux_tva),
            _fmt(ligne.total_ht),
        ]
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


def adresse_client(request: Request) -> Optional[str]:
    """
    IP réelle de l'appelant.

    L'API tourne derrière un reverse proxy : on lit X-Forwarded-For en
    priorité, dont le premier élément est le client d'origine.
    """
    transmis = request.headers.get("x-forwarded-for")
    if transmis:
        return transmis.split(",")[0].strip()[:100]
    return request.client.host[:100] if request.client else None


def signature_valide(donnee: Optional[str]) -> bool:
    """
    Vérifie sommairement que la signature reçue est bien une image PNG encodée
    en data URL, et qu'elle n'est ni vide ni démesurée.
    """
    if not donnee or not isinstance(donnee, str):
        return False
    if not donnee.startswith("data:image/png;base64,"):
        return False
    charge_utile = donnee.split(",", 1)[1] if "," in donnee else ""
    # Un tracé vide fait quelques centaines d'octets ; au-delà de ~2 Mo on refuse.
    return 200 < len(charge_utile) < 2_800_000
