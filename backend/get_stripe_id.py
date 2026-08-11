import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings

async def main():
    engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        result = await session.execute(text("SELECT id, nom, stripe_connect_account_id FROM societe WHERE stripe_connect_account_id IS NOT NULL;"))
        for row in result:
            print(f"ID: {row[0]}, Nom: {row[1]}, Stripe ID: {row[2]}")

if __name__ == "__main__":
    asyncio.run(main())
