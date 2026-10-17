import csv
from pathlib import Path
import sys
from database import get_connection
from repository import count_care_queue, create_intervention, insert_encounter
from service import calculate_risk, clean_row

DATASET = Path(__file__).parent / "diabetic_data.csv"

REQUIRED_COLUMNS = [
    "encounter_id", "patient_nbr", "age", "time_in_hospital", "number_inpatient",
    "number_emergency", "number_outpatient", "num_medications", "num_lab_procedures",
    "num_procedures", "admission_type_id", "discharge_disposition_id", "readmitted"
]
def check_headers(headers):
    missing = [column for column in REQUIRED_COLUMNS if column not in (headers or []) ]
    if missing: sys.exit("Missing required columns:\n" + "\n".join(missing))

def main():
    if not DATASET.exists(): sys.exit(f"Dataset not found.{DATASET}\n Put diabetic_data.csv in the same directory.")
    levels = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    rows_read = 0
    rows_inserted = 0
    rows_skipped = 0
    care_queue_records = 0
    with open(DATASET, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        check_headers(reader.fieldnames)
        with get_connection() as connection:
            with connection.cursor() as cursor:

                for row in reader:
                    rows_read += 1
                    encounter = clean_row(row)
                    risk = calculate_risk(encounter)
                    levels[risk["risk_level"]] += 1
                    if insert_encounter(cursor, encounter, risk): rows_inserted += 1
                    else: rows_skipped += 1
                    if risk["risk_level"] in ("MEDIUM", "HIGH"):
                        create_intervention(cursor, encounter["encounter_id"])
                care_queue_records = count_care_queue(cursor)
    print(f"Rows read: {rows_read}")
    print(f"Rows inserted: {rows_inserted}")
    print(f"Rows skipped: {rows_skipped}")
    print(f"Care queue records: {care_queue_records}")
    print(f"LOW: {levels['LOW']}")
    print(f"MEDIUM: {levels['MEDIUM']}")
    print(f"HIGH: {levels['HIGH']}")  

main()
            