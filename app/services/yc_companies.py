import html
import json
import re
from asyncio import gather
from dataclasses import dataclass
from urllib.parse import urlencode

import httpx

from app.core.config import Settings
from app.models.startup import (
    FounderReadableResponse,
    LatestStartupEnrichedResponse,
    LatestStartupLinksResponse,
    LatestStartupProfilesResponse,
    LatestStartupsReadableResponse,
    LaunchPostPreview,
    StartupOverviewResponse,
    StartupProfileRaw,
    StartupReadableResponse,
    StartupResearchResponse,
    StartupLink,
)
from app.services.llm_extraction import StartupLLMService
from app.services.market_benchmarks import build_market_benchmarks
from app.services.market_hints import build_market_hints
from app.services.yc_company_parser import (
    YCCompanyPageParseError,
    parse_startup_profile_from_company_page,
)

CURRENT_BATCH_PATTERN = re.compile(r'"currentBatch":"([^"]+)"')
ALGOLIA_OPTS_PATTERN = re.compile(r"window\.AlgoliaOpts\s*=\s*(\{.*?\});", re.DOTALL)
LAUNCH_DATE_INDEX = "YCCompany_By_Launch_Date_production"


class YCScraperError(Exception):
    """Raised when public YC data cannot be parsed safely."""


@dataclass(frozen=True)
class AlgoliaPublicConfig:
    app_id: str
    api_key: str


class YCCompanyService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def fetch_latest_startup_links(self, limit: int | None = None) -> LatestStartupLinksResponse:
        current_batch, companies = await self._fetch_latest_startup_links_data(limit=limit)

        return LatestStartupLinksResponse(
            yc_batch=current_batch,
            count=len(companies),
            companies=companies,
            sources=[self.settings.yc_companies_url, *[str(company.company_url) for company in companies]],
        )

    async def fetch_latest_startup_profiles(self, limit: int | None = None) -> LatestStartupProfilesResponse:
        timeout = self.settings.request_timeout_seconds
        headers = {"User-Agent": f"{self.settings.app_name}/0.1"}

        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            current_batch, companies = await self._fetch_latest_startup_links_data(client=client, limit=limit)
            company_pages = await gather(
                *[self._fetch_company_page(client, str(company.company_url)) for company in companies]
            )

        try:
            profiles = [
                self._attach_market_context(
                    parse_startup_profile_from_company_page(
                        page_html=page_html,
                        company_url=str(company.company_url),
                        launched_at=company.launched_at,
                    )
                )
                for company, page_html in zip(companies, company_pages, strict=True)
            ]
        except YCCompanyPageParseError as exc:
            raise YCScraperError(str(exc)) from exc

        return LatestStartupProfilesResponse(
            yc_batch=current_batch,
            count=len(profiles),
            companies=profiles,
            sources=self._build_profile_sources(profiles),
        )

    async def fetch_latest_startup_profiles_readable(
        self,
        limit: int | None = None,
    ) -> LatestStartupsReadableResponse:
        raw_profiles = await self.fetch_latest_startup_profiles(limit=limit)
        return self._format_profiles_for_api(
            yc_batch=raw_profiles.yc_batch,
            profiles=raw_profiles.companies,
            sources=raw_profiles.sources,
        )

    async def fetch_latest_startup_profiles_enriched(
        self,
        limit: int | None = None,
    ) -> LatestStartupEnrichedResponse:
        raw_profiles = await self.fetch_latest_startup_profiles(limit=limit)
        extractor = StartupLLMService(self.settings)
        enriched_response = await extractor.enrich_profiles(raw_profiles)
        return LatestStartupEnrichedResponse(
            yc_batch=enriched_response.yc_batch,
            count=enriched_response.count,
            companies=enriched_response.companies,
            sources=self._build_profile_sources(raw_profiles.companies),
        )

    async def fetch_latest_startup_profiles_enriched_readable(
        self,
        limit: int | None = None,
    ) -> LatestStartupsReadableResponse:
        enriched_profiles = await self.fetch_latest_startup_profiles_enriched(limit=limit)
        return self._format_profiles_for_api(
            yc_batch=enriched_profiles.yc_batch,
            profiles=enriched_profiles.companies,
            sources=enriched_profiles.sources,
        )

    async def _fetch_latest_startup_links_data(
        self,
        client: httpx.AsyncClient | None = None,
        limit: int | None = None,
    ) -> tuple[str, list[StartupLink]]:
        timeout = self.settings.request_timeout_seconds
        headers = {"User-Agent": f"{self.settings.app_name}/0.1"}
        resolved_limit = limit or self.settings.startup_limit

        if client is not None:
            return await self._fetch_latest_startup_links_with_client(client, limit=resolved_limit)

        async with httpx.AsyncClient(timeout=timeout, headers=headers) as owned_client:
            return await self._fetch_latest_startup_links_with_client(owned_client, limit=resolved_limit)

    async def _fetch_latest_startup_links_with_client(
        self,
        client: httpx.AsyncClient,
        limit: int,
    ) -> tuple[str, list[StartupLink]]:
        directory_html = await self._fetch_directory_html(client)
        current_batch = self._parse_current_batch(directory_html)
        algolia_config = self._parse_algolia_config(directory_html)
        hits = await self._fetch_latest_batch_hits(client, current_batch, algolia_config, limit=limit)
        companies = [self._build_startup_link(hit, current_batch) for hit in hits]
        return current_batch, companies

    async def _fetch_directory_html(self, client: httpx.AsyncClient) -> str:
        response = await client.get(self.settings.yc_companies_url)
        response.raise_for_status()
        return response.text

    async def _fetch_company_page(self, client: httpx.AsyncClient, company_url: str) -> str:
        response = await client.get(company_url)
        response.raise_for_status()
        return response.text

    def _parse_current_batch(self, page_html: str) -> str:
        match = CURRENT_BATCH_PATTERN.search(html.unescape(page_html))
        if not match:
            raise YCScraperError("Could not find the current YC batch on the companies page.")
        return match.group(1)

    def _parse_algolia_config(self, page_html: str) -> AlgoliaPublicConfig:
        match = ALGOLIA_OPTS_PATTERN.search(html.unescape(page_html))
        if not match:
            raise YCScraperError("Could not find YC's public search configuration.")

        try:
            algolia_opts = json.loads(match.group(1))
            return AlgoliaPublicConfig(
                app_id=algolia_opts["app"],
                api_key=algolia_opts["key"],
            )
        except (json.JSONDecodeError, KeyError) as exc:
            raise YCScraperError("YC's public search configuration was not in the expected format.") from exc

    async def _fetch_latest_batch_hits(
        self,
        client: httpx.AsyncClient,
        current_batch: str,
        algolia_config: AlgoliaPublicConfig,
        limit: int,
    ) -> list[dict]:
        query_url = f"https://{algolia_config.app_id}-dsn.algolia.net/1/indexes/*/queries"
        facet_filters = json.dumps([[f"batch:{current_batch}"]], separators=(",", ":"))
        params = urlencode(
            {
                "query": "",
                "hitsPerPage": limit,
                "facetFilters": facet_filters,
            }
        )
        payload = {
            "requests": [
                {
                    "indexName": LAUNCH_DATE_INDEX,
                    "params": params,
                }
            ]
        }
        headers = {
            "x-algolia-application-id": algolia_config.app_id,
            "x-algolia-api-key": algolia_config.api_key,
        }

        response = await client.post(query_url, json=payload, headers=headers)
        response.raise_for_status()

        try:
            data = response.json()
            hits = data["results"][0]["hits"]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise YCScraperError("YC's public company search response was not in the expected format.") from exc

        if not hits:
            raise YCScraperError("YC's public company search returned no startups for the current batch.")

        if limit == self.settings.startup_limit and len(hits) < limit:
            raise YCScraperError(
                f"Expected {limit} startups from the latest batch, got {len(hits)}."
            )

        return hits[:limit]

    def _build_startup_link(self, hit: dict, current_batch: str) -> StartupLink:
        company_slug = hit.get("slug") or str(hit["id"])
        company_url = f"{self.settings.yc_company_base_url}{company_slug}"

        return StartupLink(
            company_name=hit["name"],
            yc_batch=hit.get("batch", current_batch),
            company_url=company_url,
            launched_at=hit.get("launched_at"),
        )

    def _build_profile_sources(self, profiles: list[StartupProfileRaw]) -> list[str]:
        sources: list[str] = [self.settings.yc_companies_url]

        for profile in profiles:
            sources.append(str(profile.company_url))
            if profile.launch_post is not None:
                sources.append(str(profile.launch_post.url))
            for benchmark in profile.market_benchmarks.competitor_pricing:
                sources.append(str(benchmark.source_url))
            for benchmark in profile.market_benchmarks.industry_customer_counts:
                sources.append(str(benchmark.source_url))

        return list(dict.fromkeys(sources))

    def _attach_market_context(self, profile: StartupProfileRaw) -> StartupProfileRaw:
        profile_with_hints = profile.model_copy(update={"market_hints": build_market_hints(profile)})
        return profile_with_hints.model_copy(
            update={"market_benchmarks": build_market_benchmarks(profile_with_hints)}
        )

    def _format_profiles_for_api(
        self,
        *,
        yc_batch: str,
        profiles: list,
        sources: list[str],
    ) -> LatestStartupsReadableResponse:
        return LatestStartupsReadableResponse(
            yc_batch=yc_batch,
            count=len(profiles),
            companies=[self._format_single_profile(profile) for profile in profiles],
            sources=sources,
        )

    def _format_single_profile(self, profile) -> StartupReadableResponse:
        launch_post = None
        if profile.launch_post is not None:
            launch_post = LaunchPostPreview(
                title=profile.launch_post.title,
                tagline=profile.launch_post.tagline,
                url=profile.launch_post.url,
                created_at=profile.launch_post.created_at,
            )

        founders = [
            FounderReadableResponse(
                name=founder.name,
                title=founder.title,
                background_summary=getattr(founder, "background_summary", None),
            )
            for founder in profile.founders
        ]

        return StartupReadableResponse(
            overview=StartupOverviewResponse(
                company_name=profile.company_name,
                yc_batch=profile.yc_batch,
                launched_at=getattr(profile, "launched_at", None),
                description=getattr(profile, "description_plain", None) or profile.description,
                website=profile.website,
                location=profile.location,
                company_url=profile.company_url,
            ),
            research=StartupResearchResponse(
                problem=getattr(profile, "problem", None),
                solution=getattr(profile, "solution", None),
                market_category=getattr(profile, "market_category", None),
                market_definition=getattr(profile, "market_definition", None),
                target_customer=getattr(profile, "target_customer", None),
                market_size_estimate=getattr(profile, "market_size_estimate", None),
                market_size_reasoning=getattr(profile, "market_size_reasoning", None),
                tam_estimate_usd=getattr(profile, "tam_estimate_usd", None),
                sam_estimate_usd=getattr(profile, "sam_estimate_usd", None),
                som_estimate_usd=getattr(profile, "som_estimate_usd", None),
            ),
            founders=founders,
            launch_post=launch_post,
        )
