import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app import main, repository, service
from app.models import PatientSearch, RiskLevel, SearchMatch


def test_patient_search_model_requires_at_least_one_filter():
    with pytest.raises(ValidationError, match="at least one search filter"):
        PatientSearch()


def test_service_passes_all_filters_to_repository(monkeypatch):
    captured = {}

    def fake_search_patients(**kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr(service.repository, "search_patients", fake_search_patients)
    filters = PatientSearch(patient_id=123, risk_level=RiskLevel.HIGH, risk_score=0, match=SearchMatch.OR)

    assert service.search_patients(filters, limit=10, offset=5) == []
    assert captured == {
        "patient_id": 123,
        "patient_nbr": None,
        "risk_level": "HIGH",
        "risk_score": 0,
        "match": "OR",
        "limit": 10,
        "offset": 5,
    }


def test_repository_search_builds_parameterized_optional_filters(monkeypatch):
    captured = {}

    def fake_fetch_all(query, params):
        captured["query"] = query
        captured["params"] = params
        return []

    monkeypatch.setattr(repository, "_fetch_all", fake_fetch_all)

    repository.search_patients(patient_id=123, risk_level="HIGH", risk_score=0, match="OR", limit=10, offset=5)

    assert "(patient_nbr = %s OR encounter_id = %s)" in captured["query"]
    assert "risk_level = %s" in captured["query"]
    assert "risk_score = %s" in captured["query"]
    assert " OR " in captured["query"]
    assert captured["params"] == (123, 123, "HIGH", 0, 10, 5)

def test_repository_search_combines_filters_with_and_by_default(monkeypatch):
    captured = {}

    def fake_fetch_all(query, params):
        captured["query"] = query
        captured["params"] = params
        return []

    monkeypatch.setattr(repository, "_fetch_all", fake_fetch_all)
    repository.search_patients(patient_id=123, risk_level="HIGH", risk_score=5)

    assert " AND " in captured["query"]
    assert " OR risk_level" not in captured["query"]
    assert captured["params"] == (123, 123, "HIGH", 5, 50, 0)

def test_repository_rejects_unsupported_match_operator(monkeypatch):
    with pytest.raises(ValueError, match="AND.*OR"):
        repository.search_patients(patient_id=123, match="XOR")


def test_search_endpoint_requires_at_least_one_filter():
    response = TestClient(main.app).get("/patients/search")

    assert response.status_code == 422
    assert response.json()["detail"] == "Provide at least one of patient_id, patient_nbr, risk_level, or risk_score."


def test_search_endpoint_forwards_filters_and_returns_results(monkeypatch):
    result = [{
        "encounter_id": 456,
        "patient_nbr": 123,
        "age": "51-60",
        "risk_score": 0,
        "risk_level": "LOW",
        "review_reason": "No prioritization rules triggered",
        "readmitted": "NO",
    }]
    captured = {}

    def fake_search_patients(filters, limit, offset):
        captured.update(filters=filters, limit=limit, offset=offset)
        return result

    monkeypatch.setattr(main.service, "search_patients", fake_search_patients)
    response = TestClient(main.app).get(
        "/patients/search?patient_id=123&risk_level=LOW&risk_score=0&match=OR&limit=10&offset=5"
    )

    assert response.status_code == 200
    assert response.json() == result
    assert captured["filters"] == PatientSearch(
        patient_id=123,
        risk_level=RiskLevel.LOW,
        risk_score=0,
        match=SearchMatch.OR,
    )
    assert captured["limit"] == 10
    assert captured["offset"] == 5
