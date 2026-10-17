from enum import Enum

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from database import get_connection

app = FastAPI(title="Diabetic Readmission - step by step")


class InterventionStatus(str, Enum):
	PENDING_REVIEW = "PENDING REVIEW"
	IN_PROGRESS = "IN PROGRESS"
	COMPLETED = "COMPLETED"


class InterventionUpdate(BaseModel):
	status: InterventionStatus
	assigned_to: str | None = None
	notes: str | None = None


def get_encounters(limit, offset):
	with get_connection() as connection:
		return connection.execute(
			"""
			SELECT encounter_id, patient_nbr, age, time_in_hospital,
				   risk_score, risk_level, readmitted
			FROM patient_encounters
			ORDER BY encounter_id
			LIMIT %s OFFSET %s
			""",
			(limit, offset),
		).fetchall()


def get_care_queue(risk_level, status, limit, offset):
	with get_connection() as connection:
		return connection.execute(
			"""
			SELECT e.encounter_id, e.patient_nbr, e.age, e.risk_score,
				   e.risk_level, e.review_reason, ci.status, ci.assigned_to,
				   ci.notes, ci.updated_at
			FROM care_interventions AS ci
			JOIN patient_encounters AS e
				ON e.encounter_id = ci.encounter_id
			WHERE e.risk_level IN ('MEDIUM', 'HIGH')
			  AND (%s::text IS NULL OR e.risk_level = %s)
			  AND (%s::text IS NULL OR ci.status = %s)
			ORDER BY CASE WHEN e.risk_level = 'HIGH' THEN 0 ELSE 1 END,
					 e.risk_score DESC, e.encounter_id
			LIMIT %s OFFSET %s
			""",
			(risk_level, risk_level, status, status, limit, offset),
		).fetchall()


def update_intervention_row(encounter_id, status, assigned_to, notes):
	with get_connection() as connection:
		return connection.execute(
			"""
			UPDATE care_interventions
			SET status = %s,
				assigned_to = %s,
				notes = %s,
				updated_at = CURRENT_TIMESTAMP
			WHERE encounter_id = %s
			RETURNING intervention_id, encounter_id, status, assigned_to,
					  notes, updated_at
			""",
			(status, assigned_to, notes, encounter_id),
		).fetchone()


def get_summary():
	with get_connection() as connection:
		encounters = connection.execute(
			"""
			SELECT COUNT(*) AS total_encounters,
				   COUNT(*) FILTER (WHERE risk_level = 'HIGH') AS high_risk,
				   COUNT(*) FILTER (WHERE risk_level = 'MEDIUM') AS medium_risk,
				   COUNT(*) FILTER (WHERE risk_level = 'LOW') AS low_risk
			FROM patient_encounters
			"""
		).fetchone()
		care_queue = connection.execute(
			"""
			SELECT COUNT(*) AS total_care_queue,
				   COUNT(*) FILTER (WHERE status = 'PENDING REVIEW') AS pending_review,
				   COUNT(*) FILTER (WHERE status = 'IN PROGRESS') AS in_progress,
				   COUNT(*) FILTER (WHERE status = 'COMPLETED') AS completed
			FROM care_interventions
			"""
		).fetchone()
		return {"encounters": encounters, "care_queue": care_queue}


@app.get("/health")
def health():
	return {"status": "ok"}


@app.get("/encounters")
def list_encounters(
	limit: int = Query(50, ge=1, le=500),
	offset: int = Query(0, ge=0),
):
	return get_encounters(limit, offset)


@app.get("/care-queue")
def care_queue(
	risk_level: str | None = Query(None),
	status: str | None = Query(None),
	limit: int = Query(100, ge=1, le=500),
	offset: int = Query(0, ge=0),
):
	return get_care_queue(risk_level, status, limit, offset)


@app.get("/summary")
def summary():
	return get_summary()


@app.patch("/interventions/{encounter_id}")
def update_intervention(encounter_id: int, update: InterventionUpdate):
	updated = update_intervention_row(
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
