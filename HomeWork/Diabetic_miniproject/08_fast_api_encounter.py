from fastapi import FastAPI, Query
from database import get_connection

app = FastAPI(title="Diabetic Readmission -step by step")

def get_encounter(limit, offset):
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT encounter_id, patient_nbr, age, time_in_hospital, number_inpatient,
                   risk_level, risk_score, readmitted
            FROM patient_encounters
            ORDER BY encounter_id
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        ).fetchall()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/encounters")
def encounters(limit: int = Query(10, ge=1), offset: int = Query(0, ge=0)):
    return get_encounter(limit, offset)