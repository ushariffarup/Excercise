from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator

class InterventionStatus(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    ASSIGNED = "ASSIGNED"
    CONTACTED = "CONTACTED"
    FOLLOW_UP_SCHEDULED = "FOLLOW_UP_SCHEDULED"
    CLOSED = "CLOSED"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Readmitted(str, Enum):
    UNDER_30 = "<30"
    OVER_30 = ">30"
    NO = "NO"

class HealthResponse(BaseModel):
    status: str

class InterventionUpdate(BaseModel):
    status: Optional[InterventionStatus] = None
    assigned_to: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = None

    @model_validator(mode="after")
    def require_one_field(self):
        if self.status is None and self.assigned_to is None and self.notes is None: raise ValueError("Provide at least one of: status, assigned_to, notes")
        return self

class OperationsSummary(BaseModel):
    total_encounters: int
    high_risk: int
    medium_risk: int
    low_risk: int
    pending_interventions: int
    assigned_interventions: int
    contacted_interventions: int
    follow_up_scheduled: int
    closed_interventions: int
    completed_interventions: int  # same value as closed_interventions; matches the brief's example shape

class ReadmissionAnalysis(BaseModel):
    overall_encounters: int
    overall_readmitted_under_30_days: int
    overall_readmission_rate: float
    high_risk_patients: int
    high_risk_readmitted_under_30_days: int
    high_risk_readmission_rate: float
    medium_risk_patients: int
    medium_risk_readmitted_under_30_days: int
    medium_risk_readmission_rate: float
    low_risk_patients: int
    low_risk_readmitted_under_30_days: int
    low_risk_readmission_rate: float
    note: str

class ManagementDashboard(BaseModel):
    total_diabetes_encounters: int
    readmitted_under_30_days: int
    readmission_rate: float
    high_risk_population: int
    high_risk_percent: float
    high_risk_30_day_readmissions: int
    care_queue_pending: int

class PatientSearchResult(BaseModel):
    """One encounter row from /patients/search, with its care intervention (null for LOW risk, which is not queued)."""
    encounter_id: int
    patient_nbr: int
    age: Optional[str] = None
    time_in_hospital: Optional[int] = None
    number_inpatient: Optional[int] = None
    number_emergency: Optional[int] = None
    number_outpatient: Optional[int] = None
    num_medications: Optional[int] = None
    num_lab_procedures: Optional[int] = None
    discharge_disposition_id: Optional[int] = None
    admission_type_id: Optional[int] = None
    readmitted: Optional[str] = None
    risk_score: int
    risk_level: RiskLevel
    review_reason: Optional[str] = None
    intervention_id: Optional[int] = None
    status: Optional[InterventionStatus] = None
    intervention_status: Optional[InterventionStatus] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None

class Intervention(BaseModel):
    intervention_id: int
    encounter_id: int
    patient_nbr: int
    risk_level: RiskLevel
    risk_score: int
    status: InterventionStatus
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class InterventionHistoryItem(BaseModel):
    history_id: int
    encounter_id: int
    patient_nbr: int
    status: InterventionStatus
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    changed_at: datetime

class EncounterCreate(BaseModel):
    patient_nbr: int
    age: Optional[str] = None
    time_in_hospital: int = Field(default=0, ge=0)
    number_inpatient: int = Field(default=0, ge=0)
    number_emergency: int = Field(default=0, ge=0)
    number_outpatient: int = Field(default=0, ge=0)
    num_medications: int = Field(default=0, ge=0)
    num_lab_procedures: int = Field(default=0, ge=0)
    num_procedures: int = Field(default=0, ge=0)
    admission_type_id: Optional[int] = 1
    discharge_disposition_id: Optional[int] = 1
    readmitted: Optional[str] = "NO"

    @model_validator(mode="before")
    @classmethod
    def normalize_aliases(cls, data):
        if isinstance(data, dict):
            p_nbr = data.get("patient_nbr") if "patient_nbr" in data else (data.get("patient_number") or data.get("patient-number"))
            if p_nbr is not None:
                data["patient_nbr"] = p_nbr
            hosp = data.get("time_in_hospital") if "time_in_hospital" in data else data.get("hospital")
            if hosp is not None:
                data["time_in_hospital"] = hosp
            inp = data.get("number_inpatient") if "number_inpatient" in data else data.get("inpatient")
            if inp is not None:
                data["number_inpatient"] = inp
            em = data.get("number_emergency") if "number_emergency" in data else data.get("emergency")
            if em is not None:
                data["number_emergency"] = em
            meds = data.get("num_medications") if "num_medications" in data else data.get("medications")
            if meds is not None:
                data["num_medications"] = meds
        return data

class EncounterResponse(BaseModel):
    encounter_id: int
    patient_nbr: int
    age: Optional[str] = None
    time_in_hospital: Optional[int] = None
    number_inpatient: Optional[int] = None
    number_emergency: Optional[int] = None
    number_outpatient: Optional[int] = None
    num_medications: Optional[int] = None
    num_lab_procedures: Optional[int] = None
    num_procedures: Optional[int] = None
    admission_type_id: Optional[int] = None
    discharge_disposition_id: Optional[int] = None
    readmitted: Optional[str] = None
    risk_score: int
    risk_level: RiskLevel
    review_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    intervention_id: Optional[int] = None
    status: Optional[InterventionStatus] = None

