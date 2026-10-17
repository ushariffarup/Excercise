"""Final solution: HTTP routes only; SQL is in repository.py; rules are in service.py."""

from fastapi import FastAPI, HTTPException, Query

import repository
from models import InterventionUpdate

app = FastAPI(title="Diabetes Readmission Intervention Queue")


@app.get("/health")
def health():
	return {"status": "ok"}


@app.get("/encounters")
def list_encounters(
	limit: int = Query(50, ge=1, le=500),
	offset: int = Query(0, ge=0),
):
	return repository.get_encounters(limit, offset)


@app.get("/care-queue")
def care_queue(
	risk_level: str | None = None,
	status: str | None = None,
	limit: int = Query(100, ge=1, le=500),
	offset: int = Query(0, ge=0),
):
	return repository.get_care_queue(risk_level, status, limit, offset)


@app.patch("/interventions/{encounter_id}")
def update_intervention(encounter_id: int, update: InterventionUpdate):
	updated = repository.update_intervention(
		encounter_id,
		update.status.value,
		update.assigned_to,
		update.notes,
	)
	if updated is None:
		raise HTTPException(
			status_code=404,
			detail=f"No care intervention for encounter {encounter_id}",
		)
	return updated


@app.get("/operations/summary")
def operations_summary():
	return repository.get_summary()
