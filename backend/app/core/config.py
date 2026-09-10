from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'sqlite:///./qms.db'
    frontend_origin: str = 'http://localhost:5173'
    llm_provider: str = 'groq'
    groq_api_key: str | None = None
    groq_model: str = 'llama-3.1-8b-instant'
    gemini_api_key: str | None = None
    gemini_model: str = 'gemini-2.5-flash'
settings = Settings()
