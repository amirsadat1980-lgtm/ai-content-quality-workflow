from content_qa.criteria import QualityCriteria
from content_qa.rules_provider import RulesProvider


def make_criteria(**overrides):
    defaults = dict(
        name="test", min_words=1, max_words=1000, required_keywords=[],
        required_cta_phrases=[], forbidden_terms=[],
    )
    defaults.update(overrides)
    return QualityCriteria(**defaults)


def test_revise_removes_forbidden_terms():
    provider = RulesProvider()
    criteria = make_criteria(forbidden_terms=["synergy"])
    revised, fixes = provider.revise("Pure synergy today.", criteria)
    assert "synergy" not in revised.lower()
    assert any("synergy" in f for f in fixes)


def test_revise_appends_missing_cta():
    provider = RulesProvider()
    criteria = make_criteria(required_cta_phrases=["sign up now"])
    revised, fixes = provider.revise("Great product.", criteria)
    assert "sign up now" in revised.lower()
    assert any("call-to-action" in f for f in fixes)


def test_revise_does_not_duplicate_existing_cta():
    provider = RulesProvider()
    criteria = make_criteria(required_cta_phrases=["sign up now"])
    revised, fixes = provider.revise("Great product. Sign up now!", criteria)
    assert revised.lower().count("sign up now") == 1
    assert not any("call-to-action" in f for f in fixes)


def test_revise_trims_to_max_words():
    provider = RulesProvider()
    criteria = make_criteria(max_words=5)
    revised, fixes = provider.revise(" ".join(["word"] * 20), criteria)
    assert len(revised.split()) <= 5
    assert any("trimmed" in f for f in fixes)


def test_revise_no_changes_needed_reports_no_fixes():
    provider = RulesProvider()
    criteria = make_criteria(max_words=100)
    revised, fixes = provider.revise("Short and fine.", criteria)
    assert revised == "Short and fine."
    assert fixes == []
