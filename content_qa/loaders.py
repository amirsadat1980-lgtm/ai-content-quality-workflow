"""Load example content pieces and their quality criteria from examples/."""

from __future__ import annotations

import json
from pathlib import Path

from .criteria import QualityCriteria


def load_pieces(manifest_path: Path) -> list[tuple[str, QualityCriteria]]:
    """Return a list of (content_text, criteria) pairs described by the manifest."""
    manifest_path = Path(manifest_path)
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))

    pieces = []
    for entry in entries:
        text_path = manifest_path.parent / entry["input_file"]
        text = text_path.read_text(encoding="utf-8").strip()
        criteria = QualityCriteria(
            name=entry["id"],
            min_words=entry["criteria"].get("min_words", 40),
            max_words=entry["criteria"].get("max_words", 200),
            required_keywords=entry["criteria"].get("required_keywords", []),
            required_cta_phrases=entry["criteria"].get("required_cta_phrases", []),
            forbidden_terms=entry["criteria"].get("forbidden_terms", []),
        )
        pieces.append((text, criteria))
    return pieces
