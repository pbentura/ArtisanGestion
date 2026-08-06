from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr

from app.api.deps import get_db
from app.core.config import settings
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

@router.get("/google/login")
async def google_login(request: Request, platform: str = "web"):
    """
    Initie le flux de connexion Google.
    """
    # Stocker la plateforme dans la session pour s'en souvenir lors du callback
    request.session['auth_platform'] = platform
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
    
    # Rediriger vers le frontend avec le token
    frontend_url = "https://artisangestion.com"
    if "localhost" in str(request.base_url):
        frontend_url = "http://localhost:5173"
        
    # Récupérer la plateforme depuis la session
    platform = request.session.pop('auth_platform', 'web')
    
    # Si on est sur mobile, on redirige vers le schéma d'URL personnalisé de l'app
    if platform == 'mobile':
        # On utilise le schéma d'URL de l'application Capacitor
        return RedirectResponse(url=f"com.artisangestion.app://auth?token={access_token}")
        
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
            
            try {{
                // Si ouvert dans une popup, on envoie le token à la fenêtre parente
                if (window.opener && window.opener !== window) {{
                    window.opener.postMessage({{ type: 'google-auth-success', token: token }}, frontendUrl);
                    // On laisse un petit délai pour être sûr que le message est envoyé avant de fermer
                    setTimeout(() => window.close(), 200);
                }} else {{
                    // Sinon (redirection classique), on redirige directement
                    window.location.href = frontendUrl + "/app/dashboard?token=" + token;
                }}
            }} catch (e) {{
                console.error("Erreur lors de la finalisation de l'auth:", e);
                window.location.href = frontendUrl + "/app/dashboard?token=" + token;
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# ── Registration ──

@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> Any:
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
async def login(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
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
async def resend_verification(
    body: ResendVerificationRequest, db: AsyncSession = Depends(get_db)
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
async def forgot_password(
    body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)
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
async def reset_password(
    body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
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
