import json
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import stripe
from app.core.config import settings
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.email_service import (
    send_payment_failed,
    send_subscription_cancelled,
    send_subscription_confirmation,
)

logger = logging.getLogger(__name__)
router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY

class CheckoutRequest(BaseModel):
    plan_name: str
    is_annual: bool
    # Note : le champ "price" éventuellement envoyé par le frontend est ignoré.
    # Les montants sont définis côté serveur (voir PLANS ci-dessous).


# Catalogue tarifaire — source de vérité côté serveur.
# Montants en centimes, facturés par période (mois ou année).
PLANS = {
    "indépendant": {"label": "Indépendant", "mensuel": 1900, "annuel": 18600},
    "équipe":      {"label": "Équipe",      "mensuel": 3900, "annuel": 39000},
}

# Tolère les saisies sans accent envoyées par le client
_ALIAS_PLANS = {
    "independant": "indépendant",
    "equipe": "équipe",
}


def _resoudre_plan(plan_name: str) -> tuple[str, dict]:
    """Retourne (clé, plan) pour un nom de plan, ou lève une 400."""
    cle = (plan_name or "").strip().lower()
    cle = _ALIAS_PLANS.get(cle, cle)
    plan = PLANS.get(cle)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plan inconnu : {plan_name}",
        )
    return cle, plan

STATUTS_ACTIFS = ("active", "trialing", "past_due", "unpaid")


async def _client_stripe(user: User, db: AsyncSession) -> Optional[str]:
    """
    Identifiant du client Stripe rattaché au compte.

    Mémorisé en base dès qu'il est connu. La recherche par email n'est qu'un
    rattrapage pour les comptes antérieurs à cette colonne : Stripe crée un
    client par session de paiement, et interroger par email finit par renvoyer
    le mauvais dès qu'il y en a plusieurs.
    """
    if user.stripe_customer_id:
        return user.stripe_customer_id

    try:
        clients = stripe.Customer.list(email=user.email, limit=1)
    except Exception:
        logger.exception("Recherche du client Stripe de %s impossible.", user.email)
        return None
    if not clients.data:
        return None

    user.stripe_customer_id = clients.data[0].id
    db.add(user)
    await db.commit()
    return user.stripe_customer_id


async def _abonnement_actif(user: User, db: AsyncSession):
    """Abonnement en cours, ou None. Source de vérité : Stripe, pas le rôle."""
    client = await _client_stripe(user, db)
    if not client:
        return None
    try:
        abonnements = stripe.Subscription.list(customer=client, status="all", limit=10)
    except Exception:
        logger.exception("Abonnements de %s illisibles.", user.email)
        return None
    for abo in abonnements.data:
        if abo.status in STATUTS_ACTIFS:
            return abo
    return None


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not settings.STRIPE_SECRET_KEY or settings.STRIPE_SECRET_KEY == "sk_test_placeholder":
        # Pour le développement/test si la clé n'est pas configurée
        # On va simuler un retour d'URL vers l'accueil ou renvoyer une erreur explicite
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="La clé secrète Stripe n'est pas configurée. Veuillez l'ajouter dans le fichier .env (STRIPE_SECRET_KEY)."
        )

    # Sans ce contrôle, un abonné qui reclique crée un SECOND abonnement et se
    # fait prélever deux fois. Pire : chaque session créant un nouveau client
    # Stripe, le premier abonnement devenait introuvable depuis le portail et
    # son titulaire ne pouvait plus le résilier lui-même.
    if await _abonnement_actif(current_user, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vous avez déjà un abonnement en cours. Gérez-le depuis vos paramètres.",
        )

    # Le montant est déterminé par le serveur à partir du catalogue, jamais
    # par le client : sinon n'importe qui pourrait s'abonner à un centime.
    _, plan = _resoudre_plan(request.plan_name)
    montant_centimes = plan["annuel"] if request.is_annual else plan["mensuel"]
    periode = "Annuel" if request.is_annual else "Mensuel"

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
                        'name': f"Abonnement {plan['label']} ({periode})",
                    },
                    'unit_amount': montant_centimes,
                    'recurring': {
                        'interval': 'year' if request.is_annual else 'month',
                    }
                },
                'quantity': 1,
            }],
            mode='subscription',
            metadata={"plan": plan["label"], "periode": periode},
            success_url=settings.FRONTEND_URL + "/app/settings?tab=abonnement&session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.FRONTEND_URL + "/app/settings?tab=abonnement",
            client_reference_id=str(current_user.id),
            # On rattache la session au client existant quand on le connaît :
            # « customer_email » en créerait un nouveau à chaque fois.
            **(
                {"customer": current_user.stripe_customer_id}
                if current_user.stripe_customer_id
                else {"customer_email": current_user.email}
            ),
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def mon_abonnement(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    État de l'abonnement en cours, pour l'onglet Abonnement.

    Renvoyer ces informations évite d'afficher une grille de plans à quelqu'un
    qui est déjà abonné, et permet de lui montrer sa prochaine échéance sans
    l'envoyer sur le portail Stripe.
    """
    abo = await _abonnement_actif(current_user, db)
    if not abo:
        return {"abonne": False}

    donnees = _en_dict(abo)
    lignes = (donnees.get("items") or {}).get("data") or []
    prix = (lignes[0].get("price") or {}) if lignes else {}
    recurrence = (prix.get("recurring") or {}).get("interval")
    montant = prix.get("unit_amount")

    fin = donnees.get("current_period_end")
    return {
        "abonne": True,
        "statut": donnees.get("statut") or donnees.get("status"),
        "plan": "Équipe" if current_user.role == "TEAM" else "Indépendant",
        "annuel": recurrence == "year",
        "montant_centimes": montant,
        # Date du prochain prélèvement, ou de fin de service si une résiliation
        # a été programmée.
        "echeance": (
            datetime.fromtimestamp(fin, timezone.utc).date().isoformat() if fin else None
        ),
        "resiliation_programmee": bool(donnees.get("cancel_at_period_end")),
    }


@router.post("/create-portal-session")
async def create_portal_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Créer une session de portail client Stripe pour gérer l'abonnement."""
    if not settings.STRIPE_SECRET_KEY or settings.STRIPE_SECRET_KEY == "sk_test_placeholder":
        raise HTTPException(status_code=500, detail="La clé secrète Stripe n'est pas configurée.")
        
    customer_id = await _client_stripe(current_user, db)
    if not customer_id:
        raise HTTPException(
            status_code=404,
            detail="Aucun compte client Stripe trouvé pour cet utilisateur.",
        )

    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=settings.FRONTEND_URL + "/app/settings?tab=abonnement",
        )
        return {"portal_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def verifier_signature_stripe(payload: bytes, sig_header: str, chemin: str):
    """
    Valide la signature d'un webhook Stripe contre tous les secrets connus.

    ArtisanGestion reçoit deux flux distincts, chacun depuis son propre
    endpoint Stripe, donc chacun signé avec une clé différente :

      - les abonnements, émis par le compte de la plateforme ;
      - les factures des artisans, émises par leurs comptes Connect.

    On essaie les secrets l'un après l'autre : un événement légitime en
    validera toujours exactement un. Sans cela, la moitié des événements
    seraient rejetés en 400 — un paiement encaissé sans que l'application
    n'en sache rien.
    """
    secrets = settings.STRIPE_WEBHOOK_SECRETS
    if not secrets:
        # Sans secret, un tiers pourrait forger un "checkout.session.completed"
        # et s'attribuer un abonnement ou marquer une facture comme payée.
        logger.error("Aucun secret de webhook Stripe configuré : webhook refusé.")
        raise HTTPException(status_code=503, detail="Webhook non configuré")

    for secret in secrets:
        try:
            return stripe.Webhook.construct_event(payload, sig_header, secret)
        except stripe.error.SignatureVerificationError:
            continue
        except ValueError:
            # Corps illisible : réessayer avec une autre clé ne changerait rien.
            logger.error("Payload webhook Stripe illisible.")
            raise HTTPException(status_code=400, detail="Payload invalide")

    # Cause la plus fréquente : le secret vient d'un autre endpoint ou d'un
    # autre mode (test/live) que la clé API utilisée. Sans abonnement activé
    # après paiement, c'est ici qu'il faut regarder en premier.
    mode_cle = "live" if settings.STRIPE_SECRET_KEY.startswith("sk_live_") else "test"
    logger.error(
        "Signature webhook Stripe invalide sur %s : aucun des %s secret(s) connu(s) "
        "ne correspond. Clé API en mode %s. Vérifiez que STRIPE_WEBHOOK_SECRET "
        "(endpoint compte) et STRIPE_CONNECT_WEBHOOK_SECRET (endpoint Connect) "
        "proviennent bien des endpoints en mode %s "
        "(Dashboard Stripe > Developers > Webhooks).",
        chemin, len(secrets), mode_cle, mode_cle,
    )
    raise HTTPException(status_code=400, detail="Signature invalide")


def _en_dict(objet) -> dict:
    """
    Convertit un objet du SDK Stripe en dictionnaire Python ordinaire.

    Ces objets n'exposent pas `.get()` : `session.get("metadata", {})` lève
    AttributeError et fait échouer le webhook en 500. Stripe réessaie alors
    pendant des jours, l'abonnement ne s'active jamais, et rien dans
    l'application ne le signale. On normalise donc une fois à l'entrée,
    et tout le traitement travaille sur des dictionnaires ordinaires.
    """
    if isinstance(objet, dict):
        return objet
    try:
        return objet.to_dict_recursive()
    except AttributeError:
        try:
            return json.loads(str(objet))
        except (TypeError, ValueError):
            return {}


async def _notifier(coroutine, contexte: str) -> None:
    """
    Envoie un email sans jamais faire échouer le webhook.

    Une erreur ici renverrait 500 à Stripe, qui rejouerait l'événement — et
    l'abonnement serait traité deux fois pour un simple problème d'email.
    """
    try:
        await coroutine
    except Exception:
        logger.exception("Envoi de l'email « %s » échoué.", contexte)


async def _utilisateur_du_client(customer_id: str, db: AsyncSession):
    """Retrouve l'utilisateur ArtisanGestion derrière un client Stripe."""
    if not customer_id:
        return None
    try:
        client = _en_dict(stripe.Customer.retrieve(customer_id))
    except Exception:
        logger.exception("Client Stripe %s illisible.", customer_id)
        return None

    email = client.get("email")
    if not email:
        return None

    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def _retrograder_client(customer_id: str, db: AsyncSession, motif: str) -> None:
    """
    Repasse en USER le titulaire d'un abonnement définitivement terminé.

    `motif` vaut "resiliation" ou "echec_paiement". La distinction n'est pas
    cosmétique : envoyer « désolé de vous voir partir » à quelqu'un dont la
    carte a expiré le pousserait à partir pour de bon, alors qu'il voulait
    rester.
    """
    user = await _utilisateur_du_client(customer_id, db)
    if not user:
        return

    # Déjà rétrogradé : Stripe rejoue parfois un événement, on n'envoie pas
    # le message une seconde fois.
    if user.role not in ("PREMIUM", "TEAM"):
        return

    user.role = "USER"
    await db.commit()
    logger.info("Abonnement terminé pour %s (%s) : retour au rôle USER.", user.email, motif)

    prenom = user.prenom or ""
    if motif == "echec_paiement":
        await _notifier(send_payment_failed(user.email, prenom), "échec de paiement")
    else:
        await _notifier(send_subscription_cancelled(user.email, prenom), "résiliation")


async def _prevenir_echec_paiement(customer_id: str, db: AsyncSession) -> None:
    """
    Signale un prélèvement refusé, sans couper l'accès.

    Stripe relance automatiquement le paiement pendant une quinzaine de jours.
    Bloquer dès le premier refus revient à priver de son outil un artisan qui
    aurait payé au deuxième essai — souvent une carte expirée ou un plafond
    atteint. On l'avertit, et l'accès n'est retiré qu'au statut « unpaid »,
    quand Stripe a épuisé ses relances.
    """
    user = await _utilisateur_du_client(customer_id, db)
    if not user or user.role not in ("PREMIUM", "TEAM"):
        return

    logger.info("Prélèvement refusé pour %s : accès maintenu, relance envoyée.", user.email)
    await _notifier(send_payment_failed(user.email, user.prenom or ""), "échec de paiement")


async def traiter_evenement_stripe(event, db: AsyncSession):
    """
    Traite un événement Stripe déjà authentifié.

    Couvre les deux flux : le paiement d'une facture par le client d'un
    artisan (reconnu à sa métadonnée) et l'abonnement à ArtisanGestion.
    """
    donnees = _en_dict(event)
    type_evenement = donnees.get("type")
    objet = donnees.get("data", {}).get("object") or {}

    if type_evenement == 'checkout.session.completed':
        metadata = objet.get("metadata") or {}

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
                    logger.info("Facture %s marquée payée.", facture.numero_facture)

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
                            logger.warning("Notification WebSocket échouée : %s", ws_err)

        # --- Abonnement classique ---
        else:
            client_reference_id = objet.get("client_reference_id")
            plan_name = metadata.get("plan")

            if client_reference_id and plan_name:
                result = await db.execute(
                    select(User).where(User.id == int(client_reference_id))
                )
                user = result.scalars().first()

                # Un rôle déjà payant signale un événement rejoué par Stripe :
                # on ne renvoie pas la confirmation une seconde fois.
                if user and user.role not in ("PREMIUM", "TEAM"):
                    user.role = "TEAM" if plan_name.strip().lower() in ("équipe", "equipe") else "PREMIUM"
                    # Mémorisé ici : c'est le seul endroit où Stripe nous donne
                    # le client réellement utilisé pour ce paiement.
                    if objet.get("customer"):
                        user.stripe_customer_id = objet["customer"]
                    await db.commit()
                    logger.info(
                        "Abonnement %s activé pour %s (rôle %s).",
                        plan_name, user.email, user.role,
                    )

                    montant = objet.get("amount_total")
                    await _notifier(
                        send_subscription_confirmation(
                            user.email,
                            user.prenom or "",
                            plan_name,
                            metadata.get("periode") or "",
                            f"{montant / 100:.2f} €".replace(".", ",") if montant else "",
                        ),
                        "confirmation d'abonnement",
                    )

    elif type_evenement in ('customer.subscription.deleted', 'customer.subscription.canceled'):
        await _retrograder_client(objet.get("customer"), db, "resiliation")

    elif type_evenement == 'customer.subscription.updated':
        # Résiliation, impayé ou prélèvement en échec : l'accès se referme.
        statut = objet.get("status")
        client = objet.get("customer")

        # Stripe émet cet événement pour toute modification de l'abonnement,
        # y compris un simple changement de carte. `previous_attributes` liste
        # les champs qui ont réellement changé : sans ce filtre, une mise à
        # jour anodine déclencherait un email.
        precedent = (donnees.get("data") or {}).get("previous_attributes") or {}
        if "status" not in precedent:
            return

        if statut == 'canceled':
            await _retrograder_client(client, db, "resiliation")
        elif statut == 'unpaid':
            # Stripe a épuisé ses relances : l'accès se referme.
            await _retrograder_client(client, db, "echec_paiement")
        elif statut == 'past_due':
            # Relances en cours : on prévient sans couper.
            await _prevenir_echec_paiement(client, db)

    elif type_evenement == 'account.updated':
        # Stripe Connect : mise à jour du statut du compte d'un artisan.
        account_id = objet.get("id")

        if account_id:
            from app.models.societe import Societe as SocieteModel

            result = await db.execute(
                select(SocieteModel).where(
                    SocieteModel.stripe_connect_account_id == account_id
                )
            )
            societe = result.scalars().first()

            if societe:
                societe.stripe_connect_enabled = bool(
                    objet.get("charges_enabled") and objet.get("payouts_enabled")
                )
                societe.stripe_connect_onboarding_complete = bool(
                    objet.get("details_submitted")
                )
                await db.commit()

    else:
        logger.debug("Événement Stripe ignoré : %s", type_evenement)


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Point d'entrée unique des webhooks Stripe.

    Les deux endpoints déclarés dans Stripe — celui du compte et celui de
    Connect — pointent vers cette URL. Le gestionnaire reconnaît le type
    d'événement, il n'a pas besoin de savoir d'où il vient.
    """
    payload = await request.body()
    event = verifier_signature_stripe(
        payload, request.headers.get("stripe-signature"), request.url.path
    )
    await traiter_evenement_stripe(event, db)
    return {"status": "success"}

