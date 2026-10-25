"""Business rules: risk scoring, CSV row cleaning and metric calculations. No SQL here.

EDUCATIONAL PROTOTYPE: the scoring weights are learning assumptions, not clinically validated rules.
"""
from app.errors import ImportDataError, InvalidInputError
REQUIRED_COLUMNS = ("id", "employee_id", "name", "department", "email", "status")
INT_COLUMNS = ("id",)
NULL_LIKE = ("", "null", "none")
RISK_RULES = {
    "high_risk": ["terminated", "inactive"],
    "medium_risk": ["probation"],
    "low_risk": ["active"]
}
OUTCOME_NOTE="Employee status outcome based on risk rules."
"""
Rating must be between 1 and 5.
"""
RATING_RANGE = range(1, 6)


def validate_rating(rating):
    """Ensure the rating is within the allowed range."""
    if rating not in RATING_RANGE:
        raise InvalidInputError(f"Rating {rating} is out of range. Must be between 1 and 5.")
    return True

calculate_average_rating = lambda ratings: sum(ratings) / len(ratings) if ratings else 0

def calculate_risk_status(status):
    """Determine the risk status based on employee status."""
    for risk, statuses in RISK_RULES.items():
        if status.lower() in statuses:
            return risk
    return "unknown"

"""One employee can have only one performance review per appraisal period.
"""
def validate_unique_review(employee_id, appraisal_period, existing_reviews):
    """Ensure one employee has only one review per appraisal period."""
    for review in existing_reviews:
        if review["employee_id"] == employee_id and review["appraisal_period"] == appraisal_period:
            raise InvalidInputError(f"Employee {employee_id} already has a review for period {appraisal_period}.")
    return True

"""Comments are mandatory for each performance review to provide context and justification for the rating.
"""
def validate_comment(comment):
    """Ensure that a comment is provided for the performance review."""
    if not comment or comment.strip() == "":
        raise InvalidInputError("Comment is required for the performance review.")
    return True

"""Review periods can be configured as annual or semi-annual.
"""
def validate_review_period(review_period):
    """Ensure the review period is either annual or semi-annual."""
    if review_period not in ("annual", "semi-annual"):
        raise InvalidInputError(f"Review period {review_period} is invalid. Must be 'annual' or 'semi-annual'.")
    return True 

""" Only open periods can accept new performance reviews.
"""
def validate_open_period(review_period, open_periods):
    """Ensure that the review period is currently open for submissions."""
    if review_period not in open_periods:
        raise InvalidInputError(f"Review period {review_period} is not open for submissions.")
    return True
