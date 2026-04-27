from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead
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

@router.get("/google/login")
async def google_login(request: Request):
    """
    Initie le flux de connexion Google.
    """
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
    
    if not user:
        # Créer un nouvel utilisateur s'il n'existe pas
        user = User(
            email=email,
            nom=nom,
            prenom=prenom,
            mdp=None,  # Pas de mot de passe pour les comptes Google
            role="USER"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    # Générer le token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Rediriger vers le frontend avec le token
    frontend_url = "https://ventura-e277f.web.app"
    if "localhost" in str(request.base_url):
        frontend_url = "http://localhost:5173"
        
    # Retourner une page HTML qui communique avec la fenêtre parente (popup)
    # ou redirige si ouvert directement
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Authentification réussie | Ventura</title>
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
                    window.location.href = frontendUrl + "/dashboard?token=" + token;
                }}
            }} catch (e) {{
                console.error("Erreur lors de la finalisation de l'auth:", e);
                window.location.href = frontendUrl + "/dashboard?token=" + token;
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> Any:
    """
    Créer un nouvel utilisateur.
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="Cet email est déjà utilisé.",
        )
    
    # Create new user instance
    new_user = User(
        nom=user_in.nom,
        prenom=user_in.prenom,
        email=user_in.email,
        mdp=get_password_hash(user_in.mdp)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

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
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
