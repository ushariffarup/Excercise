"""Load the diabetes CSV into PostgreSQL, scoring each encounter and queueing MEDIUM/HIGH ones. Safe to rerun."""
import csv
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import repository, service
from app.config import get_dataset_path
from app.database import get_connection
from app.errors import AppError
BATCH_SIZE = 2000

def read_batches(path: Path):
    """Yield lists of parsed rows; validates the header first."""
    with open(path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        service.validate_columns(reader.fieldnames)
        batch = []
        for line_number, row in enumerate(reader, start=2):
            batch.append(service.parse_encounter_row(row, line_number))
            if len(batch) == BATCH_SIZE: yield batch; batch = []
        if batch: yield batch

def import_dataset(path: Path) -> None:
    if not path.exists(): raise AppError(f"Dataset not found at {path}. Set DATASET_PATH in .env.")
    levels, rows_read = Counter(), 0
    with get_connection() as conn:
        encounters_before, queue_before = repository.count_rows(conn, "patient_encounters"), repository.count_rows(conn, "care_interventions")
        for batch in read_batches(path):
            repository.upsert_encounters(conn, batch)
            repository.create_interventions(conn, [row["encounter_id"] for row in batch if row["risk_level"] != "LOW"])
            rows_read += len(batch)
            levels.update(row["risk_level"] for row in batch)
        encounters_after, queue_after = repository.count_rows(conn, "patient_encounters"), repository.count_rows(conn, "care_interventions")
    inserted = encounters_after - encounters_before
    print(f"Import completed\n\nRows read:                 {rows_read}\nRows inserted:             {inserted}\nRows updated/skipped:      {rows_read - inserted}")
    print(f"LOW risk:                  {levels['LOW']}\nMEDIUM risk:               {levels['MEDIUM']}\nHIGH risk:                 {levels['HIGH']}")
    print(f"New care queue records:    {queue_after - queue_before}\nCare queue records (total): {queue_after}")

if __name__ == "__main__":
    try: import_dataset(get_dataset_path())
    except AppError as exc: sys.exit(f"Import failed: {exc}")
