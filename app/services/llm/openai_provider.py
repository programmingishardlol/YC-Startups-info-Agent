import json

from openai import AsyncOpenAI, OpenAIError

from app.core.config import Settings
from app.models.startup import StartupExtractionResult, StartupProfileRaw
from app.services.llm.errors import StartupExtractionError
from app.services.memory import MemoryContext


class OpenAIStartupLLMProvider:
    def __init__(self, settings: Settings) -> None:
        if not settings.openai_api_key:
            raise StartupExtractionError("OPENAI_API_KEY is not set.")

        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def extract_profile(
        self,
        raw_profile: StartupProfileRaw,
        memory_context: MemoryContext,
        market_guide: str,
    ) -> StartupExtractionResult:
        instructions = self._build_instructions(memory_context, market_guide)
        raw_profile_json = json.dumps(raw_profile.model_dump(mode="json"), ensure_ascii=False, indent=2)

        try:
            response = await self.client.responses.parse(
                model=self.settings.llm_model,
                instructions=instructions,
                input=f"Extract structured fields from this raw startup profile JSON:\n{raw_profile_json}",
                text_format=StartupExtractionResult,
                max_output_tokens=self.settings.llm_max_output_tokens,
                temperature=0,
            )
        except OpenAIError as exc:
            raise StartupExtractionError(f"OpenAI extraction request failed: {exc}") from exc

        parsed = response.output_parsed
        if parsed is None:
            raise StartupExtractionError("OpenAI extraction returned no parsed JSON output.")

        return parsed

    def _build_instructions(self, memory_context: MemoryContext, market_guide: str) -> str:
        prompt_sections = [
            "You extract structured startup fields from deterministic YC raw profile data.",
            "Use only the provided input JSON. Do not use outside knowledge.",
            "If a field is unknown, unsupported, or ambiguous from the provided input, return null.",
            "Return strict JSON that matches the schema exactly.",
            "Write for a non-technical reader using plain, everyday language and short sentences.",
            "Avoid jargon when possible. If you must use a technical term, explain it in simple words.",
            "Keep each field concise so it fits cleanly in the response schema without long run-on text.",
            "For founders, preserve the same founder names and order as the input founders list.",
            "Founder background summaries must be short and grounded only in the founder title and bio.",
            "description_plain must be a simple one-sentence explanation of what the startup does.",
            "When launch_post is present, use its title, tagline, and body as grounded context for problem and solution.",
            "Problem and solution must be concise, factual, easy for a non-technical reader to understand, and grounded only in the provided description, launch_post fields, and founder bios.",
            "Market category must be a short market label such as 'Insurance Operations Software' or null if unclear.",
            "market_hints contains deterministic hints extracted from source text before the LLM step.",
            "Use market_hints.target_customer_hints, market_hints.customer_count_hints, and market_hints.pricing_hints to improve the market estimate when helpful.",
            "Treat these as hints, not confirmed facts, unless the source text says them directly.",
            "market_benchmarks contains deterministic public benchmark entries selected before the LLM step.",
            "Use market_benchmarks.industry_customer_counts before inventing customer-count assumptions.",
            "Use market_benchmarks.competitor_pricing before inventing pricing assumptions.",
            "If a relevant benchmark exists, anchor your assumptions to it and mention the benchmark in market_size_reasoning in simple words.",
            "For market sizing, follow a bottom-up first approach. State assumptions clearly and prefer ranges over false precision.",
            "market_size_estimate must clearly say it is an estimate and should stay to one short sentence.",
            "market_size_reasoning must explain the market definition, target customer, bottom-up logic, assumptions, and a short top-down sanity check.",
            "If there is not enough grounded information to estimate the market responsibly, return null for all market sizing fields.",
        ]

        if memory_context.past_mistakes:
            prompt_sections.append("Past mistakes from memory.md to avoid repeating:")
            prompt_sections.extend(f"- {mistake}" for mistake in memory_context.past_mistakes)

        if memory_context.prevention_rules:
            prompt_sections.append("Project prevention rules from memory.md:")
            prompt_sections.extend(f"- {rule}" for rule in memory_context.prevention_rules)

        if market_guide:
            prompt_sections.append("Market sizing guide from MARKET.md:")
            prompt_sections.append(market_guide)

        return "\n".join(prompt_sections)
