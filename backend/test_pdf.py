import asyncio
import os
from dotenv import load_dotenv

load_dotenv("../.env.production")

from app.core.database import AsyncSessionLocal
from app.models.rapport import Rapport
from app.models.client import Client
from app.models.societe import Societe
from app.models.user import User
from app.models.devis import Devis
from app.models.facture import Facture
from app.models.facture_ligne import LigneFacture
from app.models.devis_ligne import LigneDevis

from sqlalchemy.future import select

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Rapport).order_by(Rapport.id.desc()).limit(1))
        rapport = result.scalars().first()
        if rapport:
            print("--- ORIGINAL HTML ---")
            print(repr(rapport.contenu))
        else:
            print('No rapport found')

asyncio.run(main())
