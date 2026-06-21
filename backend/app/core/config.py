from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Production RAG Platform"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://rag:rag@postgres:5432/rag"
    chroma_host: str = "chroma"
    chroma_port: int = 8000
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    upload_dir: str = "/tmp/rag_uploads"
    openai_api_key: str | None = None
    langsmith_tracing: bool = False
    langsmith_project: str = "production-rag-platform"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
