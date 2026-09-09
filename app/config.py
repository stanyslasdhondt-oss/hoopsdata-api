from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./hoopsdata.db"
    app_env: str = "dev"
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = {
        "env_file": ".env"
    }  # to find the .env info if not in the environment system


settings = Settings()
