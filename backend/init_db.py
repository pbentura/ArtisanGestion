import asyncio
from app.core.database import engine, Base
from app.models.user import User
from app.models.societe import Societe
from app.models.client import Client
from app.models.rapport import Rapport
from app.models.devis import Devis
from app.models.ligne_devis import LigneDevis
from app.models.facture import Facture
from app.models.ligne_facture import LigneFacture

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
