"""Loads the reusable prompt templates in content_qa/prompts/ and fills them in.

Kept as plain .txt files (rather than inline strings) so they're easy to
read, copy into another project, or hand-edit without touching any code.
"""

from __future__ import annotations

from pathlib import Path

from .criteria import QualityCriteria

_PROMPTS_DIR = Path(__file__).parent / "prompts"

REVISE_SYSTEM_PROMPT = (_PROMPTS_DIR / "revise_system.txt").read_text(encoding="utf-8").strip()
_REVISE_USER_TEMPLATE = (_PROMPTS_DIR / "revise_user.txt").read_text(encoding="utf-8")


def build_revise_prompt(text: str, criteria: QualityCriteria) -> str:
    return _REVISE_USER_TEMPLATE.format(
        text=text,
        min_words=criteria.min_words,
        max_words=criteria.max_words,
        required_keywords=", ".join(criteria.required_keywords) or "(none)",
        required_cta_phrases=", ".join(criteria.required_cta_phrases) or "(none)",
        forbidden_terms=", ".join(criteria.forbidden_terms) or "(none)",
    )
