from services.risk_engine import calculate_risk_score, score_to_level, build_risk_response


def test_score_levels():
    assert score_to_level(30) == "LOW"
    assert score_to_level(31) == "MEDIUM"
    assert score_to_level(61) == "HIGH"


def test_income_mismatch_creates_flag():
    score, flags = calculate_risk_score({"verification_findings": [{"type": "income_mismatch", "description": "Income mismatch", "difference_percent": 25, "documents": ["payslip", "tax_return"], "pages": [1, 3]}]})
    assert score == 30
    assert flags[0].severity == "HIGH"


def test_never_auto_approves():
    result = build_risk_response("APP001", {"verification_findings": []})
    assert result["recommendation"] == "NEEDS_HUMAN_REVIEW"
