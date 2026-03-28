from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "YC Startup Research Agent"
    environment: str = "development"
    frontend_url: str = "http://127.0.0.1:3000"
    yc_companies_url: str = "https://www.ycombinator.com/companies"
    yc_company_base_url: str = "https://www.ycombinator.com/companies/"
    request_timeout_seconds: float = 20.0
    startup_limit: int = 5
    memory_file_path: str = "MEMORY.md"
    market_guide_file_path: str = "MARKET.md"
    llm_provider: str = Field(default="openai", validation_alias=AliasChoices("LLM_PROVIDER"))
    llm_model: str = Field(
        default="gpt-4.1-mini",
        validation_alias=AliasChoices("LLM_MODEL", "OPENAI_MODEL"),
    )
    llm_max_output_tokens: int = Field(
        default=800,
        validation_alias=AliasChoices("LLM_MAX_OUTPUT_TOKENS", "OPENAI_MAX_OUTPUT_TOKENS"),
    )
    openai_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_API_KEY"),
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
