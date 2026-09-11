from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'sqlite:///./qms.db'
    frontend_origin: str = 'http://localhost:5173'
    llm_provider: str = 'gemini'
    groq_api_key: str | None = None
    groq_model: str = 'openai/gpt-oss-20b'
    gemini_api_key: str | None = None
    gemini_model: str = 'gemini-3.7-flash'
    gemini_fallback_model: str = 'gemini-2.5-flash'
    gemini_base_url: str = 'https://generativelanguage.googleapis.com'
settings = Settings()
