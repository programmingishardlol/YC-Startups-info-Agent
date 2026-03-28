from app.models.startup import FounderBackgroundSummary, StartupExtractionResult, StartupProfileRaw
from app.services.llm.errors import StartupValidationError


class StartupExtractionValidator:
    def validate(
        self,
        raw_profile: StartupProfileRaw,
        extraction_result: StartupExtractionResult,
    ) -> StartupExtractionResult:
        founders = self._validate_founders(raw_profile, extraction_result)

        description_available = raw_profile.description is not None
        launch_context_available = raw_profile.launch_post is not None and bool(
            raw_profile.launch_post.tagline or raw_profile.launch_post.body or raw_profile.launch_post.title
        )
        founder_context_available = any(founder.bio or founder.title for founder in raw_profile.founders)

        description_plain = self._normalize_text(extraction_result.description_plain)
        problem = self._normalize_text(extraction_result.problem)
        solution = self._normalize_text(extraction_result.solution)
        market_category = self._normalize_text(extraction_result.market_category)
        market_definition = self._normalize_text(extraction_result.market_definition)
        target_customer = self._normalize_text(extraction_result.target_customer)
        market_size_estimate = self._normalize_text(extraction_result.market_size_estimate)
        market_size_reasoning = self._normalize_text(extraction_result.market_size_reasoning)
        tam_estimate_usd = self._normalize_amount(extraction_result.tam_estimate_usd)
        sam_estimate_usd = self._normalize_amount(extraction_result.sam_estimate_usd)
        som_estimate_usd = self._normalize_amount(extraction_result.som_estimate_usd)

        if not (description_available or launch_context_available):
            description_plain = None
            problem = None
            solution = None

        if not (description_available or launch_context_available or founder_context_available):
            market_category = None
            market_definition = None
            target_customer = None
            market_size_estimate = None
            market_size_reasoning = None
            tam_estimate_usd = None
            sam_estimate_usd = None
            som_estimate_usd = None

        description_plain = self._validate_optional_text(
            description_plain,
            field_name="description_plain",
            max_length=220,
        )
        problem = self._validate_optional_text(problem, field_name="problem", max_length=280)
        solution = self._validate_optional_text(solution, field_name="solution", max_length=280)
        market_category = self._validate_optional_text(
            market_category,
            field_name="market_category",
            max_length=80,
        )
        market_definition = self._validate_optional_text(
            market_definition,
            field_name="market_definition",
            max_length=180,
        )
        target_customer = self._validate_optional_text(
            target_customer,
            field_name="target_customer",
            max_length=180,
        )
        market_size_estimate = self._validate_optional_text(
            market_size_estimate,
            field_name="market_size_estimate",
            max_length=320,
        )
        market_size_reasoning = self._validate_optional_text(
            market_size_reasoning,
            field_name="market_size_reasoning",
            max_length=1600,
        )

        if market_size_estimate is not None and "estimate" not in market_size_estimate.lower():
            market_size_estimate = None

        if market_size_estimate is not None and (
            market_size_reasoning is None or target_customer is None or tam_estimate_usd is None
        ):
            market_size_estimate = None
            market_size_reasoning = None
            tam_estimate_usd = None
            sam_estimate_usd = None
            som_estimate_usd = None

        if tam_estimate_usd is not None and sam_estimate_usd is not None and sam_estimate_usd > tam_estimate_usd:
            sam_estimate_usd = None
            som_estimate_usd = None

        if sam_estimate_usd is not None and som_estimate_usd is not None and som_estimate_usd > sam_estimate_usd:
            som_estimate_usd = None

        return StartupExtractionResult(
            description_plain=description_plain,
            problem=problem,
            solution=solution,
            market_category=market_category,
            market_definition=market_definition,
            target_customer=target_customer,
            market_size_estimate=market_size_estimate,
            market_size_reasoning=market_size_reasoning,
            tam_estimate_usd=tam_estimate_usd,
            sam_estimate_usd=sam_estimate_usd,
            som_estimate_usd=som_estimate_usd,
            founders=founders,
        )

    def _validate_founders(
        self,
        raw_profile: StartupProfileRaw,
        extraction_result: StartupExtractionResult,
    ) -> list[FounderBackgroundSummary]:
        expected_names = [founder.name for founder in raw_profile.founders]
        returned_names = [founder.name for founder in extraction_result.founders]

        if returned_names != expected_names:
            raise StartupValidationError(
                "Founder names from LLM output did not match the deterministic YC input order."
            )

        validated_founders: list[FounderBackgroundSummary] = []
        for raw_founder, extracted_founder in zip(raw_profile.founders, extraction_result.founders, strict=True):
            background_summary = self._normalize_text(extracted_founder.background_summary)

            if not (raw_founder.title or raw_founder.bio):
                background_summary = None

            background_summary = self._validate_optional_text(
                background_summary,
                field_name=f"founder background for {raw_founder.name}",
                max_length=220,
            )

            validated_founders.append(
                FounderBackgroundSummary(
                    name=raw_founder.name,
                    background_summary=background_summary,
                )
            )

        return validated_founders

    def _validate_optional_text(
        self,
        value: str | None,
        *,
        field_name: str,
        max_length: int,
    ) -> str | None:
        if value is None:
            return None

        if len(value) > max_length:
            return self._truncate_text(value, max_length=max_length)

        return value

    def _normalize_text(self, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = " ".join(value.split())
        return normalized or None

    def _normalize_amount(self, value: float | None) -> float | None:
        if value is None:
            return None

        if value < 0:
            raise StartupValidationError("Market size amounts cannot be negative.")

        return round(float(value), 2)

    def _truncate_text(self, value: str, *, max_length: int) -> str:
        truncated = value[:max_length].rstrip()
        if len(truncated) == len(value):
            return truncated

        last_space = truncated.rfind(" ")
        if last_space >= max_length // 2:
            truncated = truncated[:last_space].rstrip()

        return truncated
