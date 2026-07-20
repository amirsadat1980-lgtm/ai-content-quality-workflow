from pathlib import Path

from content_qa.loaders import load_pieces
from content_qa.report import to_json, to_markdown
from content_qa.workflow import run_workflow

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "examples" / "criteria.json"


def _run_all():
    pieces = load_pieces(MANIFEST)
    return [run_workflow(text, criteria) for text, criteria in pieces]


def test_to_markdown_includes_every_piece():
    results = _run_all()
    markdown = to_markdown(results)
    for r in results:
        assert r.name in markdown


def test_to_json_shape():
    results = _run_all()
    payload = to_json(results)
    assert len(payload["results"]) == len(results)
    for entry in payload["results"]:
        assert 0.0 <= entry["original_scores"]["composite"] <= 1.0
        assert 0.0 <= entry["revised_scores"]["composite"] <= 1.0
        assert "improved" in entry
