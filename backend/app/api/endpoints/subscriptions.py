from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import stripe
from app.core.config import settings
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY

class CheckoutRequest(BaseModel):
    plan_name: str
    is_annual: bool
    price: float

@router.post("/create-checkout-session")
async def create_checkout_session(request: CheckoutRequest, current_user: User = Depends(get_current_user)):
    if not settings.STRIPE_SECRET_KEY or settings.STRIPE_SECRET_KEY == "sk_test_placeholder":
        # Pour le développement/test si la clé n'est pas configurée
        # On va simuler un retour d'URL vers l'accueil ou renvoyer une erreur explicite
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="La clé secrète Stripe n'est pas configurée. Veuillez l'ajouter dans le fichier .env (STRIPE_SECRET_KEY)."
        )

    try:
        # Création d'une session de paiement Stripe
        # Nous utilisons price_data pour créer le prix à la volée, sans avoir besoin
        # de le pré-configurer dans le dashboard Stripe (utile pour l'intégration rapide)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': f"Abonnement {request.plan_name} ({'Annuel' if request.is_annual else 'Mensuel'})",
                    },
                    'unit_amount': int(request.price * 100),
                    'recurring': {
                        'interval': 'year' if request.is_annual else 'month',
                    }
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=settings.FRONTEND_URL + "/app/settings?tab=abonnement&session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.FRONTEND_URL + "/app/settings?tab=abonnement",
            client_reference_id=str(current_user.id),
            customer_email=current_user.email,
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
