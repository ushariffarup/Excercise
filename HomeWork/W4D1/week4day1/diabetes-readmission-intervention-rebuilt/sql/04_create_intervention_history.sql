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
