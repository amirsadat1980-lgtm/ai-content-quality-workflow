"""Structured content quality criteria and the scoring functions for each.

Every scorer returns a float in [0, 1] and is a plain, inspectable rule —
there is no hidden model making the call. This is the "deterministic rules"
provider referenced throughout the README: no API key or network access is
needed to score content.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .text_utils import count_syllables, split_sentences, split_words

DEFAULT_WEIGHTS: dict[str, float] = {
    "length": 1.0,
    "keywords": 1.0,
    "cta": 1.5,
    "forbidden": 1.5,
    "readability": 1.0,
}


@dataclass
class QualityCriteria:
    """The structured, per-piece quality bar content is checked against."""

    name: str
    min_words: int = 40
    max_words: int = 200
    required_keywords: list[str] = field(default_factory=list)
    required_cta_phrases: list[str] = field(default_factory=list)
    forbidden_terms: list[str] = field(default_factory=list)
    weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))


def score_length(text: str, criteria: QualityCriteria) -> float:
    """1.0 within [min_words, max_words], linearly penalized outside it."""
    n = len(split_words(text))
    if criteria.min_words <= n <= criteria.max_words:
        return 1.0
    if n < criteria.min_words:
        if criteria.min_words == 0:
            return 1.0
        return max(0.0, n / criteria.min_words)
    overflow = n - criteria.max_words
    return max(0.0, 1.0 - overflow / max(criteria.max_words, 1))


def score_keywords(text: str, criteria: QualityCriteria) -> float:
    """Fraction of required keywords present (case-insensitive substring match)."""
    if not criteria.required_keywords:
        return 1.0
    lowered = text.lower()
    hits = sum(1 for kw in criteria.required_keywords if kw.lower() in lowered)
    return hits / len(criteria.required_keywords)


def score_cta(text: str, criteria: QualityCriteria) -> float:
    """1.0 if at least one required call-to-action phrase is present."""
    if not criteria.required_cta_phrases:
        return 1.0
    lowered = text.lower()
    return 1.0 if any(p.lower() in lowered for p in criteria.required_cta_phrases) else 0.0


def score_forbidden(text: str, criteria: QualityCriteria) -> float:
    """1.0 if no forbidden terms appear; each occurrence costs 0.25, floor 0."""
    if not criteria.forbidden_terms:
        return 1.0
    lowered = text.lower()
    hits = sum(lowered.count(term.lower()) for term in criteria.forbidden_terms)
    return max(0.0, 1.0 - 0.25 * hits)


def score_readability(text: str) -> float:
    """From-scratch Flesch Reading Ease approximation, normalized to [0, 1]."""
    sentences = split_sentences(text)
    words = split_words(text)
    if not sentences or not words:
        return 0.0
    syllables = sum(count_syllables(w) for w in words)
    words_per_sentence = len(words) / len(sentences)
    syllables_per_word = syllables / len(words)
    flesch = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word
    return max(0.0, min(1.0, flesch / 100))


SCORERS = {
    "length": score_length,
    "keywords": score_keywords,
    "cta": score_cta,
    "forbidden": score_forbidden,
}


def score_all(text: str, criteria: QualityCriteria) -> dict[str, float]:
    """Run every criterion and return a name -> score dict, plus 'composite'."""
    scores = {name: fn(text, criteria) for name, fn in SCORERS.items()}
    scores["readability"] = score_readability(text)

    total_weight = sum(criteria.weights.get(k, 0.0) for k in scores)
    composite = (
        sum(scores[k] * criteria.weights.get(k, 0.0) for k in scores) / total_weight
        if total_weight
        else 0.0
    )
    scores["composite"] = composite
    return scores
