import html
import json
import re

from app.models.startup import FounderProfileRaw, LaunchPostRaw, StartupProfileRaw

DATA_PAGE_PATTERN = re.compile(r'data-page="([^"]+)"', re.DOTALL)


class YCCompanyPageParseError(Exception):
    """Raised when a YC company page payload cannot be parsed."""


def parse_startup_profile_from_company_page(
    page_html: str,
    company_url: str,
    launched_at: int | None = None,
) -> StartupProfileRaw:
    page_payload = _parse_page_payload(page_html)

    try:
        props = page_payload["props"]
        company = props["company"]
    except KeyError as exc:
        raise YCCompanyPageParseError("YC company page payload is missing company data.") from exc

    return StartupProfileRaw(
        company_name=company["name"],
        yc_batch=_normalize_optional_text(company.get("batch_name")) or _normalize_optional_text(company.get("batch")),
        launched_at=launched_at,
        description=_normalize_optional_text(company.get("long_description"))
        or _normalize_optional_text(company.get("one_liner")),
        founders=_parse_founders(company.get("founders", [])),
        website=_normalize_optional_text(company.get("website")),
        location=_normalize_optional_text(company.get("location")),
        company_url=company_url,
        launch_post=_parse_launch_post(props.get("launches", [])),
    )


def _parse_page_payload(page_html: str) -> dict:
    match = DATA_PAGE_PATTERN.search(page_html)
    if not match:
        raise YCCompanyPageParseError("Could not find the server-rendered data payload on the YC company page.")

    try:
        return json.loads(html.unescape(match.group(1)))
    except json.JSONDecodeError as exc:
        raise YCCompanyPageParseError("YC company page payload was not valid JSON.") from exc


def _parse_founders(founders: list[dict]) -> list[FounderProfileRaw]:
    parsed_founders: list[FounderProfileRaw] = []

    for founder in founders:
        name = _normalize_optional_text(founder.get("full_name"))
        if not name:
            continue

        parsed_founders.append(
            FounderProfileRaw(
                name=name,
                title=_normalize_optional_text(founder.get("title")),
                bio=_normalize_optional_text(founder.get("founder_bio")),
            )
        )

    return parsed_founders


def _parse_launch_post(launches: list[dict]) -> LaunchPostRaw | None:
    public_launches = [
        launch
        for launch in launches
        if _normalize_optional_text(launch.get("state")) == "public" and _normalize_optional_text(launch.get("url"))
    ]
    if not public_launches:
        return None

    latest_launch = max(
        public_launches,
        key=lambda launch: _normalize_optional_text(launch.get("created_at")) or "",
    )
    title = _normalize_optional_text(latest_launch.get("title"))
    url = _normalize_optional_text(latest_launch.get("url"))

    if not title or not url:
        return None

    return LaunchPostRaw(
        title=title,
        tagline=_normalize_optional_text(latest_launch.get("tagline")),
        body=_normalize_optional_text(latest_launch.get("body")),
        url=url,
        created_at=_normalize_optional_text(latest_launch.get("created_at")),
    )


def _normalize_optional_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None

    normalized = html.unescape(value)
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ").strip()
    return normalized or None
