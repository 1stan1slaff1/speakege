from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "speakege"
    DATABASE_URL: str
    JWT_SECRET: str
    GROQ_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    AZURE_SPEECH_KEY: str | None = None
    AZURE_SPEECH_REGION: str | None = None
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"

settings = Settings()
