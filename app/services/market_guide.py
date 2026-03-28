from pathlib import Path


def load_market_guide(market_guide_file_path: str) -> str:
    market_guide_path = Path(market_guide_file_path)
    if not market_guide_path.exists():
        return ""

    return market_guide_path.read_text(encoding="utf-8").strip()
