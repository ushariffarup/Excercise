import pytest
from fastapi.testclient import TestClient
from app import repository
from app.errors import InvalidInputError
from app.main import app
from app.service import build_operations_summary, normalize_search

client = TestClient(app)

# ---- service: validation and normalization (no database) ----
def test_normalize_defaults():
    assert normalize_search() == {"patient_nbr": None, "risk_score": None, "risk_level": None, "limit": 50, "offset": 0}

def test_normalize_uppercases_level_and_clamps_paging():
    result = normalize_search(risk_level=" high ", limit=9999, offset=-5)
    assert (result["risk_level"], result["limit"], result["offset"]) == ("HIGH", 500, 0)

@pytest.mark.parametrize("kwargs", [{"patient_nbr": 0}, {"patient_nbr": -4}, {"risk_score": 9}, {"risk_score": -1}, {"risk_level": "EXTREME"}])
def test_normalize_rejects_bad_input(kwargs):
    with pytest.raises(InvalidInputError): normalize_search(**kwargs)

def test_summary_exposes_completed_as_closed():
    summary = build_operations_summary({"total_encounters": 3, "high_risk": 1, "medium_risk": 1, "low_risk": 1}, [{"status": "CLOSED", "count": 2}])
    assert summary["closed_interventions"] == summary["completed_interventions"] == 2

# ---- routes: validation and error mapping (repository is faked, no database) ----
def test_search_rejects_out_of_range_score():
    assert client.get("/patients/search", params={"risk_score": 9}).status_code == 422

def test_search_rejects_unknown_level():
    assert client.get("/patients/search", params={"risk_level": "BAD"}).status_code == 422

def test_search_service_error_is_400():
    assert client.get("/patients/search", params={"patient_nbr": 0}).status_code == 400

def test_search_passes_filters_to_repository(monkeypatch):
    seen = {}
    def fake(**kwargs): seen.update(kwargs); return []
    monkeypatch.setattr(repository, "search_patients", fake)
    response = client.get("/patients/search", params={"patient_nbr": 5, "risk_score": 3, "risk_level": "MEDIUM", "limit": 10, "offset": 20})
    assert response.status_code == 200 and response.json() == []
    assert seen == {"patient_nbr": 5, "risk_score": 3, "risk_level": "MEDIUM", "limit": 10, "offset": 20}

def test_get_intervention_missing_encounter_is_404(monkeypatch):
    monkeypatch.setattr(repository, "get_intervention", lambda encounter_id: None)
    monkeypatch.setattr(repository, "get_encounter", lambda encounter_id: None)
    response = client.get("/interventions/1")
    assert response.status_code == 404 and "not found" in response.json()["detail"]

def test_get_intervention_low_risk_is_404_with_reason(monkeypatch):
    monkeypatch.setattr(repository, "get_intervention", lambda encounter_id: None)
    monkeypatch.setattr(repository, "get_encounter", lambda encounter_id: {"encounter_id": encounter_id})
    response = client.get("/interventions/1")
    assert response.status_code == 404 and "no care intervention" in response.json()["detail"]

def test_history_missing_encounter_is_404(monkeypatch):
    monkeypatch.setattr(repository, "get_encounter", lambda encounter_id: None)
    assert client.get("/interventions/1/history").status_code == 404

def test_cors_allows_vite_origin_only():
    allowed = client.get("/health", headers={"Origin": "http://localhost:5173"})
    blocked = client.get("/health", headers={"Origin": "http://evil.example"})
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert "access-control-allow-origin" not in blocked.headers

def test_create_encounter_rejects_non_positive_patient_nbr():
    response = client.post("/encounters", json={"patient_nbr": 0, "age": "[50-60)"})
    assert response.status_code == 400

def test_create_encounter_success(monkeypatch):
    def fake_create(data):
        return {
            "encounter_id": 99999,
            "patient_nbr": data["patient_nbr"],
            "age": data["age"],
            "time_in_hospital": data["time_in_hospital"],
            "number_inpatient": data["number_inpatient"],
            "number_emergency": data["number_emergency"],
            "number_outpatient": data["number_outpatient"],
            "num_medications": data["num_medications"],
            "risk_score": data["risk_score"],
            "risk_level": data["risk_level"],
            "review_reason": data["review_reason"],
            "intervention_id": 100 if data["risk_level"] != "LOW" else None,
            "status": "PENDING_REVIEW" if data["risk_level"] != "LOW" else None
        }
    monkeypatch.setattr(repository, "create_encounter", fake_create)
    response = client.post("/encounters", json={
        "patient-number": 12345,
        "age": "[60-70)",
        "hospital": 8,
        "inpatient": 3,
        "emergency": 2,
        "medications": 25
    })
    assert response.status_code == 201
    data = response.json()
    assert data["patient_nbr"] == 12345
    assert data["risk_level"] == "HIGH"
    assert data["status"] == "PENDING_REVIEW"

