from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

MISTAKE_PREFIX = "- Mistake:"
PREVENTION_RULE_PREFIX = "- Prevention rule:"


@dataclass(frozen=True)
class MemoryContext:
    past_mistakes: list[str] = field(default_factory=list)
    prevention_rules: list[str] = field(default_factory=list)


def load_memory_context(memory_file_path: str) -> MemoryContext:
    memory_path = Path(memory_file_path)
    if not memory_path.exists():
        return MemoryContext()

    mistakes: list[str] = []
    rules: list[str] = []

    for line in memory_path.read_text(encoding="utf-8").splitlines():
        if line.startswith(MISTAKE_PREFIX):
            mistakes.append(line.split(MISTAKE_PREFIX, maxsplit=1)[1].strip())
        if line.startswith(PREVENTION_RULE_PREFIX):
            rules.append(line.split(PREVENTION_RULE_PREFIX, maxsplit=1)[1].strip())

    return MemoryContext(
        past_mistakes=mistakes,
        prevention_rules=rules,
    )


def load_prevention_rules(memory_file_path: str) -> list[str]:
    return load_memory_context(memory_file_path).prevention_rules


def append_memory_entry(
    memory_file_path: str,
    mistake: str,
    prevention_rule: str,
    applies_to: list[str],
) -> None:
    memory_path = Path(memory_file_path)
    current_text = memory_path.read_text(encoding="utf-8") if memory_path.exists() else "# Memory\n"

    if prevention_rule in current_text:
        return

    section_header = f"## {date.today().isoformat()}"
    lines = current_text.rstrip().splitlines()

    if section_header not in current_text:
        if lines and lines[-1] != "":
            lines.append("")
        lines.extend([section_header, ""])
    elif lines and lines[-1] != "":
        lines.append("")

    lines.append(f"- Mistake: {mistake}")
    lines.append(f"- Prevention rule: {prevention_rule}")
    lines.append(f"- Applies to: {', '.join(applies_to)}.")
    lines.append("")

    memory_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
