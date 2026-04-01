import os

class Settings:
    PROJECT_NAME: str = "Ventura API"
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "ventura")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "ventura")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ventura")

    @property
    def DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
