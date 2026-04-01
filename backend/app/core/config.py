import os

class Settings:
    PROJECT_NAME: str = "Ventura API"
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "ventura")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "ventura")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ventura")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "b443ad5a4bc032128711bd420fc28ddfd30431ae18742d48dce6db3cbeedb95f")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    @property
    def DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
