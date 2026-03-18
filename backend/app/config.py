from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://clinic:clinic@localhost:5432/clinicdb"

    # JWT
    secret_key: str = "supersecretkey-change-in-prod"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # App
    app_name: str = "The Clinic App API"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost", "http://localhost:3000", "http://localhost:8080"]

    # Seed passwords (used by test framework)
    admin_password: str = "Admin1234!"
    doctor_password: str = "Doctor1234!"
    patient_password: str = "Patient1234!"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
