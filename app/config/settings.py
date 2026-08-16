import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    app_name: str = os.getenv("APP_NAME", "AURA")
    app_version: str = os.getenv("APP_VERSION", "1.1.0")
    environment: str = os.getenv("ENVIRONMENT", "development")

    USE_MOCK_AI: bool = (
        os.getenv("USE_MOCK_AI", "true").lower() == "true"
    )

    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")


settings = Settings()