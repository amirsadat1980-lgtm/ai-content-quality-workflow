"""Command-line entry point.

    python -m content_qa.cli run
    python -m content_qa.cli run --provider llm   # requires OPENAI_API_KEY
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .loaders import load_pieces
from .report import to_json, to_markdown
from .rules_provider import RulesProvider
from .workflow import run_workflow

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = ROOT / "examples" / "criteria.json"
DEFAULT_OUTPUT_DIR = ROOT / "results"


def _build_provider(name: str):
    if name == "rules":
        return RulesProvider()
    if name == "llm":
        from .llm_provider import LLMProvider

        return LLMProvider()
    raise ValueError(f"Unknown provider: {name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="content-qa")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Evaluate and revise every example content piece")
    run.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    run.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    run.add_argument("--provider", choices=["rules", "llm"], default="rules")
    run.add_argument("--quiet", action="store_true")

    args = parser.parse_args(argv)
    if args.command != "run":
        parser.error(f"Unknown command: {args.command}")
        return 2

    provider = _build_provider(args.provider)
    pieces = load_pieces(args.manifest)
    results = [run_workflow(text, criteria, provider=provider) for text, criteria in pieces]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    markdown = to_markdown(results)
    (args.output_dir / "sample_report.md").write_text(markdown, encoding="utf-8")
    (args.output_dir / "sample_report.json").write_text(
        json.dumps(to_json(results), indent=2), encoding="utf-8"
    )

    if not args.quiet:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
