import re

from app.models.startup import MarketHintsRaw, StartupProfileRaw

TARGET_CUSTOMER_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bstartups?\b",
        r"\bsmall businesses\b",
        r"\bSMBs?\b",
        r"\bhospitals?\b",
        r"\bdepartments?\b",
        r"\bclinics?\b",
        r"\binsurance companies?\b",
        r"\bpublic adjusters?\b",
        r"\brestoration contents?\b",
        r"\bhardware companies?\b",
        r"\bhardware teams?\b",
        r"\bfounders?\b",
        r"\bproviders?\b",
        r"\bhealth systems?\b",
        r"\bacademic health systems?\b",
        r"\bCFOs?\b",
        r"\btreasury teams?\b",
        r"\btesting labs?\b",
    ]
]

CUSTOMER_COUNT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\b\d[\d,]*(?:\+)?\s+(?:departments?|hospitals?|companies?|businesses?|customers?|clients?|teams?|clinics?|labs?|systems?|firms?)\b",
        r"\b(?:dozens|hundreds|thousands|millions)\s+of\s+(?:departments?|hospitals?|companies?|businesses?|customers?|clients?|teams?|clinics?|labs?|systems?|firms?)\b",
        r"\bFortune 500 companies\b",
    ]
]

PRICING_HINT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\$\s?\d[\d,]*(?:\.\d+)?\s*(?:[KMB]|million|billion)?",
        r"\b\d+(?:\.\d+)?%\b",
        r"\bmanagement fee\b",
        r"\bfees?\b",
        r"\bprice\b",
        r"\bpricing\b",
        r"\bcosts?\b",
        r"\bcharge\b",
        r"\bcharged\b",
        r"\byield\b",
        r"\breturns?\b",
        r"\bannual\b",
        r"\bper year\b",
        r"\bper month\b",
        r"\bper seat\b",
        r"\bper user\b",
        r"\bsubscription\b",
    ]
]

SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+|\n+")


def build_market_hints(profile: StartupProfileRaw) -> MarketHintsRaw:
    text_blocks = [
        profile.description or "",
        profile.launch_post.title if profile.launch_post else "",
        profile.launch_post.tagline if profile.launch_post else "",
        profile.launch_post.body if profile.launch_post else "",
    ]
    full_text = "\n".join(block for block in text_blocks if block)
    sentences = [sentence.strip() for sentence in SENTENCE_SPLIT_PATTERN.split(full_text) if sentence.strip()]

    return MarketHintsRaw(
        target_customer_hints=_collect_pattern_matches(full_text, TARGET_CUSTOMER_PATTERNS, limit=8),
        customer_count_hints=_collect_matching_sentences(sentences, CUSTOMER_COUNT_PATTERNS, limit=6),
        pricing_hints=_collect_matching_sentences(sentences, PRICING_HINT_PATTERNS, limit=6),
    )


def _collect_pattern_matches(text: str, patterns: list[re.Pattern[str]], limit: int) -> list[str]:
    matches: list[str] = []

    for pattern in patterns:
        for match in pattern.finditer(text):
            snippet = " ".join(match.group(0).split())
            if snippet and snippet not in matches:
                matches.append(snippet)
            if len(matches) >= limit:
                return matches

    return matches


def _collect_matching_sentences(
    sentences: list[str],
    patterns: list[re.Pattern[str]],
    limit: int,
) -> list[str]:
    matches: list[str] = []

    for sentence in sentences:
        normalized = " ".join(sentence.split())
        if not normalized:
            continue

        if any(pattern.search(normalized) for pattern in patterns) and normalized not in matches:
            matches.append(normalized)

        if len(matches) >= limit:
            return matches

    return matches
