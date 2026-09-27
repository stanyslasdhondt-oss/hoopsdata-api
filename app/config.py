from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./hoopsdata.db"
    app_env: str = "dev"
    cors_origins: list[str] = ["http://localhost:5173"]
    r2_endpoint: str | None = None
    r2_access_key_id: str | None = None
    r2_secret_access_key: str | None = None
    r2_bucket: str | None = None
    storage_backend: str = "fake"
    model_config = {
        "env_file": ".env"
    }  # to find the .env info if not in the environment system


settings = Settings()
