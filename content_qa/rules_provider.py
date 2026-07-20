"""The default, deterministic content provider.

No API key, no network access, no randomness — the same input always
produces the same output. `revise()` applies a small set of explicit,
inspectable fixes for the most common failures against a QualityCriteria:
too long, missing a call-to-action, or containing a forbidden term. It does
not attempt to invent missing content (e.g. a too-short draft) — that's a
real limitation of a rules-only approach, documented in the README rather
than papered over with an actual LLM call.
"""

from __future__ import annotations

from .criteria import QualityCriteria
from .text_utils import truncate_to_words


class RulesProvider:
    """Deterministic revise-only provider. Safe to run with zero setup."""

    name = "rules"

    def revise(self, text: str, criteria: QualityCriteria) -> tuple[str, list[str]]:
        """Return (revised_text, list_of_fixes_applied)."""
        fixes: list[str] = []
        result = text

        for term in criteria.forbidden_terms:
            if term.lower() in result.lower():
                result = _replace_case_insensitive(result, term, "[removed]")
                fixes.append(f"removed forbidden term '{term}'")

        needs_cta = criteria.required_cta_phrases and not any(
            p.lower() in result.lower() for p in criteria.required_cta_phrases
        )
        cta = criteria.required_cta_phrases[0] if needs_cta else ""

        # Truncate first, reserving room for the CTA we're about to add, so
        # trimming to the word budget can never cut the CTA back off again.
        budget = criteria.max_words - len(cta.split())
        word_count = len(result.split())
        if word_count > budget:
            result = truncate_to_words(result, max(budget, 1))
            fixes.append(f"trimmed to fit the {criteria.max_words}-word budget (was {word_count} words)")

        if needs_cta:
            result = result.rstrip()
            if not result.endswith((".", "!", "?")):
                result += "."
            result = f"{result} {cta}"
            fixes.append(f"appended missing call-to-action: '{cta}'")

        return result, fixes


def _replace_case_insensitive(text: str, term: str, replacement: str) -> str:
    lowered = text.lower()
    term_lower = term.lower()
    out = []
    idx = 0
    while True:
        pos = lowered.find(term_lower, idx)
        if pos == -1:
            out.append(text[idx:])
            break
        out.append(text[idx:pos])
        out.append(replacement)
        idx = pos + len(term)
    return "".join(out)
