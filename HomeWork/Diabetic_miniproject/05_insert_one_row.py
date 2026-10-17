import csv
from pathlib import Path
from database import get_connection
from service import calculate_risk, clean_row

DATASET = Path(__file__).parent / "diabetic_data.csv"

with open(DATASET, "r", encoding="utf-8-sig") as file:
    first_row = next(csv.DictReader(file))

encounter = clean_row(first_row)
risk = calculate_risk(encounter)
print(f"Encounter: {encounter['encounter_id']}, ->: {risk}")

with get_connection() as connection:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            "INSERT INTO patient_encounters (encounter_id, patient_nbr, age, time_in_hospital, number_inpatient, number_emergency, number_outpatient, num_medications, num_lab_procedures, num_procedures, admission_type_id, discharge_disposition_id, readmitted, risk_score, risk_level, review_reason) " \
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
                risk["review_reason"]
            ),
        )

        if risk["risk_level"] in ("HIGH","MEDIUM"):
            cursor.execute("INSERT INTO care_interventions (encounter_id) VALUES (%s) ON CONFLICT (encounter_id) DO NOTHING")
            
        cursor.execute("SELECT encounter_id, risk_score, risk_level, review_reason FROM patient_encounters WHERE encounter_id = %s", (encounter["encounter_id"],))
        print("In postgreSQL:", cursor.fetchone())
        cursor.execute("SELECT intervention_id, status FROM care_interventions WHERE encounter_id = %s", (encounter["encounter_id"],))
        print("In postgreSQL (care_interventions):", cursor.fetchone())
      