

def to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


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


def calculate_risk(encounter):
    score = 0
    reason = []

    if encounter["number_inpatient"] >= 3:
        score += 3
        reason.append("3+ prior inpatient visits")
    if encounter["number_emergency"] >= 2:
        score += 2
        reason.append("2+ prior emergency visits")
    if encounter["number_outpatient"] >= 3:
        score += 1
        reason.append("3+ prior outpatient visits")
    if encounter["time_in_hospital"] >= 7:
        score += 1
        reason.append("7+ days in hospital")
    if encounter["num_medications"] >= 20:
        score += 1
        reason.append("20+ medications")
    if score >= 5: level = "HIGH"
    elif score >= 3: level = "MEDIUM"
    else: level = "LOW"
    
    review_reason = "; ".join(reason) if reason else "No prototype risk rule triggered"
    return {"risk_score": score, "risk_level": level, "review_reason": review_reason}

def make_encounter(**changes):
    encounter = {
        "number_inpatient": 0, "number_emergency": 0, "number_outpatient": 0, "time_in_hospital": 0, "num_medications": "0-10"
    }
    encounter.update(changes)
    return encounter

def test_low():
    result = calculate_risk(make_encounter())
    assert result["risk_score"] == 0 and result["risk_level"] == "LOW"

def test_medium():
    result = calculate_risk(make_encounter(number_inpatient=3))
    assert result["risk_score"] == 3 and result["risk_level"] == "MEDIUM"

def test_high():
    result = calculate_risk(make_encounter(number_inpatient=3, number_emergency=2))
    assert result["risk_score"] == 5 and result["risk_level"] == "HIGH"