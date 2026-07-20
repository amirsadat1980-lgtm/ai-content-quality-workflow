"""Ties scoring and revision together: evaluate a draft, and optionally run
it through a provider's revise() step, then re-evaluate to show the delta.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .criteria import QualityCriteria, score_all
from .rules_provider import RulesProvider


def evaluate(text: str, criteria: QualityCriteria) -> dict[str, float]:
    return score_all(text, criteria)


@dataclass
class WorkflowResult:
    name: str
    original_text: str
    original_scores: dict[str, float]
    revised_text: str
    revised_scores: dict[str, float]
    fixes_applied: list[str] = field(default_factory=list)

    @property
    def improved(self) -> bool:
        return self.revised_scores["composite"] >= self.original_scores["composite"]


def run_workflow(text: str, criteria: QualityCriteria, provider=None) -> WorkflowResult:
    """Evaluate, revise once, and re-evaluate — the full generate/evaluate/
    improve loop, using the deterministic RulesProvider by default."""
    provider = provider or RulesProvider()

    original_scores = evaluate(text, criteria)
    revised_text, fixes = provider.revise(text, criteria)
    revised_scores = evaluate(revised_text, criteria)

    return WorkflowResult(
        name=criteria.name,
        original_text=text,
        original_scores=original_scores,
        revised_text=revised_text,
        revised_scores=revised_scores,
        fixes_applied=fixes,
    )
