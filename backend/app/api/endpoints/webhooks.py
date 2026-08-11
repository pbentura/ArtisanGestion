import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import stripe

from app.core.config import settings
from app.api.deps import get_db
from app.models.facture import Facture

logger = logging.getLogger(__name__)
router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET if hasattr(settings, "STRIPE_WEBHOOK_SECRET") else None

@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    event = None

    try:
        if endpoint_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        else:
            # Si pas de secret configuré (ex: dev local sans stripe-cli configuré), on parse juste le JSON
            # Note: En production, le secret est OBLIGATOIRE pour des raisons de sécurité.
            import json
            data = json.loads(payload)
            event = stripe.Event.construct_from(data, stripe.api_key)
            
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        
        # Vérifier si c'est un paiement de facture
        if session.get("metadata") and session["metadata"].get("type") == "invoice_payment":
            facture_id = session["metadata"].get("facture_id")
            if facture_id:
                try:
                    result = await db.execute(select(Facture).where(Facture.id == int(facture_id)))
                    facture = result.scalars().first()
                    
                    if facture:
                        facture.est_payee = True
                        await db.commit()
                        logger.info(f"Facture {facture_id} marquée comme payée via Webhook.")
                except Exception as e:
                    logger.error(f"Erreur lors de la mise à jour de la facture {facture_id}: {e}")

    return {"status": "success"}
