from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/learnsight.db"
    jwt_secret: str = "development-secret-change-me"
    cors_origins: str = "http://localhost:5173"
    tesseract_cmd: str = ""
    upload_dir: str = "../uploads"
    model_dir: str = "../models"
    max_upload_mb: int = 10
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
Path("data").mkdir(exist_ok=True)
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path("../reports").mkdir(parents=True, exist_ok=True)
