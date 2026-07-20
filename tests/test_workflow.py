from pathlib import Path

from content_qa.criteria import QualityCriteria
from content_qa.loaders import load_pieces
from content_qa.workflow import run_workflow

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "examples" / "criteria.json"


def test_load_pieces_reads_all_examples():
    pieces = load_pieces(MANIFEST)
    assert len(pieces) == 3
    ids = {c.name for _, c in pieces}
    assert ids == {"well_formed_ad", "too_long_no_cta", "jargon_violation"}


def test_run_workflow_on_well_formed_ad_needs_no_fixes():
    pieces = dict((c.name, (t, c)) for t, c in load_pieces(MANIFEST))
    text, criteria = pieces["well_formed_ad"]
    result = run_workflow(text, criteria)
    assert result.fixes_applied == []
    assert result.revised_scores["composite"] == result.original_scores["composite"]


def test_run_workflow_on_jargon_violation_improves_composite():
    pieces = dict((c.name, (t, c)) for t, c in load_pieces(MANIFEST))
    text, criteria = pieces["jargon_violation"]
    result = run_workflow(text, criteria)
    assert result.fixes_applied  # at least one fix was applied
    assert result.revised_scores["composite"] > result.original_scores["composite"]
    assert result.improved


def test_run_workflow_on_too_long_no_cta_trims_and_adds_cta():
    pieces = dict((c.name, (t, c)) for t, c in load_pieces(MANIFEST))
    text, criteria = pieces["too_long_no_cta"]
    result = run_workflow(text, criteria)
    assert len(result.revised_text.split()) <= criteria.max_words
    assert any(p in result.revised_text.lower() for p in criteria.required_cta_phrases)
    assert result.improved
