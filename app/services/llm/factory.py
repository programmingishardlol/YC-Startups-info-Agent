from app.core.config import Settings
from app.services.llm.base import StartupLLMProvider
from app.services.llm.errors import StartupExtractionError
from app.services.llm.openai_provider import OpenAIStartupLLMProvider


def build_startup_llm_provider(settings: Settings) -> StartupLLMProvider:
    provider_name = settings.llm_provider.strip().lower()

    if provider_name == "openai":
        return OpenAIStartupLLMProvider(settings)

    raise StartupExtractionError(
        f"Unsupported LLM provider '{settings.llm_provider}'. Configure LLM_PROVIDER=openai."
    )
