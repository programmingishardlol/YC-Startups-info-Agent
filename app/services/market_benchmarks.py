from dataclasses import dataclass

from app.models.startup import MarketBenchmarkRaw, MarketBenchmarksRaw, StartupProfileRaw


@dataclass(frozen=True)
class _BenchmarkCatalogEntry:
    benchmark: MarketBenchmarkRaw
    any_keywords: tuple[str, ...]


PRICING_BENCHMARKS: tuple[_BenchmarkCatalogEntry, ...] = (
    _BenchmarkCatalogEntry(
        benchmark=MarketBenchmarkRaw(
            name="Salesforce Starter Suite",
            benchmark_type="competitor_pricing",
            value_hint="As of March 27, 2026, Salesforce listed Starter Suite at $25 per user per month.",
            source_label="Salesforce Starter Suite pricing",
            source_url="https://www.salesforce.com/small-business/pro-suite/",
            note="Useful as a baseline for small-team CRM pricing.",
        ),
        any_keywords=("crm", "sales", "pipeline", "deal"),
    ),
    _BenchmarkCatalogEntry(
        benchmark=MarketBenchmarkRaw(
            name="HubSpot Sales Hub Starter",
            benchmark_type="competitor_pricing",
            value_hint="As of January 26, 2026, HubSpot listed Sales Hub Starter at $9 per seat per month billed annually or $15 monthly.",
            source_label="HubSpot Sales Hub pricing",
            source_url="https://blog.hubspot.com/sales/hubspot-sales-hub-pricing",
            note="Useful as a baseline for startup-focused CRM and sales tooling.",
        ),
        any_keywords=("crm", "sales", "pipeline", "marketing"),
    ),
)


CUSTOMER_COUNT_BENCHMARKS: tuple[_BenchmarkCatalogEntry, ...] = (
    _BenchmarkCatalogEntry(
        benchmark=MarketBenchmarkRaw(
            name="U.S. Small Businesses",
            benchmark_type="industry_customer_count",
            value_hint="The SBA said on August 14, 2024 that the United States has more than 34 million small businesses.",
            source_label="U.S. Small Business Administration",
            source_url="https://www.sba.gov/article/2024/08/14/small-dollar-lending-lending-underserved-entrepreneurs-continues-rise-record-19-million-new-business",
            note="Useful as an upper-bound customer pool for startup and SMB-focused products.",
        ),
        any_keywords=("startup", "startups", "small business", "small businesses", "smb", "smbs", "founder", "founders", "cfo", "cfos"),
    ),
    _BenchmarkCatalogEntry(
        benchmark=MarketBenchmarkRaw(
            name="U.S. Hospitals",
            benchmark_type="industry_customer_count",
            value_hint="AHA Fast Facts 2026 lists 6,100 total U.S. hospitals and 5,121 community hospitals.",
            source_label="American Hospital Association Fast Facts 2026",
            source_url="https://www.aha.org/statistics/fast-facts-us-hospitals",
            note="Useful for healthcare operations and hospital workflow software.",
        ),
        any_keywords=("hospital", "hospitals", "clinic", "clinics", "health system", "health systems"),
    ),
    _BenchmarkCatalogEntry(
        benchmark=MarketBenchmarkRaw(
            name="U.S. Insurers",
            benchmark_type="industry_customer_count",
            value_hint="The NAIC says its 2025 listing includes more than 5,000 insurers in the United States.",
            source_label="National Association of Insurance Commissioners",
            source_url="https://content.naic.org/publications",
            note="Useful for insurance workflow, claims, and carrier software markets.",
        ),
        any_keywords=("insurance", "insurer", "insurers", "public adjuster", "public adjusters", "restoration"),
    ),
    _BenchmarkCatalogEntry(
        benchmark=MarketBenchmarkRaw(
            name="U.S. Manufacturing Establishments",
            benchmark_type="industry_customer_count",
            value_hint="The U.S. Census Bureau reported that manufacturing establishments declined from 291,586 in 2017 to 286,626 in 2022.",
            source_label="U.S. Census Bureau manufacturing snapshot",
            source_url="https://www.census.gov/library/stories/2026/03/chemical-manufacturing.html",
            note="Useful as a rough upper-bound benchmark for hardware and product companies.",
        ),
        any_keywords=("hardware", "manufacturing", "compliance", "testing lab", "testing labs"),
    ),
)


def build_market_benchmarks(profile: StartupProfileRaw) -> MarketBenchmarksRaw:
    searchable_text = _build_searchable_text(profile)

    return MarketBenchmarksRaw(
        competitor_pricing=_match_benchmarks(searchable_text, PRICING_BENCHMARKS, limit=4),
        industry_customer_counts=_match_benchmarks(searchable_text, CUSTOMER_COUNT_BENCHMARKS, limit=4),
    )


def _build_searchable_text(profile: StartupProfileRaw) -> str:
    parts: list[str] = [
        profile.company_name,
        profile.description or "",
        profile.launch_post.title if profile.launch_post else "",
        profile.launch_post.tagline if profile.launch_post else "",
        profile.launch_post.body if profile.launch_post else "",
        *profile.market_hints.target_customer_hints,
    ]
    return " ".join(part.lower() for part in parts if part)


def _match_benchmarks(
    searchable_text: str,
    entries: tuple[_BenchmarkCatalogEntry, ...],
    *,
    limit: int,
) -> list[MarketBenchmarkRaw]:
    matches: list[MarketBenchmarkRaw] = []

    for entry in entries:
        if any(keyword in searchable_text for keyword in entry.any_keywords):
            if not any(existing.source_url == entry.benchmark.source_url for existing in matches):
                matches.append(entry.benchmark)

        if len(matches) >= limit:
            return matches

    return matches
