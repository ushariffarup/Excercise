"""All SQL lives here. Every value is passed as a psycopg parameter (%s); only fixed SQL fragments are ever joined into a query."""
from app.database import get_connection
ENCOUNTER_COLUMNS = ("encounter_id", "patient_nbr", "age", "time_in_hospital", "number_inpatient", "number_emergency", "number_outpatient", "num_medications", "num_lab_procedures", "num_procedures", "admission_type_id", "discharge_disposition_id", "readmitted", "risk_score", "risk_level", "review_reason")
QUEUE_SELECT = """
    SELECT e.encounter_id, e.patient_nbr, e.age, e.risk_score, e.risk_level, e.review_reason,
           ci.intervention_id, ci.status, ci.assigned_to, ci.notes, ci.created_at, ci.updated_at
    FROM care_interventions ci
    JOIN patient_encounters e ON e.encounter_id = ci.encounter_id
"""

def _fetch_all(query, params=()):
    with get_connection() as conn: return conn.execute(query, params).fetchall()

def _fetch_one(query, params=()):
    with get_connection() as conn: return conn.execute(query, params).fetchone()

def _where(clauses: list) -> str:
    return f"WHERE {' AND '.join(clauses)}" if clauses else ""

def list_encounters(risk_level, readmitted, limit, offset, order="asc"):
    clauses, params = [], []
    if risk_level: clauses.append("risk_level = %s"); params.append(risk_level)
    if readmitted: clauses.append("readmitted = %s"); params.append(readmitted)
    dir_str = "DESC" if order and str(order).lower() == "desc" else "ASC"
    return _fetch_all(f"SELECT * FROM patient_encounters {_where(clauses)} ORDER BY encounter_id {dir_str} LIMIT %s OFFSET %s", (*params, limit, offset))

def create_encounter(encounter_data: dict) -> dict:
    """Inserts a new patient encounter and automatically queues care intervention if MEDIUM or HIGH risk."""
    query = """
        WITH next_id AS (
            SELECT COALESCE(MAX(encounter_id), 0) + 1 AS new_id FROM patient_encounters
        ),
        inserted_enc AS (
            INSERT INTO patient_encounters (
                encounter_id, patient_nbr, age, time_in_hospital, number_inpatient,
                number_emergency, number_outpatient, num_medications, num_lab_procedures,
                num_procedures, admission_type_id, discharge_disposition_id, readmitted,
                risk_score, risk_level, review_reason, created_at
            )
            SELECT
                new_id, %(patient_nbr)s, %(age)s, %(time_in_hospital)s, %(number_inpatient)s,
                %(number_emergency)s, %(number_outpatient)s, %(num_medications)s, %(num_lab_procedures)s,
                %(num_procedures)s, %(admission_type_id)s, %(discharge_disposition_id)s, %(readmitted)s,
                %(risk_score)s, %(risk_level)s, %(review_reason)s, CURRENT_TIMESTAMP
            FROM next_id
            RETURNING *
        )
        SELECT * FROM inserted_enc;
    """
    row = _fetch_one(query, encounter_data)
    if not row:
        return None

    if row.get("risk_level") in ("MEDIUM", "HIGH"):
        ci_row = _fetch_one("""
            INSERT INTO care_interventions (encounter_id, status)
            VALUES (%s, 'PENDING_REVIEW')
            ON CONFLICT (encounter_id) DO UPDATE SET encounter_id = EXCLUDED.encounter_id
            RETURNING intervention_id, status;
        """, (row["encounter_id"],))
        if ci_row:
            row["intervention_id"] = ci_row["intervention_id"]
            row["status"] = ci_row["status"]
    else:
        row["intervention_id"] = None
        row["status"] = None

    return row

def get_encounter(encounter_id):
    return _fetch_one("""
        SELECT e.*, ci.intervention_id, ci.status AS intervention_status, ci.assigned_to, ci.notes AS intervention_notes,
               ci.created_at AS intervention_created_at, ci.updated_at AS intervention_updated_at
        FROM patient_encounters e
        LEFT JOIN care_interventions ci ON ci.encounter_id = e.encounter_id
        WHERE e.encounter_id = %s
    """, (encounter_id,))

def list_care_queue(risk_level, status, assigned_to, limit, offset):
    clauses, params = ["e.risk_level IN ('MEDIUM', 'HIGH')"], []
    if risk_level: clauses.append("e.risk_level = %s"); params.append(risk_level)
    if status: clauses.append("ci.status = %s"); params.append(status)
    if assigned_to: clauses.append("ci.assigned_to = %s"); params.append(assigned_to)
    order = "ORDER BY CASE e.risk_level WHEN 'HIGH' THEN 0 ELSE 1 END, ci.created_at, ci.intervention_id"
    return _fetch_all(f"{QUEUE_SELECT} {_where(clauses)} {order} LIMIT %s OFFSET %s", (*params, limit, offset))

def update_intervention(encounter_id, status, assigned_to, notes):
    """Returns the updated row (with patient_nbr, risk_level, risk_score), or None when the encounter does not exist. Fields left as None are kept unchanged."""
    if get_encounter(encounter_id) is None:
        return None
    return _fetch_one("""
        WITH u AS (
            INSERT INTO care_interventions (encounter_id, status, assigned_to, notes)
            VALUES (%s, COALESCE(%s, 'PENDING_REVIEW'), %s, %s)
            ON CONFLICT (encounter_id) DO UPDATE
            SET status = COALESCE(EXCLUDED.status, care_interventions.status),
                assigned_to = COALESCE(EXCLUDED.assigned_to, care_interventions.assigned_to),
                notes = COALESCE(EXCLUDED.notes, care_interventions.notes),
                updated_at = CURRENT_TIMESTAMP
            RETURNING intervention_id, encounter_id, status, assigned_to, notes, created_at, updated_at
        )
        SELECT u.intervention_id, u.encounter_id, e.patient_nbr, e.risk_level, e.risk_score, u.status, u.assigned_to, u.notes, u.created_at, u.updated_at
        FROM u JOIN patient_encounters e ON e.encounter_id = u.encounter_id
    """, (encounter_id, status, assigned_to, notes))

def search_patients(patient_nbr, risk_score, risk_level, limit, offset):
    """Any combination of filters (AND). LEFT JOIN so LOW-risk encounters (no intervention) are still returned. HIGH first."""
    clauses, params = [], []
    if patient_nbr is not None: clauses.append("e.patient_nbr = %s"); params.append(patient_nbr)
    if risk_score is not None: clauses.append("e.risk_score = %s"); params.append(risk_score)
    if risk_level: clauses.append("e.risk_level = %s"); params.append(risk_level)
    order = "ORDER BY CASE e.risk_level WHEN 'HIGH' THEN 0 WHEN 'MEDIUM' THEN 1 ELSE 2 END, e.risk_score DESC, e.encounter_id"
    return _fetch_all(f"""
        SELECT e.encounter_id, e.patient_nbr, e.age, e.time_in_hospital, e.number_inpatient, e.number_emergency, e.number_outpatient,
               e.num_medications, e.num_lab_procedures, e.discharge_disposition_id, e.admission_type_id, e.readmitted,
               e.risk_score, e.risk_level, e.review_reason,
               ci.intervention_id, ci.status, ci.status AS intervention_status, ci.assigned_to, ci.notes
        FROM patient_encounters e
        LEFT JOIN care_interventions ci ON ci.encounter_id = e.encounter_id
        {_where(clauses)} {order} LIMIT %s OFFSET %s
    """, (*params, limit, offset))

def get_intervention(encounter_id):
    """None when the encounter has no intervention (missing encounter or LOW risk)."""
    return _fetch_one("""
        SELECT ci.intervention_id, ci.encounter_id, e.patient_nbr, e.risk_level, e.risk_score,
               ci.status, ci.assigned_to, ci.notes, ci.created_at, ci.updated_at
        FROM care_interventions ci JOIN patient_encounters e ON e.encounter_id = ci.encounter_id
        WHERE ci.encounter_id = %s
    """, (encounter_id,))

def get_intervention_history(encounter_id):
    """Audit trail, newest first."""
    return _fetch_all("""
        SELECT h.history_id, h.encounter_id, e.patient_nbr, h.status, h.assigned_to, h.notes, h.changed_at
        FROM care_intervention_history h JOIN patient_encounters e ON e.encounter_id = h.encounter_id
        WHERE h.encounter_id = %s
        ORDER BY h.changed_at DESC, h.history_id DESC
    """, (encounter_id,))

def get_risk_counts():
    return _fetch_one("""
        SELECT COUNT(*) AS total_encounters,
               COUNT(*) FILTER (WHERE risk_level = 'HIGH') AS high_risk,
               COUNT(*) FILTER (WHERE risk_level = 'MEDIUM') AS medium_risk,
               COUNT(*) FILTER (WHERE risk_level = 'LOW') AS low_risk
        FROM patient_encounters
    """)

def get_status_counts():
    return _fetch_all("SELECT status, COUNT(*) AS count FROM care_interventions GROUP BY status")

def get_risk_group_outcomes():
    """Per risk group: encounter count and historical <30 readmissions. `readmitted` is used here only AFTER scoring, for retrospective validation."""
    return _fetch_all("""
        SELECT risk_level, COUNT(*) AS encounters, COUNT(*) FILTER (WHERE readmitted = '<30') AS readmitted_under_30
        FROM patient_encounters GROUP BY risk_level
    """)

def count_pending_interventions():
    return _fetch_one("SELECT COUNT(*) AS count FROM care_interventions WHERE status = 'PENDING_REVIEW'")["count"]

# --- importer / setup helpers (take an open connection so the whole import is one transaction) ---
def count_rows(conn, table):
    """`table` must be one of the project's own tables, never user input."""
    if table not in ("patient_encounters", "care_interventions", "care_intervention_history"): raise ValueError(f"Unknown table: {table}")
    return conn.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"]

def upsert_encounters(conn, rows):
    columns = ENCOUNTER_COLUMNS
    updates = ", ".join(f"{column} = EXCLUDED.{column}" for column in columns if column != "encounter_id")
    query = f"INSERT INTO patient_encounters ({', '.join(columns)}) VALUES ({', '.join(f'%({c})s' for c in columns)}) ON CONFLICT (encounter_id) DO UPDATE SET {updates}"
    with conn.cursor() as cursor: cursor.executemany(query, rows)

def create_interventions(conn, encounter_ids):
    with conn.cursor() as cursor: cursor.executemany("INSERT INTO care_interventions (encounter_id) VALUES (%s) ON CONFLICT (encounter_id) DO NOTHING", [(encounter_id,) for encounter_id in encounter_ids])

def table_exists(conn, table):
    return conn.execute("SELECT to_regclass(%s) IS NOT NULL AS found", (f"public.{table}",)).fetchone()["found"]
