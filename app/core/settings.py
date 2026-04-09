from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    app_env: str
    app_debug: bool

    database_url: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    bootstrap_superadmin_secret: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()