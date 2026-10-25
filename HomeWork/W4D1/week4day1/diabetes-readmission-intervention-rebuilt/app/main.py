from typing import Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from app import repository, service
from app.config import APP_NAME, get_cors_origins
from app.errors import ConfigurationError, DatabaseUnavailableError, InvalidInputError, NotFoundError
from app.models import (
    EncounterCreate, EncounterResponse, HealthResponse, Intervention,
    InterventionHistoryItem, InterventionStatus, InterventionUpdate,
    ManagementDashboard, OperationsSummary, PatientSearchResult,
    Readmitted, ReadmissionAnalysis, RiskLevel
)
app = FastAPI(title=APP_NAME, description="EDUCATIONAL PROTOTYPE - not clinically validated and not for patient-care decisions. Risk rules are illustrative; the historical `readmitted` outcome is never used for scoring.")
app.add_middleware(CORSMiddleware, allow_origins=get_cors_origins(), allow_methods=["*"], allow_headers=["*"])
def _get_ui_file() -> Optional[Path]:
    candidates = [
        Path(__file__).resolve().parent.parent / "frontend" / "add_patient.html",
        Path(__file__).resolve().parent.parent / "frontend" / "index.html",
        Path(__file__).resolve().parent.parent / "index.html",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None

LIMIT = Query(50, ge=1, le=500, description="Page size")
OFFSET = Query(0, ge=0, description="Rows to skip")

@app.exception_handler(NotFoundError)
def handle_not_found(request, exc): return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(InvalidInputError)
def handle_invalid_input(request, exc): return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(DatabaseUnavailableError)
def handle_database_unavailable(request, exc): return JSONResponse(status_code=503, content={"detail": "Database is unavailable. Try again later."})

@app.exception_handler(ConfigurationError)
def handle_configuration(request, exc): return JSONResponse(status_code=500, content={"detail": "Application is not configured correctly. Check the server environment."})

def _value(option): return option.value if option else None

@app.get("/", include_in_schema=False)
def serve_index():
    ui_file = _get_ui_file()
    if ui_file and ui_file.exists():
        return FileResponse(ui_file)
    return {"status": "ok", "message": "Backend online. UI file not found."}

@app.get("/health", response_model=HealthResponse, summary="Service health check")
def health(): return {"status": "ok"}

@app.get("/encounters", summary="List diabetes encounters")
def list_encounters(risk_level: Optional[RiskLevel] = None, readmitted: Optional[Readmitted] = None, order: Optional[str] = Query("asc", description="Sort order: asc or desc"), limit: int = LIMIT, offset: int = OFFSET):
    return repository.list_encounters(_value(risk_level), _value(readmitted), limit, offset, order)

@app.post("/encounters", response_model=EncounterResponse, status_code=201, summary="Add a new patient encounter")
def create_encounter(payload: EncounterCreate):
    created = service.create_encounter(payload.model_dump())
    if not created:
        raise InvalidInputError("Failed to create encounter")
    return created

@app.get("/encounters/{encounter_id}", summary="Get one encounter with its intervention")
def get_encounter(encounter_id: int):
    encounter = repository.get_encounter(encounter_id)
    if encounter is None: raise NotFoundError(f"Encounter {encounter_id} not found")
    return encounter

@app.get("/care-queue", summary="View the MEDIUM + HIGH risk care queue")
def get_care_queue(risk_level: Optional[RiskLevel] = None, status: Optional[InterventionStatus] = None, assigned_to: Optional[str] = None, limit: int = LIMIT, offset: int = OFFSET):
    return repository.list_care_queue(_value(risk_level), _value(status), assigned_to, limit, offset)

@app.get("/care-queue/high", summary="View the high-risk care queue")
def get_high_risk_queue(status: Optional[InterventionStatus] = None, assigned_to: Optional[str] = None, limit: int = LIMIT, offset: int = OFFSET):
    return repository.list_care_queue("HIGH", _value(status), assigned_to, limit, offset)

@app.patch("/interventions/{encounter_id}", response_model=Intervention, summary="Update care intervention")
def update_intervention(encounter_id: int, payload: InterventionUpdate):
    updated = repository.update_intervention(encounter_id, _value(payload.status), payload.assigned_to, payload.notes)
    if updated is None:
        if repository.get_encounter(encounter_id) is None: raise NotFoundError(f"Encounter {encounter_id} not found")
        raise NotFoundError(f"Encounter {encounter_id} has no care intervention (only MEDIUM/HIGH risk encounters are queued)")
    return updated

@app.get("/patients/search", response_model=list[PatientSearchResult], summary="Search patients by patient number, risk score and/or risk level")
def search_patients(patient_nbr: Optional[int] = Query(None, description="Patient number (patient_nbr)"), risk_score: Optional[int] = Query(None, ge=0, le=8, description="Exact risk score, 0-8"), risk_level: Optional[RiskLevel] = None, limit: int = LIMIT, offset: int = OFFSET):
    """Any combination of filters (AND). Results are HIGH first. Each row includes its care intervention status (null for LOW risk, which is not queued)."""
    filters = service.normalize_search(patient_nbr, risk_score, _value(risk_level), limit, offset)
    return repository.search_patients(**filters)

@app.get("/interventions/{encounter_id}", response_model=Intervention, summary="Get the care intervention (status) for one encounter")
def get_intervention(encounter_id: int):
    intervention = repository.get_intervention(encounter_id)
    if intervention is None:
        if repository.get_encounter(encounter_id) is None: raise NotFoundError(f"Encounter {encounter_id} not found")
        raise NotFoundError(f"Encounter {encounter_id} has no care intervention (only MEDIUM/HIGH risk encounters are queued)")
    return intervention

@app.get("/interventions/{encounter_id}/history", response_model=list[InterventionHistoryItem], summary="Audit history of status changes for one encounter, newest first")
def get_intervention_history(encounter_id: int):
    if repository.get_encounter(encounter_id) is None: raise NotFoundError(f"Encounter {encounter_id} not found")
    return repository.get_intervention_history(encounter_id)

@app.get("/operations/summary", response_model=OperationsSummary, summary="Operational queue and workload metrics")
def operations_summary(): return service.build_operations_summary(repository.get_risk_counts(), repository.get_status_counts())

@app.get("/operations/readmission-analysis", response_model=ReadmissionAnalysis, summary="Compare risk levels with historical readmission outcomes")
def readmission_analysis():
    """Compares risk groups (scored WITHOUT the outcome) with the historical `<30` readmission field. Retrospective validation only - differing rates do not prove the rules are clinically predictive."""
    return service.build_readmission_analysis(repository.get_risk_group_outcomes())

@app.get("/management/dashboard", response_model=ManagementDashboard, summary="Executive summary metrics")
def management_dashboard(): return service.build_management_dashboard(repository.get_risk_group_outcomes(), repository.count_pending_interventions())
