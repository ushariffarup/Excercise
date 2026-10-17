from database import get_connection

with get_connection() as connection:
    print("Database connection: OK")

    total = connection.execute(
        "SELECT COUNT(*) AS total FROM patient_encounters"
    ).fetchone()["total"]
    print(f"Encounter rows: {total}")

    levels = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for row in connection.execute(
        "SELECT risk_level, COUNT(*) AS total "
        "FROM patient_encounters GROUP BY risk_level"
    ):
        levels[row["risk_level"]] = row["total"]

    for level, count in levels.items():
        print(f"{level}: {count}")

    queue = connection.execute(
        "SELECT COUNT(*) AS total FROM care_interventions"
    ).fetchone()["total"]
    print(f"Care queue rows: {queue}")

    # Sanity check: the queue should hold exactly the MEDIUM + HIGH encounters.
    if total == 0:
        print("WARNING: no encounters found. STOP - run step 06 before starting FastAPI.")
    elif queue != levels["MEDIUM"] + levels["HIGH"]:
        print("WARNING: care queue rows do not match MEDIUM + HIGH encounters.")
    else:
        print("Looks consistent. Safe to continue to FastAPI.")