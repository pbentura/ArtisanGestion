import os
from dotenv import load_dotenv, find_dotenv

# Load .env file from the root directory
load_dotenv(find_dotenv())

class Settings:
    PROJECT_NAME: str = "ArtisanGestion API"
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "artisangestion")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "artisangestion")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "artisangestion")
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    _CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,https://artisangestion.com")
    CORS_ORIGINS: list[str] = [origin.strip() for origin in _CORS_ORIGINS.split(",")]
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback")

    # Mistral AI
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")

    # Resend (Emails)
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "onboarding@resend.dev")
    SUPPORT_EMAIL: str = os.getenv("SUPPORT_EMAIL", "pinhasbent@gmail.com")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = int(os.getenv("EMAIL_VERIFICATION_EXPIRE_HOURS", "48"))
    PASSWORD_RESET_EXPIRE_MINUTES: int = int(os.getenv("PASSWORD_RESET_EXPIRE_MINUTES", "30"))

    # Stripe
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_CONNECT_COMMISSION_PERCENT: float = float(os.getenv("STRIPE_CONNECT_COMMISSION_PERCENT", "1.5"))

    @property
    def DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def validate(self) -> None:
        """
        Vérifie au démarrage que la configuration est exploitable.
        Mieux vaut refuser de démarrer que tourner avec des secrets de repli.
        """
        if not self.SECRET_KEY:
            raise RuntimeError(
                "SECRET_KEY est absente de l'environnement. "
                "Générez-en une avec `openssl rand -hex 32` et ajoutez-la au fichier .env."
            )

        if self.ENVIRONMENT != "production":
            return

        # Variables sans lesquelles la production est cassée ou non sécurisée
        requises = {
            "STRIPE_SECRET_KEY": self.STRIPE_SECRET_KEY,
            "STRIPE_WEBHOOK_SECRET": self.STRIPE_WEBHOOK_SECRET,
            "RESEND_API_KEY": self.RESEND_API_KEY,
            "GOOGLE_CLIENT_ID": self.GOOGLE_CLIENT_ID,
            "GOOGLE_CLIENT_SECRET": self.GOOGLE_CLIENT_SECRET,
        }
        manquantes = [nom for nom, valeur in requises.items() if not valeur]
        if manquantes:
            raise RuntimeError(
                "Variables d'environnement manquantes en production : "
                + ", ".join(manquantes)
            )

        if len(self.SECRET_KEY) < 32:
            raise RuntimeError("SECRET_KEY doit faire au moins 32 caractères en production.")

        if self.STRIPE_SECRET_KEY.startswith("sk_test_"):
            raise RuntimeError(
                "STRIPE_SECRET_KEY est une clé de test alors que ENVIRONMENT=production."
            )

settings = Settings()
settings.validate()
