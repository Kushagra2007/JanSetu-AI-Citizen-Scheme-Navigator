from types import SimpleNamespace
from scoring import compute_eligibility_score, compute_profile_completeness
import json


def make_scheme(**kwargs):
    defaults = dict(
        min_age=18, max_age=40, max_income=200000, gender="All",
        caste_categories="[]", occupations='["farmer"]', states='["All"]',
        education="[]", marital_status="Any", disability_required=False,
        documents_required='["aadhaar", "bank"]',
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def make_profile(**kwargs):
    defaults = dict(age=25, gender="Male", income=150000, occupation="farmer",
                     state="Bihar", category="General", education="10th",
                     marital_status="Unmarried", disability=False)
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def make_doc(doc_type, has_document=True):
    return SimpleNamespace(doc_type=doc_type, has_document=has_document)


def test_full_match_high_score():
    scheme = make_scheme()
    profile = make_profile()
    docs = [make_doc("aadhaar"), make_doc("bank")]
    result = compute_eligibility_score(profile, docs, scheme)
    assert result["eligible"] is True
    assert result["total_score"] > 80


def test_failed_age_criteria():
    scheme = make_scheme(min_age=18, max_age=40)
    profile = make_profile(age=55)
    docs = [make_doc("aadhaar"), make_doc("bank")]
    result = compute_eligibility_score(profile, docs, scheme)
    assert "Age range" in result["failed_criteria"]
    assert result["eligible"] is False


def test_missing_documents_lowers_score():
    scheme = make_scheme()
    profile = make_profile()
    docs = []
    result = compute_eligibility_score(profile, docs, scheme)
    assert result["document_score"] == 0
    assert set(result["missing_documents"]) == {"aadhaar", "bank"}


def test_income_exceeds_limit():
    scheme = make_scheme(max_income=100000)
    profile = make_profile(income=500000)
    docs = [make_doc("aadhaar"), make_doc("bank")]
    result = compute_eligibility_score(profile, docs, scheme)
    assert "Income limit" in result["failed_criteria"]


def test_profile_completeness_calculation():
    profile = make_profile()
    score = compute_profile_completeness(profile)
    assert score == 100.0


def test_profile_completeness_partial():
    profile = make_profile(age=None, gender=None)
    score = compute_profile_completeness(profile)
    assert 0 < score < 100