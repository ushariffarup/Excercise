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

class SearchMatch(str, Enum):
    AND = "AND"
    OR = "OR"

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

class EncounterCreate(BaseModel):
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
    readmitted: Optional[Readmitted] = None

class PatientSearch(BaseModel):
    patient_id: Optional[int] = Field(default=None, gt=0)
    patient_nbr: Optional[int] = Field(default=None, gt=0)
    risk_level: Optional[RiskLevel] = None
    risk_score: Optional[int] = Field(default=None, ge=0, le=8)
    match: SearchMatch = SearchMatch.AND

    @model_validator(mode="after")
    def require_search_filter(self):
        if (
            self.patient_id is None
            and self.patient_nbr is None
            and self.risk_level is None
            and self.risk_score is None
        ):
            raise ValueError("Provide at least one search filter.")
        return self

class PatientSearchResult(BaseModel):
    encounter_id: int
    patient_nbr: int
    age: Optional[str] = None
    risk_score: int
    risk_level: RiskLevel
    review_reason: Optional[str] = None
    readmitted: Optional[str] = None