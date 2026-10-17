from fastapi import FastAPI, Query

from database import get_connection

app = FastAPI(title="Diabetic Readmission - step by step")


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


@app.get("/health")
def health():
	return {"status": "ok"}


@app.get("/encounters")
def encounters(limit: int = Query(10, ge=1), offset: int = Query(0, ge=0)):
	return get_encounters(limit, offset)


@app.get("/care-queue")
def care_queue(
	risk_level: str | None = Query(None),
	status: str | None = Query(None),
	limit: int = Query(10, ge=1),
	offset: int = Query(0, ge=0),
):
	return get_care_queue(risk_level, status, limit, offset)
