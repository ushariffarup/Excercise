def insert_encounter(cursor, encounter, risk):
	cursor.execute(
		"""
		INSERT INTO patient_encounters (
			encounter_id, patient_nbr, age, time_in_hospital,
			number_inpatient, number_emergency, number_outpatient,
			num_medications, num_lab_procedures, num_procedures,
			admission_type_id, discharge_disposition_id, readmitted,
			risk_score, risk_level, review_reason
		)
		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
		ON CONFLICT (encounter_id) DO NOTHING
		""",
		(
			encounter["encounter_id"],
			encounter["patient_nbr"],
			encounter["age"],
			encounter["time_in_hospital"],
			encounter["number_inpatient"],
			encounter["number_emergency"],
			encounter["number_outpatient"],
			encounter["num_medications"],
			encounter["num_lab_procedures"],
			encounter["num_procedures"],
			encounter["admission_type_id"],
			encounter["discharge_disposition_id"],
			encounter["readmitted"],
			risk["risk_score"],
			risk["risk_level"],
			risk["review_reason"],
		),
	)
	return cursor.rowcount == 1


def create_intervention(cursor, encounter_id):
	cursor.execute(
		"""
		INSERT INTO care_interventions (encounter_id)
		VALUES (%s)
		ON CONFLICT (encounter_id) DO NOTHING
		""",
		(encounter_id,),
	)
	return cursor.rowcount == 1


def count_care_queue(cursor):
	cursor.execute("SELECT COUNT(*) AS total FROM care_interventions")
	return cursor.fetchone()["total"]


def fetch_all(query, params=()):
	from database import get_connection

	with get_connection() as connection:
		with connection.cursor() as cursor:
			cursor.execute(query, params)
			return cursor.fetchall()


def get_encounters(limit, offset):
	return fetch_all(
		"""
		SELECT encounter_id, patient_nbr, age, time_in_hospital,
			   risk_score, risk_level, readmitted
		FROM patient_encounters
		ORDER BY encounter_id
		LIMIT %s OFFSET %s
		""",
		(limit, offset),
	)


def get_care_queue(risk_level, status, limit, offset):
	return fetch_all(
		"""
		SELECT e.encounter_id, e.patient_nbr, e.age, e.risk_score,
		       e.risk_level, e.review_reason, ci.status, ci.assigned_to,
		       ci.notes, ci.updated_at
		FROM care_interventions AS ci
		JOIN patient_encounters AS e ON e.encounter_id = ci.encounter_id
		WHERE e.risk_level IN ('MEDIUM', 'HIGH')
		  AND (%s::text IS NULL OR e.risk_level = %s)
		  AND (%s::text IS NULL OR ci.status = %s)
		ORDER BY CASE WHEN e.risk_level = 'HIGH' THEN 0 ELSE 1 END,
		         e.risk_score DESC, e.encounter_id
		LIMIT %s OFFSET %s
		""",
		(risk_level, risk_level, status, status, limit, offset),
	)


def update_intervention(encounter_id, status, assigned_to, notes):
	return fetch_one(
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
	)


def fetch_one(query, params=()):
	from database import get_connection

	with get_connection() as connection:
		with connection.cursor() as cursor:
			cursor.execute(query, params)
			return cursor.fetchone()


def get_summary():
	from database import get_connection

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
