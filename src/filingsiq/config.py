from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://filings:filings@localhost:5432/filingsiq"
    redis_url: str = "redis://localhost:6379/0"
    anthropic_api_key: str = ""
    sec_user_agent: str = ""
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_provider: str = "local"
    retrieval_backend: str = "postgres"
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 384


settings = Settings()
