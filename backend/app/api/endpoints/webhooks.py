"""
Ancienne URL de webhook Stripe, conservée comme alias.

Historiquement, ce module portait un second gestionnaire qui ne traitait que
le paiement des factures. Un endpoint Stripe configuré ici répondait donc 200
à un événement d'abonnement sans rien en faire : le client payait et restait
bloqué, sans la moindre erreur pour le signaler.

Plutôt que de supprimer la route — ce qui casserait tout endpoint Stripe
encore configuré sur cette URL — elle délègue désormais au gestionnaire unique
de `subscriptions.py`, qui couvre les deux flux. Les deux URL sont donc
interchangeables, et le piège a disparu.

Rien de nouveau ne devrait pointer ici : la référence est
`POST /api/subscriptions/webhook`.
"""

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.endpoints.subscriptions import (
    traiter_evenement_stripe,
    verifier_signature_stripe,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/stripe")
async def stripe_webhook_alias(request: Request, db: AsyncSession = Depends(get_db)):
    """Alias de compatibilité vers POST /api/subscriptions/webhook."""
    payload = await request.body()
    event = verifier_signature_stripe(
        payload, request.headers.get("stripe-signature"), request.url.path
    )
    await traiter_evenement_stripe(event, db)
    return {"status": "success"}
