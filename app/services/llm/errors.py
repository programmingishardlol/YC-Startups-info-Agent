class StartupExtractionError(Exception):
    """Raised when LLM extraction fails or is misconfigured."""


class StartupValidationError(Exception):
    """Raised when extracted startup data fails deterministic validation."""
