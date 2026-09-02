import re
from datetime import timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr

from app.api.deps import get_db
from app.core.config import settings
from app.core.rate_limit import limiter
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    create_email_verification_token,
    verify_email_token,
    create_password_reset_token,
    verify_password_reset_token,
    create_waiting_token,
)
from app.models.user import User
from app.models.invitation import Invitation
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead, UserRegisterResponse
from app.services.email_service import (
    send_welcome_email,
    send_verification_email,
    send_password_reset_email,
)
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse

router = APIRouter()

oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


# ── Pydantic schemas for new endpoints ──

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr


# ── Google OAuth ──

def _origine_autorisee(origine: str) -> Optional[str]:
    """
    Ne retient une origine que si elle figure dans la liste CORS (ou si c'est un
    localhost en développement). Le jeton d'accès est renvoyé à cette origine
    précise : accepter n'importe laquelle reviendrait à le diffuser à tous.
    """
    if not origine:
        return None
    origine = origine.rstrip("/")
    autorisees = {o.rstrip("/") for o in settings.CORS_ORIGINS if o}
    if origine in autorisees:
        return origine
    if settings.ENVIRONMENT != "production" and re.match(
        r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$", origine
    ):
        return origine
    return None


@router.get("/google/login")
async def google_login(request: Request, platform: str = "web", origin: str = ""):
    """
    Initie le flux de connexion Google.

    `origin` est l'origine de la page qui a ouvert la popup. Elle est validée ici
    puis réutilisée au retour pour cibler le postMessage.
    """
    # Stocker la plateforme dans la session pour s'en souvenir lors du callback
    request.session['auth_platform'] = platform
    request.session['auth_origin'] = _origine_autorisee(origin) or ""
    return await oauth.google.authorize_redirect(request, settings.GOOGLE_REDIRECT_URI)

@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Gère le retour de Google après l'authentification.
    """
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Échec de l'authentification Google: {str(e)}")
        
    user_info = token.get('userinfo')
    if not user_info:
        raise HTTPException(status_code=400, detail="Impossible de récupérer les infos utilisateur Google")
    
    email = user_info['email']
    nom = user_info.get('family_name', '')
    prenom = user_info.get('given_name', '')
    
    # Vérifier si l'utilisateur existe déjà
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    is_new_user = False
    if not user:
        # Créer un nouvel utilisateur s'il n'existe pas
        # Les comptes Google sont automatiquement vérifiés
        user = User(
            email=email,
            nom=nom,
            prenom=prenom,
            mdp=None,  # Pas de mot de passe pour les comptes Google
            role="USER",
            is_email_verified=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        is_new_user = True
    
    # Envoyer l'email de bienvenue pour les nouveaux utilisateurs Google
    if is_new_user:
        await send_welcome_email(email, prenom)
    
    # Générer le token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Récupérer la plateforme et l'origine validée depuis la session
    platform = request.session.pop('auth_platform', 'web')
    origine_validee = request.session.pop('auth_origin', '') or ''

    # Origine cible du postMessage : celle d'où vient l'utilisateur si elle a été
    # validée à l'aller, sinon le frontend configuré. Jamais "*".
    frontend_url = (
        origine_validee
        or (settings.FRONTEND_URL.rstrip('/') if settings.FRONTEND_URL else "http://localhost:5173")
    )
    
    # « Ce compte vient d'être créé » : le frontend en a besoin pour déclencher
    # la conversion d'inscription. Sans cela, une inscription via Google est
    # indiscernable d'une reconnexion et n'est jamais comptabilisée.
    nouveau = "1" if is_new_user else "0"

    # Si on est sur mobile, on redirige vers le schéma d'URL personnalisé de l'app
    if platform == 'mobile':
        # On utilise le schéma d'URL de l'application Capacitor
        return RedirectResponse(
            url=f"com.artisangestion.app://auth?token={access_token}&nouveau={nouveau}"
        )
        
    # Retourner une page HTML qui communique avec la fenêtre parente (popup)
    # ou redirige si ouvert directement
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Authentification réussie | ArtisanGestion</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                background-color: #ffffff;
                color: #111827;
            }}
            .loader {{
                border: 3px solid #f3f3f3;
                border-top: 3px solid #3b82f6;
                border-radius: 50%;
                width: 32px;
                height: 32px;
                animation: spin 1s linear infinite;
                margin-bottom: 16px;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .text {{ font-size: 1rem; font-weight: 500; color: #4b5563; }}
        </style>
    </head>
    <body>
        <div class="loader"></div>
        <div class="text">Connexion réussie, redirection...</div>
        <script>
            const token = "{access_token}";
            const frontendUrl = "{frontend_url}";
            const nouveau = "{nouveau}" === "1";
            
            try {{
                // Si ouvert dans une popup, on envoie le token à la fenêtre parente
                if (window.opener && window.opener !== window) {{
                    // Origine explicite : avec '*', le jeton serait remis à
                    // n'importe quelle page ayant ouvert cette popup.
                    window.opener.postMessage({{ type: 'google-auth-success', token: token, nouveau: nouveau }}, frontendUrl);
                    // On laisse un petit délai pour être sûr que le message est envoyé avant de fermer
                    setTimeout(() => window.close(), 300);
                }} else {{
                    // Sinon (redirection classique), on redirige directement
                    window.location.href = frontendUrl + "/app/dashboard?token=" + token + (nouveau ? "&nouveau=1" : "");
                }}
            }} catch (e) {{
                console.error("Erreur lors de la finalisation de l'auth:", e);
                window.location.href = frontendUrl + "/app/dashboard?token=" + token + (nouveau ? "&nouveau=1" : "");
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# ── Registration ──

@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")
async def register(request: Request, user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> Any:
    """
    Créer un nouvel utilisateur et envoyer les emails de bienvenue et de vérification.
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="Cet email est déjà utilisé.",
        )
    
    # Generate email verification token
    verification_token = create_email_verification_token(user_in.email)
    
    # Create new user instance
    new_user = User(
        nom=user_in.nom,
        prenom=user_in.prenom,
        email=user_in.email,
        mdp=get_password_hash(user_in.mdp),
        is_email_verified=False,
        email_verification_token=verification_token,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Send only verification email initially
    await send_verification_email(user_in.email, user_in.prenom, verification_token)
    
    waiting_token = create_waiting_token(user_in.email)
    
    return {
        "user": new_user,
        "waiting_token": waiting_token
    }


# ── Login ──

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    Connecter un utilisateur et obtenir un jeton JWT.
    """
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.mdp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Veuillez vérifier votre adresse email avant de vous connecter.",
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ── Email Verification ──

@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Vérifie l'adresse email de l'utilisateur via le token envoyé par email.
    """
    email = verify_email_token(token)
    if not email:
        raise HTTPException(
            status_code=400,
            detail="Le lien de vérification est invalide ou a expiré.",
        )
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    
    if user.is_email_verified:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {
            "message": "Votre adresse email est déjà vérifiée.",
            "access_token": access_token,
            "token_type": "bearer",
        }
    
    user.is_email_verified = True
    user.email_verification_token = None
    db.add(user)
    await db.commit()
    
    # Envoyer l'email de bienvenue maintenant que l'email est vérifié
    await send_welcome_email(user.email, user.prenom)
    
    # Générer le token JWT pour auto-login
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    from app.core.websockets import manager
    await manager.broadcast_to_user(user.id, {
        "type": "EMAIL_VERIFIED",
    })
    
    return {
        "message": "Votre adresse email a été vérifiée avec succès !",
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/resend-verification")
@limiter.limit("3/hour")
async def resend_verification(
    request: Request, body: ResendVerificationRequest, db: AsyncSession = Depends(get_db)
):
    """
    Renvoie l'email de vérification si l'utilisateur n'est pas encore vérifié.
    Retourne toujours 200 pour ne pas révéler si l'email existe.
    """
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalars().first()
    
    if user and not user.is_email_verified:
        verification_token = create_email_verification_token(user.email)
        user.email_verification_token = verification_token
        db.add(user)
        await db.commit()
        
        await send_verification_email(user.email, user.prenom or "", verification_token)
    
    return {"message": "Si un compte existe avec cet email, un nouveau lien de vérification a été envoyé."}


# ── Password Reset ──

@router.post("/forgot-password")
@limiter.limit("3/hour")
async def forgot_password(
    request: Request, body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)
):
    """
    Envoie un email de réinitialisation de mot de passe.
    Retourne toujours 200 pour ne pas révéler si l'email existe.
    """
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalars().first()
    
    if user:
        # Ne pas permettre le reset pour les comptes Google (pas de mot de passe)
        if user.mdp is None:
            return {"message": "Si un compte existe avec cet email, un lien de réinitialisation a été envoyé."}
        
        reset_token = create_password_reset_token(user.email)
        user.password_reset_token = reset_token
        db.add(user)
        await db.commit()
        
        await send_password_reset_email(user.email, user.prenom or "", reset_token)
    
    return {"message": "Si un compte existe avec cet email, un lien de réinitialisation a été envoyé."}


@router.post("/reset-password")
@limiter.limit("10/hour")
async def reset_password(
    request: Request, body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    """
    Réinitialise le mot de passe de l'utilisateur avec un nouveau mot de passe.
    """
    email = verify_password_reset_token(body.token)
    if not email:
        raise HTTPException(
            status_code=400,
            detail="Le lien de réinitialisation est invalide ou a expiré.",
        )
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    
    # Vérifier que le token correspond à celui stocké en DB (invalidation single-use)
    if user.password_reset_token != body.token:
        raise HTTPException(
            status_code=400,
            detail="Ce lien de réinitialisation a déjà été utilisé.",
        )
    
    # Mettre à jour le mot de passe
    user.mdp = get_password_hash(body.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    db.add(user)
    await db.commit()
    
    return {"message": "Votre mot de passe a été réinitialisé avec succès."}


# ── Collaborateur Registration ──

class RegisterCollaborateurRequest(BaseModel):
    token: str
    nom: str
    prenom: str
    email: EmailStr
    mdp: str


@router.post("/register-collaborateur", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_collaborateur(
    body: RegisterCollaborateurRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Inscription d'un collaborateur via un magic link.
    Pas besoin de créer d'entreprise, il est automatiquement rattaché.
    """
    # 1. Vérifier le token d'invitation
    from datetime import datetime, timezone
    result = await db.execute(
        select(Invitation).where(Invitation.token == body.token)
    )
    invitation = result.scalars().first()

    if not invitation:
        raise HTTPException(400, "Lien d'invitation invalide.")

    if invitation.status != "pending":
        raise HTTPException(400, "Cette invitation a déjà été utilisée.")

    expires_at = invitation.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        invitation.status = "expired"
        await db.commit()
        raise HTTPException(400, "Cette invitation a expiré.")

    # 1 bis. Si l'invitation cible une adresse précise, l'inscription doit s'y
    # conformer : sinon toute personne disposant du lien pourrait rejoindre
    # l'entreprise avec l'adresse de son choix.
    if invitation.email and invitation.email.strip().lower() != body.email.strip().lower():
        raise HTTPException(
            400,
            "Cette invitation est réservée à l'adresse email à laquelle elle a été envoyée.",
        )

    # 2. Vérifier que l'email n'est pas déjà utilisé
    result = await db.execute(select(User).where(User.email == body.email))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(400, "Cet email est déjà utilisé.")

    # 3. Créer l'utilisateur collaborateur
    new_user = User(
        nom=body.nom,
        prenom=body.prenom,
        email=body.email,
        mdp=get_password_hash(body.mdp),
        role="USER",
        is_email_verified=True,  # Pas besoin de vérifier, le magic link fait office
        id_societe=invitation.id_societe,
        is_owner=False,
        can_create_rapports=invitation.can_create_rapports,
        can_create_clients=invitation.can_create_clients,
        can_create_devis=invitation.can_create_devis,
        can_create_factures=invitation.can_create_factures,
        can_invite=invitation.can_invite,
        can_edit_societe=invitation.can_edit_societe,
    )
    db.add(new_user)

    # 4. Marquer l'invitation comme acceptée
    invitation.status = "accepted"
    db.add(invitation)

    await db.commit()
    await db.refresh(new_user)

    # 5. Envoyer l'email de bienvenue
    await send_welcome_email(body.email, body.prenom)

    # 6. Générer le token JWT pour auto-login
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

