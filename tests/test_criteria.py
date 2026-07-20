from content_qa.criteria import (
    QualityCriteria,
    score_all,
    score_cta,
    score_forbidden,
    score_keywords,
    score_length,
    score_readability,
)


def make_criteria(**overrides):
    defaults = dict(name="test", min_words=5, max_words=20, required_keywords=[], required_cta_phrases=[], forbidden_terms=[])
    defaults.update(overrides)
    return QualityCriteria(**defaults)


def test_score_length_within_bounds_is_perfect():
    text = " ".join(["word"] * 10)
    assert score_length(text, make_criteria(min_words=5, max_words=20)) == 1.0


def test_score_length_too_short_is_penalized():
    text = " ".join(["word"] * 2)
    score = score_length(text, make_criteria(min_words=10, max_words=20))
    assert 0.0 < score < 1.0


def test_score_length_too_long_is_penalized():
    text = " ".join(["word"] * 40)
    score = score_length(text, make_criteria(min_words=5, max_words=20))
    assert 0.0 <= score < 1.0


def test_score_keywords_counts_fraction_present():
    criteria = make_criteria(required_keywords=["alpha", "beta", "gamma"])
    assert score_keywords("alpha and beta are here", criteria) == 2 / 3


def test_score_keywords_no_requirements_is_perfect():
    assert score_keywords("anything", make_criteria(required_keywords=[])) == 1.0


def test_score_cta_present_and_absent():
    criteria = make_criteria(required_cta_phrases=["sign up now"])
    assert score_cta("Please Sign Up Now for access.", criteria) == 1.0
    assert score_cta("No call to action here.", criteria) == 0.0


def test_score_forbidden_penalizes_each_occurrence():
    criteria = make_criteria(forbidden_terms=["synergy"])
    assert score_forbidden("Great teamwork here.", criteria) == 1.0
    assert score_forbidden("Pure synergy and synergy again.", criteria) == 0.5


def test_score_readability_prefers_simple_sentences():
    simple = "The cat sat on the mat. It was happy."
    complex_ = (
        "The feline organism, having situated itself upon the woven floor "
        "covering, subsequently exhibited indicators consistent with satisfaction."
    )
    assert score_readability(simple) > score_readability(complex_)


def test_score_all_includes_composite_between_zero_and_one():
    criteria = make_criteria(
        required_keywords=["cat"], required_cta_phrases=["adopt today"], forbidden_terms=["bad"]
    )
    scores = score_all("The cat sat on the mat. Adopt today!", criteria)
    assert "composite" in scores
    assert 0.0 <= scores["composite"] <= 1.0
