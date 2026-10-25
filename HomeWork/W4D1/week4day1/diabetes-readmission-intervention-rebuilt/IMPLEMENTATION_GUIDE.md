# Implementation Guide: Patient Search, High-Care List and Status Tracking

Phase-by-phase guide for adding the reference frontend (`DiabeticProject-main` / `fde-react-check`) to **your** project `diabetes-readmission-intervention`, cross-checked against your home assignment and the original mini-project brief.

> **Supersedes** `FRONTEND_INTEGRATION_PROMPT.md`. That file described the work; this one contains the exact, tested code. Two items in it were incomplete (see section 2, findings 5 and 8).

## How to verify this guide was checked (read this once)

Every change below was applied to a scratch copy of your project and run, not just written:

| What I ran | Result |
|---|---|
| Your schema + importer on PostgreSQL 16 with your `diabetic_data.csv` | 16,997 encounters, 990 queue rows (matches your README numbers) |
| New SQL migration: run twice, plus importer re-run | idempotent; history stays at 990 rows; trigger logs updates |
| Phase 1 Swagger checklist, via FastAPI against the real database | all 30+ checks pass (listed in Phase 1) |
| `pytest` | **28 passed** (your 12 existing + 16 new) |
| `npm run fetch-apis` and `npm run encounter` against the live API | every call succeeded, no `undefined` fields |
| `tsc --noEmit` and `eslint` on the frontend | clean |
| Both HTML screens loaded from the Vite dev server in a simulated browser (jsdom) against the live API | **34 of 34 checks pass** (search, link rule, count badge, update, clear notes, 404 paths) |

**Not verified:** a real browser (Chrome/Edge) and the visual layout (for example the new "Status Tracking" header link), your Windows setup, and your exact PostgreSQL version. Check the layout yourself in Phase 3.

---

## 0. How to use this file

1. Do **one phase at a time**. Each phase ends with a checklist and a **STOP**. Run the checks, read the code, then move on. This is what your assignment asks for ("do one at a time and test it properly, read the generated code").
2. You can follow it by hand, or give it to Claude Code / Cursor / Copilot with this instruction:
   > Implement **Phase N only** from `IMPLEMENTATION_GUIDE.md`. Apply the diffs exactly. Explain each file in 2-3 lines. Run the phase's verification, show me the output, then stop and wait for me to say "continue".
3. Changes to existing files are **unified diffs against the files in your zip**. New files are given in full. If a diff does not apply cleanly, make the same change by hand; do not force it.
4. Commands are written for Windows PowerShell, like your `Commands file.txt`. Run Python commands from the project root.
5. Never commit `.env` or `data/Commands file.txt` (it holds a MongoDB credential). Rotate that password.

---

## 1. Cross-check against your assignment

| # | Assignment item | Where it is covered | Status |
|---|---|---|---|
| 1 | **Last week's homework, 8+ APIs** | Your backend already has all 8 mandatory endpoints from the brief (section 9) plus `/health`: `/encounters`, `/encounters/{id}`, `/care-queue`, `/care-queue/high`, `PATCH /interventions/{id}`, `/operations/summary`, `/operations/readmission-analysis`, `/management/dashboard`. This work adds 3 more: **12 total**. | Met |
| 1b | Brief's example summary includes `completed_interventions` | Added to `/operations/summary` (same value as `closed_interventions`; purely additive) | Added in Phase 1 |
| 2 | **Individual API in TypeScript: interface, call, print** | `fetchApis.ts`: 12 typed functions, one interface per response, a demo that prints each. Interfaces are shaped by what the UI shows (mapping table in Phase 2) | Phase 2 |
| 3a-i | Python for patient search: `main.py`, `service.py`, `repository.py`, `models.py` | `GET /patients/search` in all four files | Phase 1 |
| 3a-ii | Test with Swagger after starting uvicorn | Swagger checklist with expected results | Phase 1 |
| 3a-iii | TypeScript function to call the API and confirm | `searchPatients()` + demo output | Phase 2 |
| 3a-iv | UI for the search, call the GET API, list | `searchPatient.html` / `.js` | Phase 3 |
| 3b | Search high-care patients, list them, **link the encounter id**, **fetch the intervention status** | "High Risk" quick filter lists HIGH encounters; each queued Encounter ID links to the Status screen, which calls `GET /interventions/{id}` | Phases 3 and 4 |
| 3c | Update screen to update the status (status tracking) | `intervention.html` / `.js`, `PATCH /interventions/{id}`, history table | Phase 4 |
| - | Brief acceptance criteria (parameterized SQL, layering, useful 404s, persistence) | New code follows your layering; all SQL uses `%s` parameters; 404 messages reuse your wording | Preserved |

---

## 2. What the cross-check found (and how this guide handles it)

| # | Finding | Handling |
|---|---|---|
| 1 | The reference frontend was built for a **different backend** (`GET /` health, `min_risk_score`, `risk_groups[]`, `completed_interventions`, `care_queue_size` ...). Your backend's contract is different. | Backend contract wins. The TypeScript interfaces are rewritten to your real response shapes. |
| 2 | Three endpoints the frontend calls do not exist in your backend: `/patients/search`, `GET /interventions/{id}`, `GET /interventions/{id}/history`. No CORS either. | Built in Phase 1. |
| 3 | The reference's test data (`patient 84002391`, "Score = 8") **does not exist in your dataset** (highest score is 7). Those quick-test buttons would return nothing. | Replaced with real values (Appendix A). |
| 4 | The reference links **every** encounter to the status screen and its PATCH creates an intervention for LOW encounters. Your rule is that only MEDIUM/HIGH are queued (PATCH on LOW returns 404). | Your rule is kept. Only queued encounters are links; LOW rows show "Not queued". |
| 5 | **(Missed in the earlier prompt)** `repository.count_rows` only accepts two table names, so `verify_setup.py` would crash on the new history table. | Whitelist updated (in the repository diff). |
| 6 | `sql/03_reset.sql` **fails** once the history table exists (foreign key). I confirmed the error. | Reset script updated. |
| 7 | The reference sends `null` for empty fields, and your PATCH treats `null` as "leave unchanged", so a note or assignee could never be cleared. | The form sends the trimmed text, so an empty string clears. Verified in Phase 4. |
| 8 | **(Missed in the earlier prompt)** The reference sends the PATCH to whatever is typed in the Encounter Id box, not the encounter that is loaded. Edit the box and press Update, and a *different* encounter than the one shown gets changed. | The update always targets the loaded encounter and refuses if the box was edited. |
| 9 | The results badge says "50 Records" even when 50 is just the page limit. | Shows "50+ Records (showing first 50)" when capped. |
| 10 | The reference declares `CareQueueItem extends Encounter`, but your queue rows only return a subset of columns. | Own interface in `fetchApis.ts`. |
| 11 | Error text told users to run `backend.app.main:app`. Yours is `app.main:app`. | Fixed. |
| 12 | A failed fetch (for example a LOW encounter) left the previous encounter's data on screen. | Form, badges and history are cleared on failure; Update is disabled until something is loaded. |

---

## Phase 1: Backend (assignment 3a-i and 3a-ii)

**Goal:** three new endpoints, an audit-history table, CORS, and a richer PATCH response. Do the steps in order and read each one.

### 1.1 Create `sql/04_create_intervention_history.sql` (new file)

Idempotent: safe on your already-populated database and safe to re-run. The trigger records every insert/update of an intervention. The backfill creates one history row per existing intervention, only when the history table is empty.

```sql
-- Audit trail for care interventions (run after 01 and 02; safe to re-run).
CREATE TABLE IF NOT EXISTS care_intervention_history (
    history_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    encounter_id BIGINT NOT NULL REFERENCES patient_encounters (encounter_id) ON DELETE CASCADE,
    intervention_id BIGINT REFERENCES care_interventions (intervention_id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL,
    assigned_to VARCHAR(100),
    notes TEXT,
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_history_encounter_changed
    ON care_intervention_history (encounter_id, changed_at DESC);

CREATE OR REPLACE FUNCTION log_care_intervention_history()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO care_intervention_history (encounter_id, intervention_id, status, assigned_to, notes, changed_at)
    VALUES (NEW.encounter_id, NEW.intervention_id, NEW.status, NEW.assigned_to, NEW.notes, CURRENT_TIMESTAMP);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS care_interventions_audit_trail ON care_interventions;
CREATE TRIGGER care_interventions_audit_trail
AFTER INSERT OR UPDATE ON care_interventions
FOR EACH ROW EXECUTE FUNCTION log_care_intervention_history();

-- Backfill one row per existing intervention, only when the history table is empty (re-run safe).
INSERT INTO care_intervention_history (encounter_id, intervention_id, status, assigned_to, notes, changed_at)
SELECT encounter_id, intervention_id, status, assigned_to, notes, COALESCE(updated_at, created_at)
FROM care_interventions
WHERE NOT EXISTS (SELECT 1 FROM care_intervention_history);
```

Run it yourself:

```powershell
psql -U fde_user -d fde_db -f sql/04_create_intervention_history.sql
```

Re-running the importer later does **not** add history noise: `ON CONFLICT DO NOTHING` inserts no row, so the trigger does not fire.

### 1.2 `sql/03_reset.sql` (edit)

Without this, the reset fails with a foreign-key error.

```diff
--- a/sql/03_reset.sql
+++ b/sql/03_reset.sql
@@ -1,2 +1,2 @@
--- Clears imported data (keeps tables and the status lookup). Both tables in one statement respects the foreign key.
-TRUNCATE TABLE care_interventions, patient_encounters RESTART IDENTITY;
+-- Clears imported data (keeps tables and the status lookup). All tables in one statement respects the foreign keys.
+TRUNCATE TABLE care_intervention_history, care_interventions, patient_encounters RESTART IDENTITY;
```

### 1.3 `app/errors.py` and `app/config.py` (edit)

A new 400-type error, and the allowed browser origins. The defaults cover Vite (5173) and React (3000), so **no `.env` change is needed**. Set `CORS_ORIGINS` in `.env` only if you use another port.

```diff
--- a/app/errors.py
+++ b/app/errors.py
@@ -8,3 +8,5 @@
 class NotFoundError(AppError): pass
 
 class ImportDataError(AppError): pass
+
+class InvalidInputError(AppError): pass
```

```diff
--- a/app/config.py
+++ b/app/config.py
@@ -16,3 +16,9 @@
 
 APP_NAME = os.getenv("APP_NAME", "Diabetes Readmission Intervention Queue")
 APP_ENV = os.getenv("APP_ENV", "local")
+
+DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
+
+def get_cors_origins() -> list:
+    """Comma-separated list from CORS_ORIGINS; defaults to the local Vite/React dev servers."""
+    return [origin.strip() for origin in os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",") if origin.strip()]
```

### 1.4 `app/models.py` (edit)

Adds `PatientSearchResult`, `Intervention`, `InterventionHistoryItem`, and `completed_interventions` on the summary.

```diff
--- a/app/models.py
+++ b/app/models.py
@@ -1,3 +1,4 @@
+from datetime import datetime
 from enum import Enum
 from typing import Optional
 from pydantic import BaseModel, Field, model_validator
@@ -42,6 +43,7 @@
     contacted_interventions: int
     follow_up_scheduled: int
     closed_interventions: int
+    completed_interventions: int  # same value as closed_interventions; matches the brief's example shape
 
 class ReadmissionAnalysis(BaseModel):
     overall_encounters: int
@@ -66,3 +68,47 @@
     high_risk_percent: float
     high_risk_30_day_readmissions: int
     care_queue_pending: int
+
+class PatientSearchResult(BaseModel):
+    """One encounter row from /patients/search, with its care intervention (null for LOW risk, which is not queued)."""
+    encounter_id: int
+    patient_nbr: int
+    age: Optional[str] = None
+    time_in_hospital: Optional[int] = None
+    number_inpatient: Optional[int] = None
+    number_emergency: Optional[int] = None
+    number_outpatient: Optional[int] = None
+    num_medications: Optional[int] = None
+    num_lab_procedures: Optional[int] = None
+    discharge_disposition_id: Optional[int] = None
+    admission_type_id: Optional[int] = None
+    readmitted: Optional[str] = None
+    risk_score: int
+    risk_level: RiskLevel
+    review_reason: Optional[str] = None
+    intervention_id: Optional[int] = None
+    status: Optional[InterventionStatus] = None
+    intervention_status: Optional[InterventionStatus] = None  # same value as status (alias kept for the UI)
+    assigned_to: Optional[str] = None
+    notes: Optional[str] = None
+
+class Intervention(BaseModel):
+    intervention_id: int
+    encounter_id: int
+    patient_nbr: int
+    risk_level: RiskLevel
+    risk_score: int
+    status: InterventionStatus
+    assigned_to: Optional[str] = None
+    notes: Optional[str] = None
+    created_at: datetime
+    updated_at: datetime
+
+class InterventionHistoryItem(BaseModel):
+    history_id: int
+    encounter_id: int
+    patient_nbr: int
+    status: InterventionStatus
+    assigned_to: Optional[str] = None
+    notes: Optional[str] = None
+    changed_at: datetime
```

### 1.5 `app/repository.py` (edit)

All SQL stays here, parameterized. `update_intervention` now also returns `patient_nbr`, `risk_level`, `risk_score` (a CTE joined to the encounter) so the UI can refresh its badges from one response. `count_rows` accepts the history table.

```diff
--- a/app/repository.py
+++ b/app/repository.py
@@ -41,14 +41,53 @@
     return _fetch_all(f"{QUEUE_SELECT} {_where(clauses)} {order} LIMIT %s OFFSET %s", (*params, limit, offset))
 
 def update_intervention(encounter_id, status, assigned_to, notes):
-    """Returns the updated row, or None when the encounter has no intervention. Fields left as None are kept unchanged."""
+    """Returns the updated row (with patient_nbr, risk_level, risk_score), or None when the encounter has no intervention. Fields left as None are kept unchanged."""
     return _fetch_one("""
-        UPDATE care_interventions
-        SET status = COALESCE(%s, status), assigned_to = COALESCE(%s, assigned_to), notes = COALESCE(%s, notes), updated_at = CURRENT_TIMESTAMP
-        WHERE encounter_id = %s
-        RETURNING intervention_id, encounter_id, status, assigned_to, notes, created_at, updated_at
+        WITH u AS (
+            UPDATE care_interventions
+            SET status = COALESCE(%s, status), assigned_to = COALESCE(%s, assigned_to), notes = COALESCE(%s, notes), updated_at = CURRENT_TIMESTAMP
+            WHERE encounter_id = %s
+            RETURNING intervention_id, encounter_id, status, assigned_to, notes, created_at, updated_at
+        )
+        SELECT u.intervention_id, u.encounter_id, e.patient_nbr, e.risk_level, e.risk_score, u.status, u.assigned_to, u.notes, u.created_at, u.updated_at
+        FROM u JOIN patient_encounters e ON e.encounter_id = u.encounter_id
     """, (status, assigned_to, notes, encounter_id))
 
+def search_patients(patient_nbr, risk_score, risk_level, limit, offset):
+    """Any combination of filters (AND). LEFT JOIN so LOW-risk encounters (no intervention) are still returned. HIGH first."""
+    clauses, params = [], []
+    if patient_nbr is not None: clauses.append("e.patient_nbr = %s"); params.append(patient_nbr)
+    if risk_score is not None: clauses.append("e.risk_score = %s"); params.append(risk_score)
+    if risk_level: clauses.append("e.risk_level = %s"); params.append(risk_level)
+    order = "ORDER BY CASE e.risk_level WHEN 'HIGH' THEN 0 WHEN 'MEDIUM' THEN 1 ELSE 2 END, e.risk_score DESC, e.encounter_id"
+    return _fetch_all(f"""
+        SELECT e.encounter_id, e.patient_nbr, e.age, e.time_in_hospital, e.number_inpatient, e.number_emergency, e.number_outpatient,
+               e.num_medications, e.num_lab_procedures, e.discharge_disposition_id, e.admission_type_id, e.readmitted,
+               e.risk_score, e.risk_level, e.review_reason,
+               ci.intervention_id, ci.status, ci.status AS intervention_status, ci.assigned_to, ci.notes
+        FROM patient_encounters e
+        LEFT JOIN care_interventions ci ON ci.encounter_id = e.encounter_id
+        {_where(clauses)} {order} LIMIT %s OFFSET %s
+    """, (*params, limit, offset))
+
+def get_intervention(encounter_id):
+    """None when the encounter has no intervention (missing encounter or LOW risk)."""
+    return _fetch_one("""
+        SELECT ci.intervention_id, ci.encounter_id, e.patient_nbr, e.risk_level, e.risk_score,
+               ci.status, ci.assigned_to, ci.notes, ci.created_at, ci.updated_at
+        FROM care_interventions ci JOIN patient_encounters e ON e.encounter_id = ci.encounter_id
+        WHERE ci.encounter_id = %s
+    """, (encounter_id,))
+
+def get_intervention_history(encounter_id):
+    """Audit trail, newest first."""
+    return _fetch_all("""
+        SELECT h.history_id, h.encounter_id, e.patient_nbr, h.status, h.assigned_to, h.notes, h.changed_at
+        FROM care_intervention_history h JOIN patient_encounters e ON e.encounter_id = h.encounter_id
+        WHERE h.encounter_id = %s
+        ORDER BY h.changed_at DESC, h.history_id DESC
+    """, (encounter_id,))
+
 def get_risk_counts():
     return _fetch_one("""
         SELECT COUNT(*) AS total_encounters,
@@ -74,7 +113,7 @@
 # --- importer / setup helpers (take an open connection so the whole import is one transaction) ---
 def count_rows(conn, table):
     """`table` must be one of the project's own tables, never user input."""
-    if table not in ("patient_encounters", "care_interventions"): raise ValueError(f"Unknown table: {table}")
+    if table not in ("patient_encounters", "care_interventions", "care_intervention_history"): raise ValueError(f"Unknown table: {table}")
     return conn.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"]
 
 def upsert_encounters(conn, rows):
```

### 1.6 `app/service.py` (edit)

Validation and normalization, no SQL and no HTTP. Also fills `completed_interventions`.

```diff
--- a/app/service.py
+++ b/app/service.py
@@ -2,7 +2,7 @@
 
 EDUCATIONAL PROTOTYPE: the scoring weights are learning assumptions, not clinically validated rules.
 """
-from app.errors import ImportDataError
+from app.errors import ImportDataError, InvalidInputError
 REQUIRED_COLUMNS = ("encounter_id", "patient_nbr", "age", "time_in_hospital", "number_inpatient", "number_emergency", "number_outpatient", "num_medications", "num_lab_procedures", "num_procedures", "admission_type_id", "discharge_disposition_id", "readmitted")
 INT_COLUMNS = ("encounter_id", "patient_nbr", "time_in_hospital", "number_inpatient", "number_emergency", "number_outpatient", "num_medications", "num_lab_procedures", "num_procedures", "admission_type_id", "discharge_disposition_id")
 NULL_LIKE = {"", "?", "NULL", "NA", "N/A", "NAN"}
@@ -58,7 +58,7 @@
     return {
         "total_encounters": counts["total_encounters"], "high_risk": counts["high_risk"], "medium_risk": counts["medium_risk"], "low_risk": counts["low_risk"],
         "pending_interventions": by_status.get("PENDING_REVIEW", 0), "assigned_interventions": by_status.get("ASSIGNED", 0), "contacted_interventions": by_status.get("CONTACTED", 0),
-        "follow_up_scheduled": by_status.get("FOLLOW_UP_SCHEDULED", 0), "closed_interventions": by_status.get("CLOSED", 0),
+        "follow_up_scheduled": by_status.get("FOLLOW_UP_SCHEDULED", 0), "closed_interventions": by_status.get("CLOSED", 0), "completed_interventions": by_status.get("CLOSED", 0),
     }
 
 def _group_totals(group_rows: list) -> dict:
@@ -89,3 +89,14 @@
         "total_diabetes_encounters": all_count, "readmitted_under_30_days": all_readmitted, "readmission_rate": percentage(all_readmitted, all_count),
         "high_risk_population": high_count, "high_risk_percent": percentage(high_count, all_count), "high_risk_30_day_readmissions": high_readmitted, "care_queue_pending": pending,
     }
+
+VALID_RISK_LEVELS = ("LOW", "MEDIUM", "HIGH")
+MAX_RISK_SCORE = sum(points for _, _, points, _ in RISK_RULES)  # 8 = every rule triggered
+
+def normalize_search(patient_nbr=None, risk_score=None, risk_level=None, limit=50, offset=0) -> dict:
+    """Validate and normalize patient-search filters. No SQL and no HTTP here; raises InvalidInputError."""
+    if patient_nbr is not None and patient_nbr <= 0: raise InvalidInputError("Patient Number must be a positive integer.")
+    if risk_score is not None and not 0 <= risk_score <= MAX_RISK_SCORE: raise InvalidInputError(f"Risk score must be between 0 and {MAX_RISK_SCORE}.")
+    level = risk_level.strip().upper() if risk_level else None
+    if level is not None and level not in VALID_RISK_LEVELS: raise InvalidInputError(f"Invalid risk_level '{risk_level}'. Allowed: {', '.join(VALID_RISK_LEVELS)}.")
+    return {"patient_nbr": patient_nbr, "risk_score": risk_score, "risk_level": level, "limit": max(1, min(limit, 500)), "offset": max(0, offset)}
```

### 1.7 `app/main.py` (edit)

Routes and status codes only. Adds CORS (no credentials, no `*` origin), the 400 handler, the three routes, and `response_model=Intervention` on PATCH.

```diff
--- a/app/main.py
+++ b/app/main.py
@@ -1,17 +1,23 @@
 from typing import Optional
 from fastapi import FastAPI, Query
+from fastapi.middleware.cors import CORSMiddleware
 from fastapi.responses import JSONResponse
 from app import repository, service
-from app.config import APP_NAME
-from app.errors import ConfigurationError, DatabaseUnavailableError, NotFoundError
-from app.models import HealthResponse, InterventionStatus, InterventionUpdate, ManagementDashboard, OperationsSummary, Readmitted, ReadmissionAnalysis, RiskLevel
+from app.config import APP_NAME, get_cors_origins
+from app.errors import ConfigurationError, DatabaseUnavailableError, InvalidInputError, NotFoundError
+from app.models import HealthResponse, Intervention, InterventionHistoryItem, InterventionStatus, InterventionUpdate, ManagementDashboard, OperationsSummary, PatientSearchResult, Readmitted, ReadmissionAnalysis, RiskLevel
 app = FastAPI(title=APP_NAME, description="EDUCATIONAL PROTOTYPE - not clinically validated and not for patient-care decisions. Risk rules are illustrative; the historical `readmitted` outcome is never used for scoring.")
+# Browser frontends (Vite dev server etc.) run on another origin, so they need CORS. Origins come from CORS_ORIGINS in .env.
+app.add_middleware(CORSMiddleware, allow_origins=get_cors_origins(), allow_methods=["*"], allow_headers=["*"])
 LIMIT = Query(50, ge=1, le=500, description="Page size")
 OFFSET = Query(0, ge=0, description="Rows to skip")
 
 @app.exception_handler(NotFoundError)
 def handle_not_found(request, exc): return JSONResponse(status_code=404, content={"detail": str(exc)})
 
+@app.exception_handler(InvalidInputError)
+def handle_invalid_input(request, exc): return JSONResponse(status_code=400, content={"detail": str(exc)})
+
 @app.exception_handler(DatabaseUnavailableError)
 def handle_database_unavailable(request, exc): return JSONResponse(status_code=503, content={"detail": "Database is unavailable. Try again later."})
 
@@ -41,7 +47,7 @@
 def get_high_risk_queue(status: Optional[InterventionStatus] = None, assigned_to: Optional[str] = None, limit: int = LIMIT, offset: int = OFFSET):
     return repository.list_care_queue("HIGH", _value(status), assigned_to, limit, offset)
 
-@app.patch("/interventions/{encounter_id}", summary="Update care intervention")
+@app.patch("/interventions/{encounter_id}", response_model=Intervention, summary="Update care intervention")
 def update_intervention(encounter_id: int, payload: InterventionUpdate):
     updated = repository.update_intervention(encounter_id, _value(payload.status), payload.assigned_to, payload.notes)
     if updated is None:
@@ -49,6 +55,25 @@
         raise NotFoundError(f"Encounter {encounter_id} has no care intervention (only MEDIUM/HIGH risk encounters are queued)")
     return updated
 
+@app.get("/patients/search", response_model=list[PatientSearchResult], summary="Search patients by patient number, risk score and/or risk level")
+def search_patients(patient_nbr: Optional[int] = Query(None, description="Patient number (patient_nbr)"), risk_score: Optional[int] = Query(None, ge=0, le=8, description="Exact risk score, 0-8"), risk_level: Optional[RiskLevel] = None, limit: int = LIMIT, offset: int = OFFSET):
+    """Any combination of filters (AND). Results are HIGH first. Each row includes its care intervention status (null for LOW risk, which is not queued)."""
+    filters = service.normalize_search(patient_nbr, risk_score, _value(risk_level), limit, offset)
+    return repository.search_patients(**filters)
+
+@app.get("/interventions/{encounter_id}", response_model=Intervention, summary="Get the care intervention (status) for one encounter")
+def get_intervention(encounter_id: int):
+    intervention = repository.get_intervention(encounter_id)
+    if intervention is None:
+        if repository.get_encounter(encounter_id) is None: raise NotFoundError(f"Encounter {encounter_id} not found")
+        raise NotFoundError(f"Encounter {encounter_id} has no care intervention (only MEDIUM/HIGH risk encounters are queued)")
+    return intervention
+
+@app.get("/interventions/{encounter_id}/history", response_model=list[InterventionHistoryItem], summary="Audit history of status changes for one encounter, newest first")
+def get_intervention_history(encounter_id: int):
+    if repository.get_encounter(encounter_id) is None: raise NotFoundError(f"Encounter {encounter_id} not found")
+    return repository.get_intervention_history(encounter_id)
+
 @app.get("/operations/summary", response_model=OperationsSummary, summary="Operational queue and workload metrics")
 def operations_summary(): return service.build_operations_summary(repository.get_risk_counts(), repository.get_status_counts())
 
```

### 1.8 `scripts/verify_setup.py` (edit)

Checks the new table too, and prints its row count.

```diff
--- a/scripts/verify_setup.py
+++ b/scripts/verify_setup.py
@@ -12,10 +12,10 @@
     print("DATABASE_URL: OK")
     with get_connection() as conn:
         print("Database connection: OK")
-        missing = [table for table in ("patient_encounters", "care_interventions") if not repository.table_exists(conn, table)]
-        for table in ("patient_encounters", "care_interventions"): print(f"{table} table: {'MISSING' if table in missing else 'OK'}")
-        if missing: sys.exit("\nSetup incomplete: run sql/01_create_schema.sql and sql/02_seed_intervention_statuses.sql")
-        print(f"Encounter rows: {repository.count_rows(conn, 'patient_encounters')}\nCare queue rows: {repository.count_rows(conn, 'care_interventions')}")
+        missing = [table for table in ("patient_encounters", "care_interventions", "care_intervention_history") if not repository.table_exists(conn, table)]
+        for table in ("patient_encounters", "care_interventions", "care_intervention_history"): print(f"{table} table: {'MISSING' if table in missing else 'OK'}")
+        if missing: sys.exit("\nSetup incomplete: run sql/01_create_schema.sql, sql/02_seed_intervention_statuses.sql and sql/04_create_intervention_history.sql")
+        print(f"Encounter rows: {repository.count_rows(conn, 'patient_encounters')}\nCare queue rows: {repository.count_rows(conn, 'care_interventions')}\nHistory rows: {repository.count_rows(conn, 'care_intervention_history')}")
     print("\nSetup verification successful.")
 
 if __name__ == "__main__":
```

### 1.9 `tests/test_patient_search.py` (new file)

Database-free, in the same style as your existing tests.

```python
import pytest
from fastapi.testclient import TestClient
from app import repository
from app.errors import InvalidInputError
from app.main import app
from app.service import build_operations_summary, normalize_search

client = TestClient(app)

# ---- service: validation and normalization (no database) ----
def test_normalize_defaults():
    assert normalize_search() == {"patient_nbr": None, "risk_score": None, "risk_level": None, "limit": 50, "offset": 0}

def test_normalize_uppercases_level_and_clamps_paging():
    result = normalize_search(risk_level=" high ", limit=9999, offset=-5)
    assert (result["risk_level"], result["limit"], result["offset"]) == ("HIGH", 500, 0)

@pytest.mark.parametrize("kwargs", [{"patient_nbr": 0}, {"patient_nbr": -4}, {"risk_score": 9}, {"risk_score": -1}, {"risk_level": "EXTREME"}])
def test_normalize_rejects_bad_input(kwargs):
    with pytest.raises(InvalidInputError): normalize_search(**kwargs)

def test_summary_exposes_completed_as_closed():
    summary = build_operations_summary({"total_encounters": 3, "high_risk": 1, "medium_risk": 1, "low_risk": 1}, [{"status": "CLOSED", "count": 2}])
    assert summary["closed_interventions"] == summary["completed_interventions"] == 2

# ---- routes: validation and error mapping (repository is faked, no database) ----
def test_search_rejects_out_of_range_score():
    assert client.get("/patients/search", params={"risk_score": 9}).status_code == 422

def test_search_rejects_unknown_level():
    assert client.get("/patients/search", params={"risk_level": "BAD"}).status_code == 422

def test_search_service_error_is_400():
    assert client.get("/patients/search", params={"patient_nbr": 0}).status_code == 400

def test_search_passes_filters_to_repository(monkeypatch):
    seen = {}
    def fake(**kwargs): seen.update(kwargs); return []
    monkeypatch.setattr(repository, "search_patients", fake)
    response = client.get("/patients/search", params={"patient_nbr": 5, "risk_score": 3, "risk_level": "MEDIUM", "limit": 10, "offset": 20})
    assert response.status_code == 200 and response.json() == []
    assert seen == {"patient_nbr": 5, "risk_score": 3, "risk_level": "MEDIUM", "limit": 10, "offset": 20}

def test_get_intervention_missing_encounter_is_404(monkeypatch):
    monkeypatch.setattr(repository, "get_intervention", lambda encounter_id: None)
    monkeypatch.setattr(repository, "get_encounter", lambda encounter_id: None)
    response = client.get("/interventions/1")
    assert response.status_code == 404 and "not found" in response.json()["detail"]

def test_get_intervention_low_risk_is_404_with_reason(monkeypatch):
    monkeypatch.setattr(repository, "get_intervention", lambda encounter_id: None)
    monkeypatch.setattr(repository, "get_encounter", lambda encounter_id: {"encounter_id": encounter_id})
    response = client.get("/interventions/1")
    assert response.status_code == 404 and "no care intervention" in response.json()["detail"]

def test_history_missing_encounter_is_404(monkeypatch):
    monkeypatch.setattr(repository, "get_encounter", lambda encounter_id: None)
    assert client.get("/interventions/1/history").status_code == 404

def test_cors_allows_vite_origin_only():
    allowed = client.get("/health", headers={"Origin": "http://localhost:5173"})
    blocked = client.get("/health", headers={"Origin": "http://evil.example"})
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert "access-control-allow-origin" not in blocked.headers
```

### Phase 1 verification

```powershell
.\.venv\Scripts\python scripts/verify_setup.py        # all three tables OK; History rows: 990 (right after the migration)
.\.venv\Scripts\python -m pytest                      # 28 passed
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/docs> and run these in Swagger. The expected results are from my run on your dataset.

| # | Request | Expected |
|---|---|---|
| 1 | `GET /patients/search?patient_nbr=115196778` | 200, **4 rows**, order: `33695262` HIGH, `6068238` MEDIUM, `45573132` MEDIUM, `248916` LOW |
| 2 | `GET /patients/search?risk_level=HIGH&limit=5` | 5 rows, all HIGH, each with `status` filled in |
| 3 | `GET /patients/search?risk_score=7` | **3 rows** |
| 4 | `GET /patients/search?risk_score=9` | 422 |
| 5 | `GET /patients/search?patient_nbr=115196778&risk_level=HIGH&risk_score=5` | exactly encounter `33695262` |
| 6 | `GET /patients/search?patient_nbr=115196778&risk_level=MEDIUM` | 2 rows |
| 7 | `GET /patients/search?risk_level=BAD` | 422 |
| 8 | `GET /patients/search?patient_nbr=0` | 400 "Patient Number must be a positive integer." |
| 9 | `GET /patients/search?patient_nbr=1` | 200 `[]` |
| 10 | `GET /patients/search?risk_level=LOW&limit=3` | rows with `intervention_id: null`, `status: null` |
| 11 | `GET /interventions/33695262` | 200: `patient_nbr 115196778`, `risk_level HIGH`, `risk_score 5`, `status PENDING_REVIEW` |
| 12 | `GET /interventions/12522` | 404 "Encounter 12522 has no care intervention (only MEDIUM/HIGH risk encounters are queued)" |
| 13 | `GET /interventions/999` | 404 "Encounter 999 not found" |
| 14 | `PATCH /interventions/33695262` `{"status":"CONTACTED","assigned_to":"Care Team A","notes":"Called patient"}` | 200 including `patient_nbr` and `risk_level` |
| 15 | `PATCH /interventions/12522` `{"status":"CONTACTED"}` | 404 (LOW is not queued) |
| 16 | `PATCH /interventions/33695262` `{}` | 422 |
| 17 | `PATCH /interventions/33695262` `{"notes":""}` | 200; notes become `""`, status and assignee unchanged |
| 18 | `GET /interventions/33695262/history` | newest first: `CONTACTED` (notes `""`), `CONTACTED` ("Called patient"), `PENDING_REVIEW` |
| 19 | `GET /interventions/12522/history` | 200 `[]` |
| 20 | `GET /interventions/999/history` | 404 |
| 21 | `GET /operations/summary` | includes `completed_interventions` (equals `closed_interventions`); your other 8 routes behave as before |
| 22 | `curl.exe -i -H "Origin: http://localhost:5173" http://127.0.0.1:8000/health` | header `access-control-allow-origin: http://localhost:5173` |
| 23 | same with `-H "Origin: http://evil.example"` | no `access-control-allow-origin` header |

Your database now holds a few test updates for `33695262`. That is fine; the history table is meant to show them. To start clean: `psql -U fde_user -d fde_db -f sql/03_reset.sql`, then re-run the importer.

**STOP. Do not start Phase 2 until all of the above is green.**

---

## Phase 2: Frontend project and TypeScript client (assignment 2 and 3a-iii)

### 2.1 Bring the frontend in

1. Copy the reference folder `DiabeticProject-main/fde-react-check` to `frontend/` inside your project. Leave out `node_modules` if present. Keep `package.json`, `package-lock.json`, `tsconfig*.json`, `vite.config.ts`, `eslint.config.js`, `index.html`, `public/` and `src/`.
2. Leave the Vite template files alone (`src/App.tsx`, `src/main.tsx`, `src/App.css`, `src/assets/`). The real screens are plain HTML/JS/CSS pages in `src/CORS/` that Vite serves. Do **not** convert them to React.
3. Add to your root `.gitignore`:
   ```
   frontend/node_modules/
   frontend/dist/
   frontend/.vite/
   data/Commands file.txt
   ```
4. Install (needs **Node 22.6 or newer**; the npm scripts run `.ts` files directly with `--experimental-strip-types`):
   ```powershell
   cd frontend
   npm install
   ```

### 2.2 Replace `frontend/src/CORS/fetchApis.ts` (full file)

Rewritten to your backend's real shapes. This is assignment item 2 ("interface, call the API, print the response"). The interfaces are driven by what each screen shows:

| Screen element | Interface and fields |
|---|---|
| Search table: Encounter ID, Patient Nbr, Age Group, Hospital Stay, Risk Score/8, Risk Level, Readmitted, Prior Visits (In/ER/Out), Medications, Intervention Status | `PatientSearchResult`: `encounter_id, patient_nbr, age, time_in_hospital, risk_score, risk_level, readmitted, number_inpatient, number_emergency, number_outpatient, num_medications, status, intervention_id` |
| Status form: Encounter Id, Patient Number, Status, Assigned To, Notes, risk and status badges | `Intervention`: `encounter_id, patient_nbr, status, assigned_to, notes, risk_level, risk_score` |
| "List the update here" table | `InterventionHistoryItem`: `changed_at, encounter_id, patient_nbr, status, assigned_to, notes` |
| Update button payload | `InterventionUpdate`: `status, assigned_to, notes` |

```ts
/**
 * TypeScript client for the Diabetes Readmission Intervention Queue API (FastAPI, http://127.0.0.1:8000).
 *
 * Assignment: build an interface for each API (what the UI needs to show), call it, print the response.
 * Run:  npm run fetch-apis      (backend must be running: python -m uvicorn app.main:app --reload)
 *
 * 12 typed API functions:
 *   1 fetchHealth                    GET   /health
 *   2 fetchEncounters                GET   /encounters
 *   3 fetchEncounterById             GET   /encounters/{id}
 *   4 fetchCareQueue                 GET   /care-queue
 *   5 fetchHighRiskCareQueue         GET   /care-queue/high
 *   6 fetchOperationsSummary         GET   /operations/summary
 *   7 fetchReadmissionAnalysis       GET   /operations/readmission-analysis
 *   8 fetchManagementDashboard       GET   /management/dashboard
 *   9 searchPatients                 GET   /patients/search          (Search Patient screen)
 *  10 fetchInterventionByEncounterId GET   /interventions/{id}       (Status screen: fetch status)
 *  11 updateIntervention             PATCH /interventions/{id}       (Status screen: update)
 *  12 fetchInterventionHistory       GET   /interventions/{id}/history (Status screen: list the updates)
 */

// ============================================================================
// 1. TYPE ALIASES
// ============================================================================
export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";

export type InterventionStatus =
    | "PENDING_REVIEW"
    | "ASSIGNED"
    | "CONTACTED"
    | "FOLLOW_UP_SCHEDULED"
    | "CLOSED";

// ============================================================================
// 2. INTERFACES  (shaped by what each UI screen shows)
// ============================================================================

/** GET /health */
export interface HealthCheck {
    status: string;
}

/** GET /encounters row (full patient_encounters row). Nullable columns come from blank CSV values. */
export interface Encounter {
    encounter_id: number;
    patient_nbr: number;
    age: string | null;
    time_in_hospital: number | null;
    number_inpatient: number | null;
    number_emergency: number | null;
    number_outpatient: number | null;
    num_medications: number | null;
    num_lab_procedures: number | null;
    num_procedures: number | null;
    admission_type_id: number | null;
    discharge_disposition_id: number | null;
    readmitted: string | null; // "<30" | ">30" | "NO"
    risk_score: number;
    risk_level: RiskLevel;
    review_reason: string | null;
    created_at: string;
}

/** GET /encounters/{id}: the encounter plus its intervention (all null for LOW risk, which is not queued). */
export interface EncounterDetail extends Encounter {
    intervention_id: number | null;
    intervention_status: InterventionStatus | null;
    assigned_to: string | null;
    intervention_notes: string | null;
    intervention_created_at: string | null;
    intervention_updated_at: string | null;
}

/** GET /care-queue and /care-queue/high row. NOT a full encounter: only the columns the queue returns. */
export interface CareQueueItem {
    encounter_id: number;
    patient_nbr: number;
    age: string | null;
    risk_score: number;
    risk_level: RiskLevel;
    review_reason: string | null;
    intervention_id: number;
    status: InterventionStatus;
    assigned_to: string | null;
    notes: string | null;
    created_at: string;
    updated_at: string;
}

export interface CareQueueParams {
    risk_level?: RiskLevel;
    status?: InterventionStatus;
    assigned_to?: string;
    limit?: number;
    offset?: number;
}

/** Filters for the Search Patient screen: patient id and/or risk score and/or risk level. */
export interface PatientSearchParams {
    patient_nbr?: number;
    risk_score?: number; // 0..8
    risk_level?: RiskLevel;
    limit?: number;
    offset?: number;
}

/** GET /patients/search row: one table row on the Search Patient screen. */
export interface PatientSearchResult {
    encounter_id: number;
    patient_nbr: number;
    age: string | null;
    time_in_hospital: number | null;
    number_inpatient: number | null;
    number_emergency: number | null;
    number_outpatient: number | null;
    num_medications: number | null;
    num_lab_procedures: number | null;
    discharge_disposition_id: number | null;
    admission_type_id: number | null;
    readmitted: string | null;
    risk_score: number;
    risk_level: RiskLevel;
    review_reason: string | null;
    // Intervention columns: null for LOW risk (no intervention exists)
    intervention_id: number | null;
    status: InterventionStatus | null;
    intervention_status: InterventionStatus | null; // same value as status
    assigned_to: string | null;
    notes: string | null;
}

/** GET and PATCH /interventions/{id}: what the Status screen form and badges show. */
export interface Intervention {
    intervention_id: number;
    encounter_id: number;
    patient_nbr: number;
    risk_level: RiskLevel;
    risk_score: number;
    status: InterventionStatus;
    assigned_to: string | null;
    notes: string | null;
    created_at: string;
    updated_at: string;
}

/** PATCH body. Send only what changed; an empty string clears assigned_to / notes. */
export interface InterventionUpdate {
    status?: InterventionStatus;
    assigned_to?: string;
    notes?: string;
}

/** GET /interventions/{id}/history row: one line in the "List the update here" table. */
export interface InterventionHistoryItem {
    history_id: number;
    encounter_id: number;
    patient_nbr: number;
    status: InterventionStatus;
    assigned_to: string | null;
    notes: string | null;
    changed_at: string;
}

/** GET /operations/summary */
export interface OperationsSummary {
    total_encounters: number;
    high_risk: number;
    medium_risk: number;
    low_risk: number;
    pending_interventions: number;
    assigned_interventions: number;
    contacted_interventions: number;
    follow_up_scheduled: number;
    closed_interventions: number;
    completed_interventions: number; // same value as closed_interventions
}

/** GET /operations/readmission-analysis (flat shape: one block of fields per risk group) */
export interface ReadmissionAnalysis {
    overall_encounters: number;
    overall_readmitted_under_30_days: number;
    overall_readmission_rate: number;
    high_risk_patients: number;
    high_risk_readmitted_under_30_days: number;
    high_risk_readmission_rate: number;
    medium_risk_patients: number;
    medium_risk_readmitted_under_30_days: number;
    medium_risk_readmission_rate: number;
    low_risk_patients: number;
    low_risk_readmitted_under_30_days: number;
    low_risk_readmission_rate: number;
    note: string;
}

/** GET /management/dashboard */
export interface ManagementDashboard {
    total_diabetes_encounters: number;
    readmitted_under_30_days: number;
    readmission_rate: number;
    high_risk_population: number;
    high_risk_percent: number;
    high_risk_30_day_readmissions: number;
    care_queue_pending: number;
}

// ============================================================================
// 3. GENERIC FETCH HELPERS
// ============================================================================
export const BASE_URL = "http://127.0.0.1:8000";

/** Build "?a=1&b=2" from the params that are actually set (undefined values are skipped). */
function buildQuery(params: object): string {
    const search = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null && value !== "") search.append(key, String(value));
    }
    const text = search.toString();
    return text ? `?${text}` : "";
}

/** Turn a failed response into an Error carrying the backend's `detail` message (string or validation array). */
async function toApiError(response: Response, url: string): Promise<Error> {
    let detail = response.statusText;
    try {
        const body = await response.json();
        if (body?.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {
        // body was not JSON; keep statusText
    }
    return new Error(`API Error [${response.status}] ${detail} (${url})`);
}

async function apiGet<T>(path: string): Promise<T> {
    const url = `${BASE_URL}${path}`;
    const response = await fetch(url, { headers: { Accept: "application/json" } });
    if (!response.ok) throw await toApiError(response, url);
    return (await response.json()) as T;
}

// ============================================================================
// 4. API FUNCTIONS
// ============================================================================
export const fetchHealth = () => apiGet<HealthCheck>("/health");

export const fetchEncounters = (limit = 3, offset = 0) =>
    apiGet<Encounter[]>(`/encounters${buildQuery({ limit, offset })}`);

export const fetchEncounterById = (id: number) => apiGet<EncounterDetail>(`/encounters/${id}`);

export const fetchCareQueue = (params: CareQueueParams = {}) =>
    apiGet<CareQueueItem[]>(`/care-queue${buildQuery(params)}`);

export const fetchHighRiskCareQueue = (params: Omit<CareQueueParams, "risk_level"> = {}) =>
    apiGet<CareQueueItem[]>(`/care-queue/high${buildQuery(params)}`);

export const fetchOperationsSummary = () => apiGet<OperationsSummary>("/operations/summary");

export const fetchReadmissionAnalysis = () => apiGet<ReadmissionAnalysis>("/operations/readmission-analysis");

export const fetchManagementDashboard = () => apiGet<ManagementDashboard>("/management/dashboard");

/** Search by patient id and/or risk score and/or risk level (any combination). */
export const searchPatients = (params: PatientSearchParams = {}) =>
    apiGet<PatientSearchResult[]>(`/patients/search${buildQuery(params)}`);

/** Fetch the care intervention (status) for one encounter. 404 for LOW risk or unknown encounter. */
export const fetchInterventionByEncounterId = (encounterId: number) =>
    apiGet<Intervention>(`/interventions/${encounterId}`);

export const fetchInterventionHistory = (encounterId: number) =>
    apiGet<InterventionHistoryItem[]>(`/interventions/${encounterId}/history`);

export async function updateIntervention(encounterId: number, data: InterventionUpdate): Promise<Intervention> {
    const url = `${BASE_URL}/interventions/${encounterId}`;
    const response = await fetch(url, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(data),
    });
    if (!response.ok) throw await toApiError(response, url);
    return (await response.json()) as Intervention;
}

// ============================================================================
// 5. DEMO: call each GET API and print the response (does NOT call PATCH, which writes data)
// ============================================================================
async function runDemo() {
    console.log("=== Fetching from the FastAPI backend with TypeScript interfaces ===\n");
    try {
        console.log("1. GET /health");
        console.log(await fetchHealth(), "\n");

        console.log("2. GET /encounters?limit=2");
        const encounters = await fetchEncounters(2);
        console.table(encounters.map((e) => ({ encounter_id: e.encounter_id, patient_nbr: e.patient_nbr, age: e.age, risk_score: e.risk_score, risk_level: e.risk_level, readmitted: e.readmitted })));

        console.log("\n3. GET /encounters/33695262");
        const detail = await fetchEncounterById(33695262);
        console.log(`   Encounter #${detail.encounter_id}: patient ${detail.patient_nbr}, ${detail.risk_level} (${detail.risk_score} pts), intervention: ${detail.intervention_status ?? "none"}`);

        console.log("\n4. GET /care-queue/high?limit=2");
        const high = await fetchHighRiskCareQueue({ limit: 2 });
        console.table(high.map((q) => ({ intervention_id: q.intervention_id, encounter_id: q.encounter_id, risk_level: q.risk_level, status: q.status, assigned_to: q.assigned_to ?? "Unassigned" })));

        console.log("\n5. GET /operations/summary");
        console.log(await fetchOperationsSummary());

        console.log("\n6. GET /operations/readmission-analysis");
        const analysis = await fetchReadmissionAnalysis();
        console.table([
            { group: "HIGH", patients: analysis.high_risk_patients, readmitted_lt_30: analysis.high_risk_readmitted_under_30_days, rate_pct: analysis.high_risk_readmission_rate },
            { group: "MEDIUM", patients: analysis.medium_risk_patients, readmitted_lt_30: analysis.medium_risk_readmitted_under_30_days, rate_pct: analysis.medium_risk_readmission_rate },
            { group: "LOW", patients: analysis.low_risk_patients, readmitted_lt_30: analysis.low_risk_readmitted_under_30_days, rate_pct: analysis.low_risk_readmission_rate },
        ]);

        console.log("\n7. GET /management/dashboard");
        console.log(await fetchManagementDashboard());

        console.log("\n8. GET /patients/search?patient_nbr=115196778");
        const byPatient = await searchPatients({ patient_nbr: 115196778 });
        console.table(byPatient.map((r) => ({ encounter_id: r.encounter_id, risk_score: r.risk_score, risk_level: r.risk_level, status: r.status ?? "Not queued" })));

        console.log("\n9. GET /patients/search?risk_level=HIGH&risk_score=7");
        const combined = await searchPatients({ risk_level: "HIGH", risk_score: 7 });
        console.log(`   ${combined.length} encounter(s) with HIGH risk and score 7`);

        console.log("\n10. GET /interventions/33695262");
        console.log(await fetchInterventionByEncounterId(33695262));

        console.log("\n11. GET /interventions/33695262/history");
        const history = await fetchInterventionHistory(33695262);
        console.table(history.map((h) => ({ changed_at: h.changed_at, status: h.status, assigned_to: h.assigned_to ?? "Unassigned", notes: h.notes ?? "" })));

        console.log("\n12. Error path: GET /interventions/12522 (LOW risk, not queued)");
        try {
            await fetchInterventionByEncounterId(12522);
        } catch (err) {
            console.log("   Expected error ->", (err as Error).message);
        }

        console.log("\nAll GET endpoints responded and matched the TypeScript interfaces.");
    } catch (err) {
        console.error("Error while fetching API data:", err);
    }
}

runDemo();
```

### 2.3 Replace `frontend/src/CORS/encounter.ts` (full file)

Real rows instead of the invented ones, and a LOW encounter correctly has no intervention status.

```ts
/**
 * Small warm-up script: an Encounter interface, a hardcoded array, then two real API calls.
 * Run:  npm run encounter      (backend must be running)
 * Self-contained on purpose: importing fetchApis.ts would also run its demo.
 */
export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";
export type InterventionStatus = "PENDING_REVIEW" | "ASSIGNED" | "CONTACTED" | "FOLLOW_UP_SCHEDULED" | "CLOSED";

export interface Encounter {
    encounter_id: number;
    patient_nbr: number;
    age: string | null;
    time_in_hospital: number | null;
    number_inpatient: number | null;
    number_emergency: number | null;
    number_outpatient: number | null;
    num_medications: number | null;
    num_lab_procedures: number | null;
    num_procedures: number | null;
    admission_type_id: number | null;
    discharge_disposition_id: number | null;
    readmitted: string | null;
    risk_score: number;
    risk_level: RiskLevel;
    review_reason: string | null;
    created_at?: string;
}

/** GET /encounters/{id} adds the intervention columns (null for LOW risk). */
export interface EncounterDetail extends Encounter {
    intervention_id: number | null;
    intervention_status: InterventionStatus | null;
    assigned_to: string | null;
    intervention_notes: string | null;
}

// ============================================================================
// PART 1: Hardcoded encounters (real rows from the dataset)
// A LOW-risk encounter has no care intervention, so it has no intervention status.
// ============================================================================
const encounters: Encounter[] = [
    {
        encounter_id: 12522, patient_nbr: 48330783, age: "[80-90)", time_in_hospital: 13,
        number_inpatient: 0, number_emergency: 0, number_outpatient: 0, num_medications: 28, num_lab_procedures: 68,
        num_procedures: 2, admission_type_id: 2, discharge_disposition_id: 1, readmitted: "NO",
        risk_score: 2, risk_level: "LOW", review_reason: "7+ days in hospital; 20+ medications",
    },
    {
        encounter_id: 33695262, patient_nbr: 115196778, age: "[60-70)", time_in_hospital: 7,
        number_inpatient: 15, number_emergency: 0, number_outpatient: 0, num_medications: 21, num_lab_procedures: 45,
        num_procedures: 4, admission_type_id: 1, discharge_disposition_id: 1, readmitted: "<30",
        risk_score: 5, risk_level: "HIGH", review_reason: "3+ prior inpatient visits; 7+ days in hospital; 20+ medications",
    },
];

console.log("--- Hardcoded Encounters Array ---");
console.log(encounters);

// ============================================================================
// PART 2: Fetching from the backend (http://127.0.0.1:8000)
// ============================================================================
const BASE_URL = "http://127.0.0.1:8000";

async function fetchEncounters(limit = 5): Promise<void> {
    const url = `${BASE_URL}/encounters?limit=${limit}`;
    try {
        console.log(`\nFetching encounters list from: ${url} ...`);
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP Error: ${response.status} - ${response.statusText}`);
        const data: Encounter[] = await response.json();
        console.log(`--- API Response: ${data.length} Encounters fetched (showing 2) ---`);
        console.log(JSON.stringify(data.slice(0, 2), null, 2));
    } catch (error) {
        console.error("Failed to fetch encounters list:", error);
    }
}

async function fetchEncounterById(encounterId: number): Promise<void> {
    const url = `${BASE_URL}/encounters/${encounterId}`;
    try {
        console.log(`\nFetching single encounter from: ${url} ...`);
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP Error: ${response.status} - ${response.statusText}`);
        const data: EncounterDetail = await response.json();
        console.log("--- API Response: Single Encounter ---");
        console.log(JSON.stringify(data, null, 2));
    } catch (error) {
        console.error(`Failed to fetch encounter ${encounterId}:`, error);
    }
}

async function run() {
    await fetchEncounters(5);
    await fetchEncounterById(33695262);
}

run();
```

### Phase 2 verification

With uvicorn running:

```powershell
cd frontend
npm run fetch-apis
npm run encounter
npx tsc -p tsconfig.app.json --noEmit
```

Expected from `npm run fetch-apis` (your numbers will match unless you changed data):

- 12 numbered steps print, no stack trace, no `undefined` in any table.
- Step 6 (readmission analysis): HIGH 168 patients / 54 readmitted `<30` / **32.14%**, MEDIUM 822 / 181 / 22.02%, LOW 16007 / 1666 / 10.41%.
- Step 8: patient `115196778` returns 4 rows; the LOW row shows `Not queued`.
- Step 9: 3 encounters with HIGH risk and score 7.
- Step 12: a printed, **expected** error: `API Error [404] Encounter 12522 has no care intervention ...`.
- `tsc` prints nothing (success).

The demo never calls PATCH, so it does not change your data.

**STOP.**

---

## Phase 3: Search Patient screen and High-care list (assignment 3a-iv and 3b)

Files in `frontend/src/CORS/`. Layout, styling and the full-screen toggle stay as in the reference.

### 3.1 `js/searchPatient.js` (edit)

Health check on `/health`, corrected backend command in the error text, honest count badge, link only for queued encounters, "Not queued" label.

```diff
--- a/frontend/src/CORS/js/searchPatient.js
+++ b/frontend/src/CORS/js/searchPatient.js
@@ -10,7 +10,7 @@
 const CONFIG = {
     BASE_URL: 'http://127.0.0.1:8000',
     SEARCH_ENDPOINT: '/patients/search',
-    HEALTH_ENDPOINT: '/',
+    HEALTH_ENDPOINT: '/health',
     DEFAULT_LIMIT: 50,
 };
 
@@ -131,7 +131,7 @@
         
         let message = error.message;
         if (message.includes('Failed to fetch') || message.includes('NetworkError')) {
-            message = `Unable to connect to FastAPI backend at ${CONFIG.BASE_URL}. Ensure uvicorn is running: "python -m uvicorn backend.app.main:app --reload --port 8000"`;
+            message = `Unable to connect to FastAPI backend at ${CONFIG.BASE_URL}. Ensure uvicorn is running: "python -m uvicorn app.main:app --reload --port 8000"`;
             updateStatusPill(false, 'API Disconnected');
         }
         showError(message);
@@ -149,7 +149,10 @@
  */
 function renderTable(patients) {
     elements.patientsTableBody.innerHTML = '';
-    elements.resultCountBadge.textContent = `${patients.length} Record${patients.length === 1 ? '' : 's'}`;
+    const capped = patients.length >= CONFIG.DEFAULT_LIMIT;
+    elements.resultCountBadge.textContent = capped
+        ? `${CONFIG.DEFAULT_LIMIT}+ Records (showing first ${CONFIG.DEFAULT_LIMIT})`
+        : `${patients.length} Record${patients.length === 1 ? '' : 's'}`;
 
     if (!patients || patients.length === 0) {
         elements.tableContainer.style.display = 'none';
@@ -183,14 +186,7 @@
         const interventionStatus = patient.intervention_status || patient.status || null;
 
         tr.innerHTML = `
-            <td>
-                <a href="intervention.html?encounter_id=${encodeURIComponent(patient.encounter_id)}&patient_nbr=${encodeURIComponent(patient.patient_nbr)}" 
-                   class="encounter-id-link" 
-                   title="Click to view and update care intervention for Encounter #${encounterId}">
-                    <strong>#${encounterId}</strong>
-                    <span class="link-arrow">&rarr;</span>
-                </a>
-            </td>
+            <td>${createEncounterCellHtml(patient)}</td>
             <td><span class="patient-id-badge">${patientNbr}</span></td>
             <td>${age}</td>
             <td>${timeInHospital}</td>
@@ -209,6 +205,22 @@
 }
 
 /**
+ * Encounter ID cell. Only MEDIUM/HIGH encounters have a care intervention, so only those link to the
+ * Status Tracking screen. LOW-risk encounters are not queued and show plain text.
+ */
+function createEncounterCellHtml(patient) {
+    const id = escapeHtml(String(patient.encounter_id ?? '-'));
+    if (patient.intervention_id == null) {
+        return `<span class="encounter-id-plain" title="Not in care queue (LOW risk)"><strong>#${id}</strong></span>`;
+    }
+    const href = `intervention.html?encounter_id=${encodeURIComponent(patient.encounter_id)}&patient_nbr=${encodeURIComponent(patient.patient_nbr)}`;
+    return `<a href="${href}" class="encounter-id-link" title="Click to view and update care intervention for Encounter #${id}">
+        <strong>#${id}</strong>
+        <span class="link-arrow">&rarr;</span>
+    </a>`;
+}
+
+/**
  * HTML Badge for Risk Level
  */
 function createRiskBadgeHtml(level) {
@@ -225,7 +237,7 @@
  */
 function createStatusBadgeHtml(status) {
     if (!status) {
-        return `<span class="status-badge status-none">None</span>`;
+        return `<span class="status-badge status-none">Not queued</span>`;
     }
     const normalized = status.toUpperCase();
     const className = `status-${normalized.toLowerCase()}`;
```

### 3.2 `html/searchPatient.html` (edit)

Quick-test chips use real data (`Patient #115196778`, `Score = 7`; the **High Risk** chip is the High-care list for item 3b). Adds a header link to the Status Tracking screen.

```diff
--- a/frontend/src/CORS/html/searchPatient.html
+++ b/frontend/src/CORS/html/searchPatient.html
@@ -28,10 +28,15 @@
                 <h1 class="app-title">Diabetes Patient Management</h1>
             </div>
 
-            <!-- Backend CORS / API Status Indicator -->
-            <div class="api-status-pill" id="apiStatusPill" title="FastAPI Backend Status">
-                <span class="status-dot" id="statusDot"></span>
-                <span id="statusText">Checking API...</span>
+            <div class="header-right-group">
+                <!-- Navigation to the Status Tracking screen -->
+                <a href="intervention.html" class="btn btn-secondary back-nav-btn">Status Tracking <span class="arrow">&rarr;</span></a>
+
+                <!-- Backend CORS / API Status Indicator -->
+                <div class="api-status-pill" id="apiStatusPill" title="FastAPI Backend Status">
+                    <span class="status-dot" id="statusDot"></span>
+                    <span id="statusText">Checking API...</span>
+                </div>
             </div>
         </div>
     </header>
@@ -65,14 +70,14 @@
                         <div class="form-group">
                             <label for="patientNumber" class="form-label">
                                 Patient Number
-                                <span class="hint">(e.g. 84002391)</span>
+                                <span class="hint">(e.g. 115196778)</span>
                             </label>
                             <input 
                                 type="number" 
                                 id="patientNumber" 
                                 name="patientNumber" 
                                 class="form-control" 
-                                placeholder="Enter patient ID number..." 
+                                placeholder="Enter patient number..." 
                                 min="1"
                                 autocomplete="off"
                             >
@@ -117,9 +122,9 @@
                     <div class="form-actions-row">
                         <div class="quick-filters">
                             <span class="quick-filter-label">Quick Test:</span>
-                            <button type="button" class="chip-btn" data-patient="84002391">Patient #84002391</button>
+                            <button type="button" class="chip-btn" data-patient="115196778">Patient #115196778</button>
                             <button type="button" class="chip-btn" data-level="HIGH">High Risk</button>
-                            <button type="button" class="chip-btn" data-score="8">Score = 8</button>
+                            <button type="button" class="chip-btn" data-score="7">Score = 7</button>
                             <button type="button" class="chip-btn" data-level="ALL">All Risk Levels</button>
                         </div>
 
```

### Phase 3 verification (in the browser)

```powershell
# terminal 1 (project root)
.\.venv\Scripts\python -m uvicorn app.main:app --reload
# terminal 2
cd frontend
npm run dev
```

Open <http://localhost:5173/src/CORS/html/searchPatient.html>. **Use this Vite address, not a double-clicked `file://` page**: CORS only allows the Vite origins.

| # | Action | Expected |
|---|---|---|
| 1 | Page loads | pill says "API Connected (Port 8000)" |
| 2 | Click **Patient #115196778** | 4 rows, the HIGH one (`33695262`) first; badge "4 Records" |
| 3 | In that result, find the LOW row (`248916`) | Encounter ID is plain text (not a link); status "Not queued" |
| 4 | Click **High Risk** | 50 rows, all HIGH, every Encounter ID is a link; badge "50+ Records (showing first 50)" |
| 5 | Click **Score = 7** | 3 rows |
| 6 | Patient `115196778` + Risk Level Medium, Search | 2 rows |
| 7 | Patient number `1`, Search | "No Matching Encounters Found" (no red error banner) |
| 8 | Search with every field empty | validation message, no request sent |
| 9 | Risk Score `9` | "Risk Score must be between 0 and 8." |
| 10 | Stop uvicorn, click Search | red banner: "Unable to connect ... `python -m uvicorn app.main:app --reload --port 8000`". Restart uvicorn |
| 11 | Click an Encounter ID link | opens the Status screen for that encounter (Phase 4) |
| 12 | Look at the header | the "Status Tracking" button and the API pill sit together and are not overlapping (I could not check layout visually) |
| 13 | DevTools console | no errors |

**STOP.**

---

## Phase 4: Status Tracking screen (assignment 3c)

### 4.1 `js/intervention.js` (edit)

No HTML change is required. Changes: health check on `/health`; show the backend's own error text; clear everything when a fetch fails; Update disabled until an encounter is loaded; the update always targets the **loaded** encounter and refuses if the ID box was edited; send the form text as typed so an empty string clears a field; simpler success message.

```diff
--- a/frontend/src/CORS/js/intervention.js
+++ b/frontend/src/CORS/js/intervention.js
@@ -10,7 +10,7 @@
 const CONFIG = {
     BASE_URL: 'http://127.0.0.1:8000',
     INTERVENTIONS_ENDPOINT: '/interventions',
-    HEALTH_ENDPOINT: '/',
+    HEALTH_ENDPOINT: '/health',
 };
 
 const state = {
@@ -112,7 +112,7 @@
                 const errData = await response.json();
                 if (errData.detail) detail = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
             } catch (_) {}
-            throw new Error(`Encounter #${encounterId} fetch error: ${detail}`);
+            throw new Error(detail);
         }
 
         const data = await response.json();
@@ -129,6 +129,7 @@
         updateStatusPill(true, 'API Connected (Port 8000)');
     } catch (error) {
         console.error('Fetch intervention error:', error);
+        clearLoadedState();
         showError(error.message);
     } finally {
         setLoading(false);
@@ -144,23 +145,24 @@
     hideError();
     hideSuccess();
 
-    const encounterIdVal = elements.encounterIdInput.value.trim();
-    if (!encounterIdVal) {
-        showError('Please provide a valid Encounter ID.');
+    if (!state.currentIntervention) {
+        showError('Load an encounter first: enter an Encounter ID and click Fetch Status.');
         elements.encounterIdInput.focus();
         return;
     }
 
-    const encounterId = Number(encounterIdVal);
-    if (isNaN(encounterId) || encounterId <= 0) {
-        showError('Encounter ID must be a positive integer.');
-        elements.encounterIdInput.focus();
+    // Always update the encounter that is actually loaded, never a half-typed ID.
+    const encounterId = state.currentIntervention.encounter_id;
+    if (elements.encounterIdInput.value.trim() !== String(encounterId)) {
+        showError('The Encounter ID was changed. Click Fetch Status to load it before updating.');
         return;
     }
 
     const status = elements.statusSelect.value;
-    const assignedTo = elements.assignedToInput.value.trim() || null;
-    const notes = elements.notesInput.value.trim() || null;
+    // The form is pre-filled from the server, so it is the source of truth.
+    // Send the text as typed: an empty string clears the field (null would leave it unchanged).
+    const assignedTo = elements.assignedToInput.value.trim();
+    const notes = elements.notesInput.value.trim();
 
     setUpdating(true);
 
@@ -203,7 +205,7 @@
         // Fetch fresh audit trail from care_intervention_history table
         await fetchInterventionHistory(encounterId);
 
-        showSuccess(`Care intervention for Encounter #${encounterId} successfully updated and recorded in care_intervention_history table.`);
+        showSuccess(`Intervention for Encounter #${encounterId} updated.`);
 
     } catch (error) {
         console.error('Update error:', error);
@@ -223,6 +225,7 @@
 function populateForm(data) {
     if (!data) return;
 
+    elements.updateBtn.disabled = false;
     elements.encounterIdInput.value = data.encounter_id ?? '';
     if (data.patient_nbr != null) {
         elements.patientNumberInput.value = data.patient_nbr;
@@ -253,6 +256,24 @@
 }
 
 /**
+ * Forget the loaded encounter: clears the form, badges and history so stale data is never shown
+ * (used when a fetch fails, e.g. 404 for a LOW-risk encounter that is not in the care queue).
+ */
+function clearLoadedState() {
+    state.currentIntervention = null;
+    state.patientNbr = null;
+    state.updatesHistory = [];
+    elements.patientNumberInput.value = '';
+    elements.statusSelect.value = 'PENDING_REVIEW';
+    elements.assignedToInput.value = '';
+    elements.notesInput.value = '';
+    elements.encounterRiskBadge.style.display = 'none';
+    elements.encounterStatusBadge.style.display = 'none';
+    elements.updateBtn.disabled = true;
+    renderUpdatesTable();
+}
+
+/**
  * Fetch immutable audit trail directly from PostgreSQL care_intervention_history table
  */
 async function fetchInterventionHistory(encounterId) {
@@ -403,7 +424,7 @@
         elements.updateBtn.disabled = true;
         elements.updateBtn.innerHTML = `Updating...`;
     } else {
-        elements.updateBtn.disabled = false;
+        elements.updateBtn.disabled = !state.currentIntervention;
         elements.updateBtn.innerHTML = `Update <span class="arrow-down">&#9662;</span>`;
     }
 }
@@ -462,7 +483,8 @@
 // 5. Initialization & URL Param Handling
 // -----------------------------------------------------------------------------
 document.addEventListener('DOMContentLoaded', () => {
-    // 1. Health check
+    // 1. Health check; Update stays disabled until an encounter is loaded
+    elements.updateBtn.disabled = true;
     checkApiHealth();
 
     // 2. Parse URL parameters (e.g. ?encounter_id=67162368&patient_nbr=84002391)
```

### Phase 4 verification (in the browser, backend and `npm run dev` running)

Start from the search page, or open <http://localhost:5173/src/CORS/html/intervention.html?encounter_id=33695262&patient_nbr=115196778>.

| # | Action | Expected |
|---|---|---|
| 1 | Arrive from a search-result link for `33695262` | form pre-filled; "HIGH RISK (Score 5)" badge; history table lists earlier entries, newest tagged LATEST |
| 2 | Status `FOLLOW_UP_SCHEDULED`, Assigned To `Care Team A`, Notes `Call back Friday`, click **Update** | "Intervention for Encounter #33695262 updated."; a new top row in the history table; status badge changes |
| 3 | Clear the Notes box, click Update | a new history row with empty notes; reloading the page shows notes still empty (cleared, not "unchanged") |
| 4 | Restart uvicorn, click **Fetch Status** | same data (persisted in PostgreSQL) |
| 5 | Edit the Encounter Id box to `6068238` and click **Update** without Fetch | blocked: "The Encounter ID was changed. Click Fetch Status ...". Encounter `6068238` is untouched |
| 6 | Type `12522`, press Enter | red banner "Encounter 12522 has no care intervention (only MEDIUM/HIGH risk encounters are queued)"; form, badges and history cleared; Update disabled |
| 7 | Type `999`, press Enter | "Encounter 999 not found" |
| 8 | Open `intervention.html` with no parameters | Update is disabled; empty-state message shown |
| 9 | Click Back to Search Patient | your previous search is restored; the status badge shows `FOLLOW UP SCHEDULED` |
| 10 | In psql: `SELECT status, assigned_to, notes, changed_at FROM care_intervention_history WHERE encounter_id = 33695262 ORDER BY history_id;` | rows match what the table shows |
| 11 | DevTools console | no errors (the red 404 logs for steps 6 and 7 are expected) |

**STOP.**

---

## Phase 5: Wrap-up

### 5.1 README

Add a Frontend section, update the API table, and add the new paths.

```markdown
## Frontend

A small Vite project in `frontend/` serves two plain HTML/JS screens (Node 22.6+):

    cd frontend
    npm install
    npm run dev

- Search Patient: http://localhost:5173/src/CORS/html/searchPatient.html
- Status Tracking: http://localhost:5173/src/CORS/html/intervention.html
- API demo in TypeScript: `npm run fetch-apis` (backend must be running)

The backend allows the Vite/React dev origins through CORS (`CORS_ORIGINS` in `.env`, optional).
Open the pages from the Vite address, not from a `file://` path.
```

Add these rows to the **Key APIs** table, and `frontend/` plus `sql/04_create_intervention_history.sql` to the path table:

```markdown
| GET | `/patients/search` | search by `patient_nbr`, `risk_score`, `risk_level` (any combination) |
| GET | `/interventions/{encounter_id}` | one encounter's care intervention (404 for LOW risk) |
| GET | `/interventions/{encounter_id}/history` | audit trail of status changes, newest first |
```

Also change the setup step that lists SQL files to include `sql/04_create_intervention_history.sql`.

### 5.2 Final checks

```powershell
.\.venv\Scripts\python scripts/verify_setup.py
.\.venv\Scripts\python -m pytest                       # 28 passed
cd frontend
npm run fetch-apis
npx tsc -p tsconfig.app.json --noEmit
npm run lint
```

### 5.3 Final summary (fill in for your submission)

| Assignment item | Files | How verified |
|---|---|---|
| 8+ APIs | `app/main.py` (12 routes incl. health) | Swagger `/docs` |
| 2: TypeScript interface, call, print | `frontend/src/CORS/fetchApis.ts`, `encounter.ts` | `npm run fetch-apis` output |
| 3a-i Python search | `main.py`, `service.py`, `repository.py`, `models.py` | code review + `tests/test_patient_search.py` |
| 3a-ii Swagger | `/docs` | Phase 1 table, 23 checks |
| 3a-iii TS function | `searchPatients()` | demo steps 8 and 9 |
| 3a-iv Search UI | `searchPatient.html` / `.js` | Phase 3 table |
| 3b High-care list + link + status | High Risk chip, encounter link, `GET /interventions/{id}` | Phase 3 steps 4, 11 and Phase 4 step 1 |
| 3c Status update UI | `intervention.html` / `.js`, `PATCH`, history | Phase 4 table |

---

## Appendix A: test data (from your dataset)

| Purpose | Value |
|---|---|
| Patient with several encounters (HIGH, MEDIUM, MEDIUM, LOW) | `patient_nbr 115196778` |
| HIGH encounter, readmitted `<30` | `encounter_id 33695262` (score 5) |
| Other HIGH encounters | `5654628`, `7825020`, `7836894` |
| A MEDIUM encounter | `6068238` (score 3) |
| Encounters with the top score, 7 | `29399700` and 2 others |
| LOW encounter (no intervention; expect 404 on the status screen) | `12522` |
| Not in your data (do not use) | patient `84002391`, risk score `8` |

Dataset totals: 16,997 encounters; LOW 16,007, MEDIUM 822, HIGH 168; queue 990.

## Appendix B: troubleshooting

| Symptom | Cause and fix |
|---|---|
| Browser console: "blocked by CORS policy" | The page was opened from `file://` or another port. Use the Vite URL on 5173, or add the origin to `CORS_ORIGINS` in `.env` and restart uvicorn. |
| Pill says "API Offline" | uvicorn is not running on port 8000, or you started it from the wrong folder. Run it from the project root as `app.main:app`. |
| `npm run fetch-apis` fails with `ECONNREFUSED` | Backend not running. |
| `npm run fetch-apis` fails with an "Unknown file extension .ts" or flag error | Node is older than 22.6. Upgrade Node. |
| Migration says `relation ... already exists, skipping` | Normal; the script is idempotent. |
| Reset fails with a foreign-key error | `03_reset.sql` was not updated (step 1.2). |
| `verify_setup.py` says the history table is MISSING | Run `sql/04_create_intervention_history.sql`. |
| Search shows only 50 rows for a big filter | Intended: the page size is 50 (the badge says "50+"). |
| A LOW encounter cannot be updated | Intended: only MEDIUM/HIGH are in the care queue. |

## Appendix C: optional stretch (only if asked)

Prev/Next paging using `offset`; a dedicated "High Care Queue" page on `GET /care-queue/high` with a status filter; one shared `BASE_URL` instead of three copies.
