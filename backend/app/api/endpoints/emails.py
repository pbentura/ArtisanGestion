from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
import logging

from app.api import deps
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.societe import Societe
from app.models.facture import Facture
from app.models.devis import Devis
from app.services.email_service import send_transactional_document
from app.services.pdf_generator import generate_invoice_pdf

logger = logging.getLogger(__name__)

router = APIRouter()

class DocumentEmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    message: str
    document_id: int
    document_type: str  # "facture", "devis", "rapport"

class DevisAdapter:
    def __init__(self, devis):
        self._devis = devis
        self.titre_document_pdf = devis.titre_document_pdf
        self.numero_facture = devis.numero_devis
        self.objet_facture = devis.objet_devis
        self.date_facture = devis.date_devis
        self.sous_total_ht = devis.sous_total_ht
        self.total_tva = devis.total_tva
        self.total_ttc = devis.total_ttc
        self.conditions_particulieres = devis.conditions_particulieres
        self.date_echeance = None
        self.nb_jours_echeance = None

async def generate_and_send_document(
    user_id: int,
    request: DocumentEmailRequest
) -> bool:
    async with AsyncSessionLocal() as db:
        try:
            # Get artisan info
            societe_result = await db.execute(select(Societe).where(Societe.id_user == user_id))
            societe = societe_result.scalars().first()
            
            user_result = await db.execute(select(User).where(User.id == user_id))
            user = user_result.scalars().first()
            
            if not societe or not user:
                logger.error("Societe or User not found for email sending")
                raise HTTPException(status_code=404, detail="Société ou utilisateur non trouvé")

            artisan_name = societe.nom
            artisan_email = user.email

            pdf_bytes = b""
            filename = "document.pdf"
            payment_url = None

            if request.document_type == "facture":
                result = await db.execute(
                    select(Facture)
                    .options(joinedload(Facture.client), joinedload(Facture.lignes))
                    .where(Facture.id == request.document_id, Facture.id_user == user_id)
                )
                facture = result.unique().scalars().first()
                if not facture:
                    logger.error(f"Facture {request.document_id} not found")
                    raise HTTPException(status_code=404, detail="Facture introuvable")
                pdf_bytes = generate_invoice_pdf(facture, facture.client, societe, facture.lignes)
                filename = f"Facture_{facture.numero_facture}.pdf"

                # Générer un lien de paiement si le compte Connect est actif
                if (
                    societe.stripe_connect_enabled
                    and societe.stripe_connect_account_id
                    and facture.statut == "validée"
                    and not facture.est_payee
                    and not facture.est_avoir
                ):
                    if facture.stripe_payment_url:
                        payment_url = facture.stripe_payment_url
                    else:
                        try:
                            import stripe
                            from app.core.config import settings

                            stripe.api_key = settings.STRIPE_SECRET_KEY

                            total_cents = int(float(facture.total_ttc) * 100)
                            commission_percent = settings.STRIPE_CONNECT_COMMISSION_PERCENT
                            application_fee = int(total_cents * commission_percent / 100)

                            session = stripe.checkout.Session.create(
                                payment_method_types=["card"],
                                line_items=[
                                    {
                                        "price_data": {
                                            "currency": "eur",
                                            "product_data": {
                                                "name": f"Facture {facture.numero_facture}",
                                                "description": facture.objet_facture or f"Facture de {societe.nom}",
                                            },
                                            "unit_amount": total_cents,
                                        },
                                        "quantity": 1,
                                    }
                                ],
                                mode="payment",
                                payment_intent_data={
                                    "application_fee_amount": application_fee,
                                },
                                metadata={
                                    "type": "invoice_payment",
                                    "facture_id": str(facture.id),
                                    "societe_id": str(societe.id),
                                    "user_id": str(user.id),
                                },
                                success_url=f"{settings.FRONTEND_URL}/pay/success?session_id={{CHECKOUT_SESSION_ID}}",
                                cancel_url=f"{settings.FRONTEND_URL}/pay/cancel",
                                stripe_account=societe.stripe_connect_account_id,
                            )

                            facture.stripe_checkout_session_id = session.id
                            facture.stripe_payment_url = session.url
                            payment_url = session.url
                            await db.commit()
                            logger.info(f"Payment link generated for facture {facture.id}: {session.url}")
                        except Exception as stripe_err:
                            logger.warning(f"Could not generate payment link for facture {facture.id}: {stripe_err}")

            elif request.document_type == "devis":
                result = await db.execute(
                    select(Devis)
                    .options(joinedload(Devis.client), joinedload(Devis.lignes))
                    .where(Devis.id == request.document_id, Devis.id_user == user_id)
                )
                devis = result.unique().scalars().first()
                if not devis:
                    logger.error(f"Devis {request.document_id} not found")
                    raise HTTPException(status_code=404, detail="Devis introuvable")
                adapted_devis = DevisAdapter(devis)
                pdf_bytes = generate_invoice_pdf(adapted_devis, devis.client, societe, devis.lignes)
                filename = f"Devis_{devis.numero_devis}.pdf"

            elif request.document_type == "rapport":
                from app.models.rapport import Rapport
                from app.services.pdf_generator import generate_rapport_pdf
                result = await db.execute(
                    select(Rapport)
                    .options(joinedload(Rapport.client))
                    .where(Rapport.id == request.document_id, Rapport.id_user == user_id)
                )
                rapport = result.unique().scalars().first()
                if not rapport:
                    logger.error(f"Rapport {request.document_id} not found")
                    raise HTTPException(status_code=404, detail="Rapport introuvable")
                
                pdf_bytes = generate_rapport_pdf(rapport, rapport.client, societe)
                filename = f"Rapport_{rapport.id}.pdf"
            
            else:
                logger.error(f"Unknown document type {request.document_type}")
                raise HTTPException(status_code=400, detail="Type de document inconnu")

            # Call email service
            success = await send_transactional_document(
                to=request.to_email,
                subject=request.subject,
                message=request.message,
                artisan_name=artisan_name,
                artisan_email=artisan_email,
                pdf_bytes=pdf_bytes,
                filename=filename,
                payment_url=payment_url,
            )
            if success:
                logger.info(f"Successfully sent {request.document_type} {request.document_id}")
                return True
            else:
                return False
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in background task generate_and_send_document: {e}")
            return False

@router.post("/send-document")
async def send_document(
    request: DocumentEmailRequest,
    current_user: User = Depends(deps.check_trial_active)
):
    """
    Envoie un document (devis, facture, rapport) par email au client de façon synchrone.
    """
    success = await generate_and_send_document(current_user.id, request)
    if not success:
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi de l'email")
        
    return {"message": "Email envoyé avec succès", "status": "success"}
