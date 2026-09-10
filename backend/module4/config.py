import os
from typing import Optional
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    
    class Settings(BaseSettings):
        LLM_PROVIDER: str = "mock"  # Options: "mock", "gemini", "openai"
        GEMINI_API_KEY: Optional[str] = None
        OPENAI_API_KEY: Optional[str] = None
        GEMINI_MODEL: str = "gemini-2.5-flash"
        OPENAI_MODEL: str = "gpt-4o-mini"
        CONFIDENCE_THRESHOLD: float = 0.70

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore"
        )
            
    settings = Settings()

except ImportError:
    class Settings:
        LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")
        GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
        OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
        GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.70"))

    settings = Settings()
