from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.facture import Facture
from app.models.societe import Societe
from datetime import date

async def get_next_invoice_number(db: AsyncSession, societe_id: int, is_avoir: bool = False) -> str:
    """
    Génère le prochain numéro de facture séquentiel pour une société donnée.
    Format : YYYY-XXXX pour les factures, AV-YYYY-XXXX pour les avoirs.
    """
    year = date.today().year
    prefix = "AV-" if is_avoir else ""
    
    # On recherche le numéro le plus élevé pour l'année en cours
    # Le pattern de recherche dépend de si c'est un avoir ou non
    search_pattern = f"{prefix}{year}-%"
    
    result = await db.execute(
        select(Facture.numero_facture)
        .where(
            Facture.id_societe == societe_id,
            Facture.est_avoir == is_avoir,
            Facture.numero_facture.like(search_pattern),
            Facture.statut == "validée"
        )
        .order_by(Facture.numero_facture.desc())
        .limit(1)
    )
    last_number = result.scalars().first()
    
    if not last_number:
        # Si aucun numéro trouvé pour cette année, on regarde dans la société avec un Lock (FOR UPDATE)
        # pour s'assurer qu'aucune autre transaction ne génère de numéro en même temps.
        result_soc = await db.execute(
            select(Societe)
            .where(Societe.id == societe_id)
            .with_for_update()
        )
        societe = result_soc.scalars().first()
        if societe and societe.dernier_numero_facture:
            # On ne l'utilise que si l'année correspond ou si on force le début
            if str(year) in societe.dernier_numero_facture:
                last_number = societe.dernier_numero_facture
    else:
        # Même si on a trouvé un numéro, on pose un verrou sur la société
        # pour bloquer la concurrence jusqu'au COMMIT.
        await db.execute(
            select(Societe.id)
            .where(Societe.id == societe_id)
            .with_for_update()
        )

    new_sequence = 1
    if last_number:
        try:
            # On extrait la partie séquentielle à la fin
            parts = last_number.split("-")
            last_seq = int(parts[-1])
            new_sequence = last_seq + 1
        except (ValueError, IndexError):
            new_sequence = 1
            
    # Formatage final : Année-0001
    return f"{prefix}{year}-{new_sequence:04d}"
