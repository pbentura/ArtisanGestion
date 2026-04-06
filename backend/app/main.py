from typing import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.models.user import User
from app.models.societe import Societe
from app.models.client import Client
from app.models.rapport import Rapport

from app.api.endpoints import auth, users, societes, clients, rapports, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Base.metadata.create_all is now handled by Alembic migrations
    yield

app = FastAPI(title="Ventura API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(societes.router, prefix="/api/societes", tags=["societes"])
app.include_router(clients.router, prefix="/api/clients", tags=["clients"])
app.include_router(rapports.router, prefix="/api/rapports", tags=["rapports"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
async def hello_world():
    return {"message": "Hello from Ventura Backend!"}

@app.get("/health")
async def health():
    return {"status": "ok"}
