-- Clears imported data (keeps tables and the status lookup). All tables in one statement respects the foreign keys.
TRUNCATE TABLE care_intervention_history, care_interventions, patient_encounters RESTART IDENTITY;
