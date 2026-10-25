from datetime import datetime
import email
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator

class Employee(BaseModel):
    id: int
    employee_id: str
    name: str
    department: str
    email: str
    status: str="active"

class ReviewPeriods(BaseModel):
    id: int
    name: str
    start_date: datetime
    end_date: datetime
    status: str="open"

class PerformanceReview(BaseModel):
    id: int
    employee_id: int
    employee_code: str
    period_id: int
    quality_rating: int
    delivery_rating: int
    teamwork_rating: int
    average_rating: float
    comments: str = None
    created_at: datetime=datetime.now()

class ReviewCreate(BaseModel):
    #id: Optional[int] = None
    employee_id: int
    #employee_code: Optional[str] = None
    period_id: int
    quality_rating: int
    delivery_rating: int
    teamwork_rating: int
    #average_rating: Optional[float] = None
    comments: str = None
    #created_at: datetime=datetime.now()
    