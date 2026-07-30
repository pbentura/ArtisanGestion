import os
from dotenv import load_dotenv, find_dotenv

# Load .env file from the root directory
load_dotenv(find_dotenv())

class Settings:
    PROJECT_NAME: str = "ArtisanGestion API"
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "ventura")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "ventura")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ventura")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "b443ad5a4bc032128711bd420fc28ddfd30431ae18742d48dce6db3cbeedb95f")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    _CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
    CORS_ORIGINS: list[str] = [origin.strip() for origin in _CORS_ORIGINS.split(",")]
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "https://ventura.pbentura.cloud/api/auth/google/callback")

    # Mistral AI
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")

    @property
    def DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
