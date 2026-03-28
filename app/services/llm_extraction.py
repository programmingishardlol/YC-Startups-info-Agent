from app.core.config import Settings
from app.models.startup import (
    FounderProfileEnriched,
    LatestStartupEnrichedResponse,
    LatestStartupProfilesResponse,
    StartupExtractionResult,
    StartupProfileEnriched,
    StartupProfileRaw,
)
from app.services.llm.errors import StartupExtractionError, StartupValidationError
from app.services.llm.factory import build_startup_llm_provider
from app.services.market_guide import load_market_guide
from app.services.llm_validation import StartupExtractionValidator
from app.services.memory import append_memory_entry, load_memory_context


class StartupLLMService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.validator = StartupExtractionValidator()

    async def enrich_profiles(
        self,
        raw_response: LatestStartupProfilesResponse,
    ) -> LatestStartupEnrichedResponse:
        memory_context = load_memory_context(self.settings.memory_file_path)
        market_guide = load_market_guide(self.settings.market_guide_file_path)
        provider = build_startup_llm_provider(self.settings)

        extraction_results: list[StartupExtractionResult] = []
        for raw_profile in raw_response.companies:
            extraction_result = await provider.extract_profile(raw_profile, memory_context, market_guide)

            try:
                validated_result = self.validator.validate(raw_profile, extraction_result)
            except StartupValidationError as exc:
                self._record_validation_failure(raw_profile, exc)
                raise

            extraction_results.append(validated_result)

        enriched_companies = [
            self._merge_profile(raw_profile, extraction_result)
            for raw_profile, extraction_result in zip(raw_response.companies, extraction_results, strict=True)
        ]

        return LatestStartupEnrichedResponse(
            yc_batch=raw_response.yc_batch,
            count=len(enriched_companies),
            companies=enriched_companies,
            sources=raw_response.sources,
        )

    def _merge_profile(
        self,
        raw_profile: StartupProfileRaw,
        extraction_result: StartupExtractionResult,
    ) -> StartupProfileEnriched:
        background_by_name = {
            founder.name: founder.background_summary for founder in extraction_result.founders
        }
        enriched_founders = [
            FounderProfileEnriched(
                name=founder.name,
                title=founder.title,
                bio=founder.bio,
                background_summary=background_by_name.get(founder.name),
            )
            for founder in raw_profile.founders
        ]

        return StartupProfileEnriched(
            company_name=raw_profile.company_name,
            yc_batch=raw_profile.yc_batch,
            launched_at=raw_profile.launched_at,
            description=raw_profile.description,
            description_plain=extraction_result.description_plain,
            problem=extraction_result.problem,
            solution=extraction_result.solution,
            market_category=extraction_result.market_category,
            market_definition=extraction_result.market_definition,
            target_customer=extraction_result.target_customer,
            market_size_estimate=extraction_result.market_size_estimate,
            market_size_reasoning=extraction_result.market_size_reasoning,
            tam_estimate_usd=extraction_result.tam_estimate_usd,
            sam_estimate_usd=extraction_result.sam_estimate_usd,
            som_estimate_usd=extraction_result.som_estimate_usd,
            founders=enriched_founders,
            website=raw_profile.website,
            location=raw_profile.location,
            company_url=raw_profile.company_url,
            launch_post=raw_profile.launch_post,
        )

    def _record_validation_failure(
        self,
        raw_profile: StartupProfileRaw,
        exc: StartupValidationError,
    ) -> None:
        append_memory_entry(
            memory_file_path=self.settings.memory_file_path,
            mistake=(
                f"LLM extraction for {raw_profile.company_name} failed deterministic validation: {exc}"
            ),
            prevention_rule=(
                "After LLM extraction, validate founder names and output field lengths against the "
                "deterministic input before returning enriched results."
            ),
            applies_to=["LLM prompts", "final output validation"],
        )


__all__ = ["StartupExtractionError", "StartupLLMService", "StartupValidationError"]
