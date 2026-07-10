from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    AI_API_KEY: str | None = None
    AI_MODEL: str = "gpt-4o-mini"
    AI_PROVIDER: str = "openai"
    AI_ENABLED: bool = False

    # Groq — powers the conversational chat assistant (OpenAI-compatible, fast inference)
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    class Config:
        env_file = ".env"


settings = Settings()
