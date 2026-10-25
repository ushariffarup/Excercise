import os
from pathlib import Path
from dotenv import load_dotenv
from app.errors import ConfigurationError
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url: raise ConfigurationError("DATABASE_URL is not set. Copy .env.example to .env and fill it in.")
    return url

def get_dataset_path() -> Path:
    path = Path(os.getenv("DATASET_PATH", "data/diabetic_data.csv"))
    return path if path.is_absolute() else PROJECT_ROOT / path

APP_NAME = os.getenv("APP_NAME", "Diabetes Readmission Intervention Queue")
APP_ENV = os.getenv("APP_ENV", "local")

DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,null"

def get_cors_origins() -> list:
    """Comma-separated list from CORS_ORIGINS; defaults to the local Vite/React dev servers."""
    return [origin.strip() for origin in os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",") if origin.strip()]
