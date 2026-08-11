"""
Endpoints pour l'intégration Stripe Connect Express.
Gère l'onboarding des artisans, le statut du compte, et la déconnexion.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import stripe
from app.core.config import settings
from app.api.deps import get_db, get_current_user, get_user_societe_id, require_permission
from app.models.user import User
from app.models.societe import Societe

logger = logging.getLogger(__name__)

router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/onboarding")
async def create_connect_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("can_edit_societe")),
    societe_id: int = Depends(get_user_societe_id),
):
    """
    Crée un compte Stripe Connect Express pour la société de l'artisan
    et retourne le lien d'onboarding.
    """
    result = await db.execute(select(Societe).where(Societe.id == societe_id))
    societe = result.scalars().first()
    if not societe:
        raise HTTPException(status_code=404, detail="Société introuvable")

    # Si le compte Connect existe déjà, on régénère juste le lien d'onboarding
    if societe.stripe_connect_account_id:
        try:
            # Vérifier si le compte existe encore chez Stripe
            account = stripe.Account.retrieve(societe.stripe_connect_account_id)
            if account.charges_enabled and account.payouts_enabled:
                # Déjà entièrement configuré
                societe.stripe_connect_enabled = True
                societe.stripe_connect_onboarding_complete = True
                await db.commit()
                return {
                    "status": "already_connected",
                    "message": "Votre compte Stripe Connect est déjà actif."
                }
        except stripe.error.InvalidRequestError:
            # Le compte n'existe plus chez Stripe, on en recrée un
            societe.stripe_connect_account_id = None
            societe.stripe_connect_enabled = False
            societe.stripe_connect_onboarding_complete = False

    # Créer un nouveau compte Express si nécessaire
    if not societe.stripe_connect_account_id:
        try:
            account = stripe.Account.create(
                type="express",
                country="FR",
                email=societe.email or current_user.email,
                business_type="individual",
                capabilities={
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                },
                business_profile={
                    "mcc": "1520",  # General Contractors
                    "product_description": f"Services artisanaux - {societe.nom}",
                },
                individual={
                    "email": societe.email or current_user.email,
                    "first_name": current_user.prenom or "",
                    "last_name": current_user.nom or "",
                },
                metadata={
                    "societe_id": str(societe.id),
                    "user_id": str(current_user.id),
                    "platform": "artisangestion",
                },
            )
            societe.stripe_connect_account_id = account.id
            await db.commit()
        except Exception as e:
            logger.error(f"Erreur création compte Connect: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de la création du compte Stripe: {str(e)}"
            )

    # Générer le lien d'onboarding
    try:
        account_link = stripe.AccountLink.create(
            account=societe.stripe_connect_account_id,
            refresh_url=f"{settings.FRONTEND_URL}/app/entreprise?stripe=refresh",
            return_url=f"{settings.FRONTEND_URL}/app/stripe-connect/return",
            type="account_onboarding",
        )
        return {"onboarding_url": account_link.url}
    except Exception as e:
        logger.error(f"Erreur création lien onboarding: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du lien d'onboarding: {str(e)}"
        )


@router.get("/onboarding/refresh")
async def refresh_onboarding_link(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    societe_id: int = Depends(get_user_societe_id),
):
    """
    Régénère un lien d'onboarding Stripe Connect si l'ancien a expiré.
    """
    result = await db.execute(select(Societe).where(Societe.id == societe_id))
    societe = result.scalars().first()

    if not societe or not societe.stripe_connect_account_id:
        raise HTTPException(
            status_code=400,
            detail="Aucun compte Stripe Connect trouvé. Lancez d'abord l'activation."
        )

    try:
        account_link = stripe.AccountLink.create(
            account=societe.stripe_connect_account_id,
            refresh_url=f"{settings.FRONTEND_URL}/app/entreprise?stripe=refresh",
            return_url=f"{settings.FRONTEND_URL}/app/stripe-connect/return",
            type="account_onboarding",
        )
        return {"onboarding_url": account_link.url}
    except Exception as e:
        logger.error(f"Erreur refresh lien onboarding: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/onboarding/return")
async def onboarding_return(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    societe_id: int = Depends(get_user_societe_id),
):
    """
    Endpoint de retour après l'onboarding Stripe Connect.
    Vérifie le statut du compte et met à jour la société.
    """
    result = await db.execute(select(Societe).where(Societe.id == societe_id))
    societe = result.scalars().first()

    if not societe or not societe.stripe_connect_account_id:
        raise HTTPException(status_code=400, detail="Aucun compte Connect trouvé.")

    try:
        account = stripe.Account.retrieve(societe.stripe_connect_account_id)

        societe.stripe_connect_onboarding_complete = account.details_submitted
        societe.stripe_connect_enabled = (
            account.charges_enabled and account.payouts_enabled
        )

        await db.commit()

        return {
            "status": "success",
            "details_submitted": account.details_submitted,
            "charges_enabled": account.charges_enabled,
            "payouts_enabled": account.payouts_enabled,
            "stripe_connect_enabled": societe.stripe_connect_enabled,
        }
    except Exception as e:
        logger.error(f"Erreur vérification compte Connect: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_connect_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    societe_id: int = Depends(get_user_societe_id),
):
    """
    Retourne le statut actuel du compte Stripe Connect de la société.
    """
    result = await db.execute(select(Societe).where(Societe.id == societe_id))
    societe = result.scalars().first()

    if not societe:
        raise HTTPException(status_code=404, detail="Société introuvable")

    if not societe.stripe_connect_account_id:
        return {
            "connected": False,
            "enabled": False,
            "onboarding_complete": False,
        }

    # Rafraîchir le statut depuis Stripe
    try:
        account = stripe.Account.retrieve(societe.stripe_connect_account_id)
        societe.stripe_connect_onboarding_complete = account.details_submitted
        societe.stripe_connect_enabled = (
            account.charges_enabled and account.payouts_enabled
        )
        await db.commit()

        return {
            "connected": True,
            "enabled": societe.stripe_connect_enabled,
            "onboarding_complete": societe.stripe_connect_onboarding_complete,
            "account_id": societe.stripe_connect_account_id,
        }
    except Exception as e:
        logger.error(f"Erreur vérification statut Connect: {e}")
        return {
            "connected": True,
            "enabled": societe.stripe_connect_enabled,
            "onboarding_complete": societe.stripe_connect_onboarding_complete,
            "error": "Impossible de vérifier le statut en temps réel",
        }


@router.post("/disconnect")
async def disconnect_connect_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("can_edit_societe")),
    societe_id: int = Depends(get_user_societe_id),
):
    """
    Déconnecte le compte Stripe Connect de la société.
    Note: Ne supprime pas le compte Stripe, mais le délie de la plateforme.
    """
    result = await db.execute(select(Societe).where(Societe.id == societe_id))
    societe = result.scalars().first()

    if not societe:
        raise HTTPException(status_code=404, detail="Société introuvable")

    if not societe.stripe_connect_account_id:
        raise HTTPException(status_code=400, detail="Aucun compte Connect à déconnecter.")

    societe.stripe_connect_account_id = None
    societe.stripe_connect_enabled = False
    societe.stripe_connect_onboarding_complete = False
    await db.commit()

    return {"status": "success", "message": "Compte Stripe Connect déconnecté."}
