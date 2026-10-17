

def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def clean_row(row):
    return {
        "encounter_id": to_int(row["encounter_id"]),
        "patient_nbr": to_int(row["patient_nbr"]),
        "age": row["age"],
        "time_in_hospital": to_int(row["time_in_hospital"]),
        "number_inpatient": to_int(row["number_inpatient"]),
        "number_emergency": to_int(row["number_emergency"]),
        "number_outpatient": to_int(row["number_outpatient"]),
        "num_medications": to_int(row["num_medications"]),
        "num_lab_procedures": to_int(row["num_lab_procedures"]),
        "num_procedures": to_int(row["num_procedures"]),
        "admission_type_id": to_int(row["admission_type_id"]),
        "discharge_disposition_id": to_int(row["discharge_disposition_id"]),
        "readmitted": row.get("readmitted", "")
    }

if __name__ == "__main__":
    import csv
    from pathlib import Path
    with open(Path(__file__).parent / "diabetic_data.csv", "r", encoding="utf-8-sig") as file:
        first_row = next(csv.DictReader(file))
    print(clean_row(first_row))