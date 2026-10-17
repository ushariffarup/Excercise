from enum import Enum
from pydantic import BaseModel


class InterventionStatus(str, Enum):
	PENDING_REVIEW = "PENDING REVIEW"
	ASSIGNED = "ASSIGNED"
	CONTACTED = "CONTACTED"
	FOLLOW_UP_SCHEDULED = "FOLLOW UP SCHEDULED"
	CLOSED = "CLOSED"


class InterventionUpdate(BaseModel):
	status: InterventionStatus
	assigned_to: str | None = None
	notes: str | None = None
