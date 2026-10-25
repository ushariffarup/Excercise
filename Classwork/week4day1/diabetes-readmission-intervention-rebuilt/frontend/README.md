# Diabetes Patient Management - Frontend Client

A lightweight, self-contained single-page application for the Diabetes Readmission Intervention Queue.

## How to Run

1. **Start the FastAPI backend:**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```
2. **Open the web application:**
   - **Direct URL:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/) (FastAPI serves `index.html` directly)
   - **Local File:** Double-click or open `index.html` directly in your browser.

## Features

- **➕ Add Patient Encounter:** Enter hospital stay and clinical attributes to score 30-day readmission risk and auto-queue high/medium risk interventions.
- **🔍 Patient Search & Queue:** Search encounters by patient number, risk level (HIGH/MEDIUM/LOW), and exact risk score with instant filtering.
- **📋 Care Intervention & Tracking:** View patient intervention status, assign care managers, log clinical notes, and review the audit trail history.
- **⚡ Direct HTML Event Invocations:** All functions (`addPatient(event)`, `searchPatients()`, `updateIntervention(event)`, `switchTab()`) are invoked directly via HTML attributes (`onsubmit`, `onclick`, `onchange`).
