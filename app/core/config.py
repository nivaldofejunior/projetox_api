from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega as variáveis do .env manualmente

class Settings(BaseSettings):
    PROJECT_NAME: str = "Projeto X"
    DB_URL: str
    JWT_SECRET: str = "secret"
    GROQ_API_KEY: str

    class Config:
        env_file = ".env"
        extra = "ignore"
        case_sensitive = False

settings = Settings()
