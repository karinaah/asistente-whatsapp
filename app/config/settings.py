from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Asistente WhatsApp"
    app_version: str = "0.1.0"
    environment: str = "development"

    # Mientras no tengamos billing, trabajaremos en modo simulado.
    openai_api_key: str | None = None
    use_mock_ai: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()