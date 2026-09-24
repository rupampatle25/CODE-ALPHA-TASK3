import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sargam AI"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sargam-insecure-secret-key-change-in-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'sargam.db'}")

    # Storage paths
    STORAGE_DIR: Path = BASE_DIR / "storage"
    MIDI_STORAGE_DIR: Path = BASE_DIR / "storage" / "midi"
    AUDIO_STORAGE_DIR: Path = BASE_DIR / "storage" / "audio"
    CHECKPOINTS_DIR: Path = BASE_DIR / "ai" / "checkpoints"

    # Plan credits
    DEFAULT_FREE_CREDITS: int = 10
    CREATOR_CREDITS: int = 250

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    class Config:
        case_sensitive = True

settings = Settings()

# Ensure directories exist
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
settings.MIDI_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
settings.AUDIO_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
settings.CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
