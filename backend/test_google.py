import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User
from app.models.societe import Societe
from app.models.client import Client
from app.models.rapport import Rapport
from app.models.devis import Devis
from app.models.facture import Facture
from app.services.email_service import send_welcome_email

async def main():
    engine = create_async_engine(settings.DATABASE_URI)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        user = User(
            email="test_google3@example.com",
            nom="Test",
            prenom="Google",
            mdp=None,
            role="USER",
            is_email_verified=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        print("User inserted!")
        
        await send_welcome_email("test_google3@example.com", "Google")
        print("Email sent!")

asyncio.run(main())
