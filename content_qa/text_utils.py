"""Small, dependency-free text helpers used by the scoring criteria."""

from __future__ import annotations

import re

_WORD_RE = re.compile(r"[A-Za-z']+")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def split_words(text: str) -> list[str]:
    return _WORD_RE.findall(text)


def split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(text) if s.strip()]


def count_syllables(word: str) -> int:
    word = word.lower()
    groups = re.findall(r"[aeiouy]+", word)
    count = len(groups)
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def truncate_to_words(text: str, max_words: int) -> str:
    """Trim to at most max_words, preferring to drop whole trailing sentences
    over cutting one off mid-thought. Falls back to a hard word cut only if
    even the first sentence alone exceeds the budget."""
    if len(_WORD_RE.findall(text)) <= max_words:
        return text

    sentences = split_sentences(text)
    kept: list[str] = []
    for sentence in sentences:
        candidate = kept + [sentence]
        if len(_WORD_RE.findall(" ".join(candidate))) > max_words:
            break
        kept = candidate

    if kept:
        return " ".join(kept)

    matches = list(_WORD_RE.finditer(text))
    end = matches[max_words - 1].end()
    return text[:end].rstrip().rstrip(",.;:") + "."
