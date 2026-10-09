from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://miaoyi:miaoyi@db:5432/miaoyi"
    redis_url: str = "redis://redis:6379/0"
    openai_api_key: str = ""
    chat_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    supabase_jwt_secret: str = ""
    google_vision_api_key: str = ""
    r2_endpoint: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket: str = "miaoyi-uploads"
    rate_limit_per_minute: int = 20


settings = Settings()
