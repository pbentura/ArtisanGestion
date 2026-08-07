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
                filename=filename
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
    current_user: User = Depends(deps.get_current_user)
):
    """
    Envoie un document (devis, facture, rapport) par email au client de façon synchrone.
    """
    success = await generate_and_send_document(current_user.id, request)
    if not success:
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi de l'email")
        
    return {"message": "Email envoyé avec succès", "status": "success"}
