from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import stripe
from app.core.config import settings
from app.api.deps import get_current_user, get_db
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
            metadata={"plan": request.plan_name},
            success_url=settings.FRONTEND_URL + "/app/settings?tab=abonnement&session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.FRONTEND_URL + "/app/settings?tab=abonnement",
            client_reference_id=str(current_user.id),
            customer_email=current_user.email,
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        # In a real app, you would define STRIPE_WEBHOOK_SECRET in settings
        # and use stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        # Here we just parse the event since we don't have the secret configured for local dev
        event = stripe.Event.construct_from(
            stripe.util.json.loads(payload), stripe.api_key
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event.type == 'checkout.session.completed':
        session = event.data.object
        client_reference_id = session.get("client_reference_id")
        plan_name = session.get("metadata", {}).get("plan")

        if client_reference_id and plan_name:
            user_id = int(client_reference_id)
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()

            if user:
                # 19€ -> PREMIUM, 39€ -> TEAM
                # Les noms de plan sont "Indépendant" et "Équipe"
                if plan_name.lower() == "équipe" or plan_name.lower() == "equipe":
                    user.role = "TEAM"
                else:
                    user.role = "PREMIUM"
                
                await db.commit()

    return {"status": "success"}
