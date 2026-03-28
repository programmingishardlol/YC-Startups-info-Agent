from typing import Protocol

from app.models.startup import StartupExtractionResult, StartupProfileRaw
from app.services.memory import MemoryContext


class StartupLLMProvider(Protocol):
    async def extract_profile(
        self,
        raw_profile: StartupProfileRaw,
        memory_context: MemoryContext,
        market_guide: str,
    ) -> StartupExtractionResult:
        """Extract structured fields from a raw startup profile."""
