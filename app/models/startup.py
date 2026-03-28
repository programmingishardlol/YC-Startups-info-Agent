from pydantic import BaseModel, Field, HttpUrl


class FounderProfileRaw(BaseModel):
    name: str
    title: str | None = None
    bio: str | None = None


class FounderBackgroundSummary(BaseModel):
    name: str
    background_summary: str | None = None


class LaunchPostRaw(BaseModel):
    title: str
    tagline: str | None = None
    body: str | None = None
    url: HttpUrl
    created_at: str | None = None


class MarketHintsRaw(BaseModel):
    target_customer_hints: list[str] = Field(default_factory=list)
    customer_count_hints: list[str] = Field(default_factory=list)
    pricing_hints: list[str] = Field(default_factory=list)


class MarketBenchmarkRaw(BaseModel):
    name: str
    benchmark_type: str
    value_hint: str
    source_label: str
    source_url: HttpUrl
    note: str | None = None


class MarketBenchmarksRaw(BaseModel):
    competitor_pricing: list[MarketBenchmarkRaw] = Field(default_factory=list)
    industry_customer_counts: list[MarketBenchmarkRaw] = Field(default_factory=list)


class StartupLink(BaseModel):
    company_name: str
    yc_batch: str
    company_url: HttpUrl
    launched_at: int | None = None


class LatestStartupLinksResponse(BaseModel):
    yc_batch: str
    count: int = Field(..., ge=0)
    companies: list[StartupLink]
    sources: list[HttpUrl]


class StartupProfileRaw(BaseModel):
    company_name: str
    yc_batch: str
    launched_at: int | None = None
    description: str | None = None
    founders: list[FounderProfileRaw]
    website: HttpUrl | None = None
    location: str | None = None
    company_url: HttpUrl
    launch_post: LaunchPostRaw | None = None
    market_hints: MarketHintsRaw = Field(default_factory=MarketHintsRaw)
    market_benchmarks: MarketBenchmarksRaw = Field(default_factory=MarketBenchmarksRaw)


class LatestStartupProfilesResponse(BaseModel):
    yc_batch: str
    count: int = Field(..., ge=0)
    companies: list[StartupProfileRaw]
    sources: list[HttpUrl]


class StartupExtractionResult(BaseModel):
    description_plain: str | None = None
    problem: str | None = None
    solution: str | None = None
    market_category: str | None = None
    market_definition: str | None = None
    target_customer: str | None = None
    market_size_estimate: str | None = None
    market_size_reasoning: str | None = None
    tam_estimate_usd: float | None = None
    sam_estimate_usd: float | None = None
    som_estimate_usd: float | None = None
    founders: list[FounderBackgroundSummary]


class FounderProfileEnriched(BaseModel):
    name: str
    title: str | None = None
    bio: str | None = None
    background_summary: str | None = None


class StartupProfileEnriched(BaseModel):
    company_name: str
    yc_batch: str
    launched_at: int | None = None
    description: str | None = None
    description_plain: str | None = None
    problem: str | None = None
    solution: str | None = None
    market_category: str | None = None
    market_definition: str | None = None
    target_customer: str | None = None
    market_size_estimate: str | None = None
    market_size_reasoning: str | None = None
    tam_estimate_usd: float | None = None
    sam_estimate_usd: float | None = None
    som_estimate_usd: float | None = None
    founders: list[FounderProfileEnriched]
    website: HttpUrl | None = None
    location: str | None = None
    company_url: HttpUrl
    launch_post: LaunchPostRaw | None = None


class LatestStartupEnrichedResponse(BaseModel):
    yc_batch: str
    count: int = Field(..., ge=0)
    companies: list[StartupProfileEnriched]
    sources: list[HttpUrl]


class LaunchPostPreview(BaseModel):
    title: str
    tagline: str | None = None
    url: HttpUrl
    created_at: str | None = None


class StartupOverviewResponse(BaseModel):
    company_name: str
    yc_batch: str
    launched_at: int | None = None
    description: str | None = None
    website: HttpUrl | None = None
    location: str | None = None
    company_url: HttpUrl


class StartupResearchResponse(BaseModel):
    problem: str | None = None
    solution: str | None = None
    market_category: str | None = None
    market_definition: str | None = None
    target_customer: str | None = None
    market_size_estimate: str | None = None
    market_size_reasoning: str | None = None
    tam_estimate_usd: float | None = None
    sam_estimate_usd: float | None = None
    som_estimate_usd: float | None = None


class FounderReadableResponse(BaseModel):
    name: str
    title: str | None = None
    background_summary: str | None = None


class StartupReadableResponse(BaseModel):
    overview: StartupOverviewResponse
    research: StartupResearchResponse
    founders: list[FounderReadableResponse]
    launch_post: LaunchPostPreview | None = None


class LatestStartupsReadableResponse(BaseModel):
    yc_batch: str
    count: int = Field(..., ge=0)
    companies: list[StartupReadableResponse]
    sources: list[HttpUrl]
