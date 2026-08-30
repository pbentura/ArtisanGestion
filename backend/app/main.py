from typing import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.core.rate_limit import limiter
from app.models.user import User
from app.models.societe import Societe
from app.models.client import Client
from app.models.rapport import Rapport
from app.models.devis import Devis
from app.models.ligne_devis import LigneDevis
from app.models.facture import Facture
from app.models.ligne_facture import LigneFacture
from app.models.invitation import Invitation

from app.api.endpoints import auth, users, societes, clients, rapports, admin, ai, devis, factures, dashboard, ws, subscriptions, emails, collaborateurs, stripe_connect, webhooks

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Base.metadata.create_all is now handled by Alembic migrations
    yield

app = FastAPI(title="ArtisanGestion API", lifespan=lifespan)

# Limitation de débit : les plafonds sont posés route par route (@limiter.limit)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(societes.router, prefix="/api/societes", tags=["societes"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(rapports.router, prefix="/api/rapports", tags=["rapports"])
app.include_router(devis.router, prefix="/api/devis", tags=["devis"])
app.include_router(factures.router, prefix="/api/factures", tags=["factures"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(ws.router, prefix="/api/ws", tags=["websocket"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["subscriptions"])
app.include_router(emails.router, prefix="/api/emails", tags=["emails"])
app.include_router(collaborateurs.router, prefix="/api/collaborateurs", tags=["collaborateurs"])
app.include_router(stripe_connect.router, prefix="/api/stripe-connect", tags=["stripe-connect"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])


@app.get("/")
async def hello_world():
    return {"message": "Hello from ArtisanGestion Backend!"}

@app.get("/health")
async def health():
    return {"status": "ok"}
