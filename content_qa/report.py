"""Markdown/JSON reporting for a batch of WorkflowResults."""

from __future__ import annotations

from .workflow import WorkflowResult


def _pct(x: float) -> str:
    return f"{x * 100:.0f}%"


def to_markdown(results: list[WorkflowResult]) -> str:
    lines = ["# Content Quality Report", ""]
    header = ["Piece", "Composite (before)", "Composite (after)", "Fixes applied"]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * len(header))
    for r in results:
        fixes = "; ".join(r.fixes_applied) or "(none needed)"
        lines.append(
            f"| {r.name} | {_pct(r.original_scores['composite'])} | "
            f"{_pct(r.revised_scores['composite'])} | {fixes} |"
        )

    lines.append("")
    lines.append("## Detail")
    for r in results:
        lines.append("")
        lines.append(f"### {r.name}")
        lines.append("")
        lines.append("**Original:**")
        lines.append(f"> {r.original_text}")
        lines.append("")
        lines.append(
            "Scores: "
            + ", ".join(f"{k}: {_pct(v)}" for k, v in r.original_scores.items())
        )
        lines.append("")
        lines.append("**Revised:**")
        lines.append(f"> {r.revised_text}")
        lines.append("")
        lines.append(
            "Scores: "
            + ", ".join(f"{k}: {_pct(v)}" for k, v in r.revised_scores.items())
        )
    return "\n".join(lines) + "\n"


def to_json(results: list[WorkflowResult]) -> dict:
    return {
        "results": [
            {
                "name": r.name,
                "original_text": r.original_text,
                "original_scores": {k: round(v, 4) for k, v in r.original_scores.items()},
                "revised_text": r.revised_text,
                "revised_scores": {k: round(v, 4) for k, v in r.revised_scores.items()},
                "fixes_applied": r.fixes_applied,
                "improved": r.improved,
            }
            for r in results
        ]
    }
