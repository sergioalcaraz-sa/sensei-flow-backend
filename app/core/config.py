# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Pydantic buscará automáticamente estas variables en el entorno o el .env
    
    # Groq
    GROQ_API_KEY: str = Field(..., alias="GROQ_API_KEY")
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    TEMPERATURE: float = 0.0
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # API Metadata
    PROJECT_NAME: str = "Sensei-Flow AI"
    DEBUG: bool = False

    # Configuración para leer el archivo .env desde la raíz
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" # Ignora variables extra en el .env que no estén aquí
    )

settings = Settings()