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

@router.post("/create-portal-session")
async def create_portal_session(current_user: User = Depends(get_current_user)):
    """Créer une session de portail client Stripe pour gérer l'abonnement."""
    if not settings.STRIPE_SECRET_KEY or settings.STRIPE_SECRET_KEY == "sk_test_placeholder":
        raise HTTPException(status_code=500, detail="La clé secrète Stripe n'est pas configurée.")
        
    try:
        # Trouver le customer Stripe via son email (ou id si stocké)
        customers = stripe.Customer.list(email=current_user.email, limit=1)
        if not customers.data:
            raise HTTPException(status_code=404, detail="Aucun compte client Stripe trouvé pour cet utilisateur.")
            
        customer_id = customers.data[0].id
        
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=settings.FRONTEND_URL + "/app/settings?tab=abonnement",
        )
        return {"portal_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        if settings.STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        else:
            # Fallback pour le dev local sans webhook secret
            event = stripe.Event.construct_from(
                stripe.util.json.loads(payload), stripe.api_key
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event.type == 'checkout.session.completed':
        session = event.data.object
        metadata = session.get("metadata", {})

        # --- Paiement de facture via Connect ---
        if metadata.get("type") == "invoice_payment":
            facture_id = metadata.get("facture_id")
            user_id = metadata.get("user_id")

            if facture_id:
                from app.models.facture import Facture

                result = await db.execute(
                    select(Facture).where(Facture.id == int(facture_id))
                )
                facture = result.scalars().first()

                if facture and not facture.est_payee:
                    facture.est_payee = True
                    await db.commit()

                    # Notification WebSocket à l'artisan
                    if user_id:
                        try:
                            from app.core.websockets import manager
                            await manager.broadcast_to_user(int(user_id), {
                                "type": "INVOICE_PAID",
                                "facture_id": int(facture_id),
                                "message": f"La facture {facture.numero_facture} a été payée en ligne !",
                            })
                        except Exception as ws_err:
                            import logging
                            logging.getLogger(__name__).warning(f"WebSocket notification failed: {ws_err}")

        # --- Abonnement classique ---
        else:
            client_reference_id = session.get("client_reference_id")
            plan_name = metadata.get("plan")

            if client_reference_id and plan_name:
                user_id = int(client_reference_id)
                result = await db.execute(select(User).where(User.id == user_id))
                user = result.scalars().first()

                if user:
                    if plan_name.lower() == "équipe" or plan_name.lower() == "equipe":
                        user.role = "TEAM"
                    else:
                        user.role = "PREMIUM"
                    
                    await db.commit()

    elif event.type in ['customer.subscription.deleted', 'customer.subscription.canceled']:
        subscription = event.data.object
        customer_id = subscription.get("customer")
        
        if customer_id:
            customer = stripe.Customer.retrieve(customer_id)
            email = customer.get("email")
            
            if email:
                result = await db.execute(select(User).where(User.email == email))
                user = result.scalars().first()
                if user:
                    user.role = "USER"
                    await db.commit()

    elif event.type == 'customer.subscription.updated':
        subscription = event.data.object
        customer_id = subscription.get("customer")
        sub_status = subscription.get("status")
        
        if sub_status in ['canceled', 'unpaid', 'past_due'] and customer_id:
            customer = stripe.Customer.retrieve(customer_id)
            email = customer.get("email")
            
            if email:
                result = await db.execute(select(User).where(User.email == email))
                user = result.scalars().first()
                if user:
                    user.role = "USER"
                    await db.commit()

    elif event.type == 'account.updated':
        # Stripe Connect: mise à jour du statut du compte artisan
        account = event.data.object
        account_id = account.get("id")

        if account_id:
            from app.models.societe import Societe as SocieteModel

            result = await db.execute(
                select(SocieteModel).where(
                    SocieteModel.stripe_connect_account_id == account_id
                )
            )
            societe = result.scalars().first()

            if societe:
                societe.stripe_connect_enabled = (
                    account.get("charges_enabled", False)
                    and account.get("payouts_enabled", False)
                )
                societe.stripe_connect_onboarding_complete = account.get(
                    "details_submitted", False
                )
                await db.commit()

    return {"status": "success"}

