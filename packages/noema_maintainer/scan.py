from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

OBJECT_CLASSES = ("raw", "structured", "proposals", "logs")


@dataclass(frozen=True)
class ObjectRecord:
    path: Path
    object_class: str
    metadata: dict[str, Any]


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"').strip("'") for item in inner.split(",")]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value.strip('"').strip("'")


def parse_frontmatter(text: str) -> dict[str, Any] | None:
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return None

    metadata: dict[str, Any] = {}
    current_key: str | None = None
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            return metadata

        if line.startswith("  - ") or line.startswith("- "):
            if current_key is None:
                continue
            value = line.split("-", 1)[1].strip()
            existing = metadata.get(current_key)
            if not isinstance(existing, list):
                existing = []
            existing.append(_parse_scalar(value))
            metadata[current_key] = existing
            continue

        if ":" not in line:
            continue

        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        current_key = key

        if raw_value == "":
            metadata[key] = []
        else:
            metadata[key] = _parse_scalar(raw_value)

    return None


def scan_repository(repo_root: Path) -> list[ObjectRecord]:
    records: list[ObjectRecord] = []
    for object_class in OBJECT_CLASSES:
        class_dir = repo_root / object_class
        if not class_dir.exists():
            continue
        for md_file in sorted(class_dir.rglob("*.md")):
            frontmatter = parse_frontmatter(md_file.read_text(encoding="utf-8"))
            if frontmatter is None:
                continue
            records.append(ObjectRecord(path=md_file, object_class=object_class, metadata=frontmatter))
    records.sort(key=lambda r: (r.metadata.get("workspace", ""), r.object_class, str(r.path), r.metadata.get("id", "")))
    return records
