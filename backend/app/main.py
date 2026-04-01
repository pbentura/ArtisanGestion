from typing import AsyncGenerator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.models.user import User
from app.models.societe import Societe

from app.api.endpoints import auth, users, societes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Base.metadata.create_all is now handled by Alembic migrations
    yield

app = FastAPI(title="Ventura API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(societes.router, prefix="/api/societes", tags=["societes"])

@app.get("/")
async def hello_world():
    return {"message": "Hello from Ventura Backend!"}

@app.get("/health")
async def health():
    return {"status": "ok"}
