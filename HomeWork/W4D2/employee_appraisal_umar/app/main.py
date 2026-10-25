from typing import Optional
import psycopg
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from app import repository, services
from app.config import APP_NAME, get_cors_origins
from app.errors import ConfigurationError, DatabaseUnavailableError, InvalidInputError, NotFoundError
from app.models import (
    Employee, ReviewPeriods, PerformanceReview, ReviewCreate
)

app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _error_response(status_code: int, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": message})

@app.exception_handler(NotFoundError)
def not_found_handler(request: Request, exc: NotFoundError):
    return _error_response(404, str(exc))

@app.exception_handler(InvalidInputError)
def invalid_input_handler(request: Request, exc: InvalidInputError):
    return _error_response(400, str(exc))

@app.exception_handler(DatabaseUnavailableError)
def database_unavailable_handler(request: Request, exc: DatabaseUnavailableError):
    return _error_response(503, str(exc))

@app.exception_handler(ConfigurationError)
def configuration_handler(request: Request, exc: ConfigurationError):
    return _error_response(500, str(exc))

@app.exception_handler(psycopg.IntegrityError)
@app.exception_handler(psycopg.DataError)
def database_constraint_handler(request: Request, exc: psycopg.Error):
    return _error_response(400, "Invalid performance review data: check the employee, period, ratings, and whether a review already exists for this employee and period.")



@app.get("/employees", summary="Get all employees with their interventions")
def all_employees():
    employees = repository.fetch_all_employees()
    if not employees: raise NotFoundError("No employees found")
    return employees

@app.get("/review-periods", summary="Get all review periods")
def all_review_periods():
    review_periods = repository.fetch_review_periods()
    if not review_periods: raise NotFoundError("No review periods found")
    return review_periods

@app.get("/performance-reviews", summary="Get all performance reviews")
def all_performance_reviews():
    performance_reviews = repository.fetch_performance_reviews()
    if not performance_reviews: raise NotFoundError("No performance reviews found")
    return performance_reviews

@app.get("/performance-reviews/{id}", summary="Get performance reviews by ID")
def performance_reviews_by_id(id: int):
    performance_reviews = repository.fetch_performance_reviews_by_id(id)
    if not performance_reviews: raise NotFoundError(f"No performance reviews found forID {id}")
    return performance_reviews

@app.post("/performance-reviews", status_code=201, summary="Add a new performance review")
def create_performance_review(payload: ReviewCreate):
    success = repository.add_performance_review(
        employee_id=payload.employee_id,
        period_id=payload.period_id,
        quality_rating=payload.quality_rating,
        delivery_rating=payload.delivery_rating,
        teamwork_rating=payload.teamwork_rating,
        comments=payload.comments
    )
    if not success: raise InvalidInputError("Failed to add performance review")
    return {"message": "Performance review added successfully"}