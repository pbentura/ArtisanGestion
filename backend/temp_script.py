import asyncio
import os
from dotenv import load_dotenv

load_dotenv("../.env")

from app.core.database import AsyncSessionLocal
from app.models.rapport import Rapport
from sqlalchemy.future import select

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Rapport).order_by(Rapport.id.desc()).limit(1))
        rapport = result.scalars().first()
        if rapport:
            print('Contenu:', repr(rapport.contenu))
            print('Photos:', repr(rapport.photos))
            print('Photo URL:', repr(rapport.photo_url))
        else:
            print('No rapport found')

asyncio.run(main())
