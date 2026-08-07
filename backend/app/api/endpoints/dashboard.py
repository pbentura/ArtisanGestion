"""
Endpoint Dashboard — Agrège toutes les données KPI en une seule requête.
"""
import logging
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import func, and_, case

from app.api import deps
from app.models.facture import Facture
from app.models.devis import Devis
from app.models.rapport import Rapport
from app.models.client import Client
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
async def get_dashboard(
    db: AsyncSession = Depends(deps.get_db),
    societe_id: int = Depends(deps.get_user_societe_id),
):
    try:
        today = date.today()
        first_day_current_month = today.replace(day=1)
        first_day_previous_month = first_day_current_month - relativedelta(months=1)
        last_day_previous_month = first_day_current_month - timedelta(days=1)
        thirty_days_ago = today - timedelta(days=30)

        # ── 1. CA du mois courant (factures validées) ──
        ca_current = await db.execute(
            select(
                func.coalesce(func.sum(Facture.sous_total_ht), 0).label("ca_ht"),
                func.coalesce(func.sum(Facture.total_ttc), 0).label("ca_ttc"),
            ).where(
                Facture.id_societe == societe_id,
                Facture.statut == "validée",
                Facture.date_facture >= first_day_current_month,
                Facture.date_facture <= today,
            )
        )
        ca_current_row = ca_current.one()

        # ── 2. CA du mois précédent ──
        ca_previous = await db.execute(
            select(
                func.coalesce(func.sum(Facture.sous_total_ht), 0).label("ca_ht"),
                func.coalesce(func.sum(Facture.total_ttc), 0).label("ca_ttc"),
            ).where(
                Facture.id_societe == societe_id,
                Facture.statut == "validée",
                Facture.date_facture >= first_day_previous_month,
                Facture.date_facture <= last_day_previous_month,
            )
        )
        ca_previous_row = ca_previous.one()

        # ── 3. Encours client (factures non payées) ──
        encours = await db.execute(
            select(
                func.coalesce(func.sum(Facture.total_ttc), 0)
            ).where(
                Facture.id_societe == societe_id,
                Facture.est_payee == False,
            )
        )
        encours_ttc = float(encours.scalar() or 0)

        # ── 4. Factures en retard ──
        retard = await db.execute(
            select(
                func.count(Facture.id),
                func.coalesce(func.sum(Facture.total_ttc), 0),
            ).where(
                Facture.id_societe == societe_id,
                Facture.est_payee == False,
                Facture.date_echeance < today,
            )
        )
        retard_row = retard.one()

        # ── 5. Pipeline devis (brouillon/envoyé, non convertis) ──
        pipeline = await db.execute(
            select(
                func.coalesce(func.sum(Devis.total_ttc), 0)
            ).where(
                Devis.id_societe == societe_id,
                Devis.statut.in_(["brouillon", "envoyé"]),
                ~Devis.id.in_(
                    select(Facture.id_devis).where(
                        Facture.id_devis.isnot(None),
                        Facture.id_societe == societe_id,
                    )
                ),
            )
        )
        pipeline_ttc = float(pipeline.scalar() or 0)

        # ── 6. Rapports 30 jours ──
        rapports_stats = await db.execute(
            select(
                func.count(Rapport.id),
                func.count(case((Rapport.statut == "en cours", 1))),
                func.count(case((Rapport.statut == "terminé", 1))),
            ).where(
                Rapport.id_societe == societe_id,
                Rapport.created_at >= thirty_days_ago,
            )
        )
        rapports_row = rapports_stats.one()

        # ── 7. 5 derniers rapports ──
        derniers_rapports_result = await db.execute(
            select(Rapport)
            .options(joinedload(Rapport.client))
            .where(Rapport.id_societe == societe_id)
            .order_by(Rapport.created_at.desc())
            .limit(5)
        )
        derniers_rapports = derniers_rapports_result.scalars().all()

        # ── 8. Top 5 clients par CA ──
        top_clients_result = await db.execute(
            select(
                Client.id,
                Client.nom,
                func.coalesce(func.sum(Facture.total_ttc), 0).label("ca_ttc"),
            )
            .join(Facture, and_(Facture.id_client == Client.id, Facture.statut == "validée"))
            .where(Client.id_societe == societe_id)
            .group_by(Client.id, Client.nom)
            .order_by(func.sum(Facture.total_ttc).desc())
            .limit(5)
        )
        top_clients = top_clients_result.all()

        # ── 9. Taux de conversion ──
        total_devis_result = await db.execute(
            select(func.count(Devis.id)).where(Devis.id_societe == societe_id)
        )
        total_devis = total_devis_result.scalar() or 0

        devis_convertis_result = await db.execute(
            select(func.count(func.distinct(Facture.id_devis))).where(
                Facture.id_societe == societe_id,
                Facture.id_devis.isnot(None),
            )
        )
        devis_convertis = devis_convertis_result.scalar() or 0

        taux_conversion = round((devis_convertis / total_devis * 100), 1) if total_devis > 0 else 0.0

        # ── 10. Factures à relancer (en retard, non payées) ──
        relance_result = await db.execute(
            select(Facture)
            .options(joinedload(Facture.client))
            .where(
                Facture.id_societe == societe_id,
                Facture.est_payee == False,
                Facture.date_echeance < today,
            )
            .order_by(Facture.date_echeance.asc())
            .limit(10)
        )
        factures_a_relancer = relance_result.unique().scalars().all()

        # ── 11. Devis arrivant à expiration (7 jours) ──
        # Fetch all active devis and filter expiration in Python to avoid
        # complex PostgreSQL interval arithmetic in SQLAlchemy
        devis_actifs_result = await db.execute(
            select(Devis)
            .options(joinedload(Devis.client))
            .where(
                Devis.id_societe == societe_id,
                Devis.statut.in_(["brouillon", "envoyé"]),
            )
            .order_by(Devis.date_devis.asc())
        )
        devis_actifs = devis_actifs_result.unique().scalars().all()
        
        devis_expirant = []
        for d in devis_actifs:
            if d.date_devis and d.nb_jours_validite:
                expiry = d.date_devis + timedelta(days=d.nb_jours_validite)
                if today <= expiry <= today + timedelta(days=7):
                    devis_expirant.append(d)
                    if len(devis_expirant) >= 10:
                        break

        # ── 12. Évolution CA sur 6 mois ──
        evolution_ca = []
        for i in range(5, -1, -1):
            month_start = first_day_current_month - relativedelta(months=i)
            month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)

            evo_result = await db.execute(
                select(
                    func.coalesce(func.sum(Facture.sous_total_ht), 0),
                    func.coalesce(func.sum(Facture.total_ttc), 0),
                ).where(
                    Facture.id_societe == societe_id,
                    Facture.statut == "validée",
                    Facture.date_facture >= month_start,
                    Facture.date_facture <= month_end,
                )
            )
            evo_row = evo_result.one()
            evolution_ca.append({
                "mois": month_start.strftime("%Y-%m"),
                "label": month_start.strftime("%b %Y"),
                "ca_ht": float(evo_row[0]),
                "ca_ttc": float(evo_row[1]),
            })

        # ── 13. 5 dernières factures impayées ──
        impayees_result = await db.execute(
            select(Facture)
            .options(joinedload(Facture.client))
            .where(
                Facture.id_societe == societe_id,
                Facture.est_payee == False,
            )
            .order_by(Facture.date_echeance.asc())
            .limit(5)
        )
        factures_impayees = impayees_result.unique().scalars().all()

        # ── Build response ──
        def serialize_facture(f):
            return {
                "id": f.id,
                "numero_facture": f.numero_facture,
                "titre_document_pdf": f.titre_document_pdf,
                "date_facture": str(f.date_facture) if f.date_facture else None,
                "date_echeance": str(f.date_echeance) if f.date_echeance else None,
                "total_ttc": float(f.total_ttc),
                "statut": f.statut,
                "est_payee": f.est_payee,
                "client_nom": f.client.nom if f.client else "Inconnu",
            }

        def serialize_rapport(r):
            return {
                "id": r.id,
                "titre_document_pdf": r.titre_document_pdf,
                "date_intervention": str(r.date_intervention) if r.date_intervention else None,
                "statut": r.statut,
                "contenu": (r.contenu[:120] + "...") if r.contenu and len(r.contenu) > 120 else r.contenu,
                "photos": r.photos or [],
                "photo_url": r.photo_url,
                "client_nom": r.client.nom if r.client else "Inconnu",
                "created_at": str(r.created_at) if r.created_at else None,
            }

        def serialize_devis(d):
            expiry = d.date_devis + timedelta(days=d.nb_jours_validite) if d.date_devis and d.nb_jours_validite else None
            return {
                "id": d.id,
                "numero_devis": d.numero_devis,
                "titre_document_pdf": d.titre_document_pdf,
                "date_devis": str(d.date_devis) if d.date_devis else None,
                "date_expiration": str(expiry) if expiry else None,
                "total_ttc": float(d.total_ttc),
                "statut": d.statut,
                "client_nom": d.client.nom if d.client else "Inconnu",
            }

        return {
            # KPIs financiers
            "ca_mois_ht": float(ca_current_row.ca_ht),
            "ca_mois_ttc": float(ca_current_row.ca_ttc),
            "ca_mois_precedent_ht": float(ca_previous_row.ca_ht),
            "ca_mois_precedent_ttc": float(ca_previous_row.ca_ttc),
            "encours_client_ttc": encours_ttc,
            "factures_en_retard_count": retard_row[0],
            "factures_en_retard_montant": float(retard_row[1]),
            "pipeline_devis_ttc": pipeline_ttc,

            # Activité
            "rapports_30_jours": rapports_row[0],
            "rapports_en_cours": rapports_row[1],
            "rapports_termines": rapports_row[2],
            "derniers_rapports": [serialize_rapport(r) for r in derniers_rapports],

            # Top clients
            "top_clients": [
                {"id": c.id, "nom": c.nom, "ca_ttc": float(c.ca_ttc)}
                for c in top_clients
            ],

            # Taux de conversion
            "total_devis": total_devis,
            "devis_convertis": devis_convertis,
            "taux_conversion": taux_conversion,

            # Alertes
            "factures_a_relancer": [serialize_facture(f) for f in factures_a_relancer],
            "devis_expirant": [serialize_devis(d) for d in devis_expirant],

            # Évolution CA
            "evolution_ca": evolution_ca,

            # Factures impayées
            "factures_impayees": [serialize_facture(f) for f in factures_impayees],
        }

    except Exception as e:
        logger.error(f"Dashboard error: {e}", exc_info=True)
        raise
