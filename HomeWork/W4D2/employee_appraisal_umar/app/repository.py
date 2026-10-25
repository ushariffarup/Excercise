"""All SQL lives here. Every value is passed as a psycopg parameter (%s); only fixed SQL fragments are ever joined into a query."""
from app.database import get_connection
EMPLOYEE_COLUMNS = ("id", "employee_id", "name", "department", "email", "status")
QUEUE_SELECT = "SELECT id, employee_id, name, department, email, status FROM employee_queue"
REVIEW_PERIOD_COLUMNS = ("id", "name", "start_date", "end_date","status")
PERFORMANCE_REVIEW_COLUMNS = ("id", "employee_id", "period_id", "quality_rating", "delivery_rating", "teamwork_rating", "average_rating", "comments", "created_at")

def _fetch_all(query, params=()):
    with get_connection() as conn: return conn.execute(query, params).fetchall()

def _fetch_one(query, params=()):
    with get_connection() as conn: return conn.execute(query, params).fetchone()

def _where(clauses: list) -> str:
    return f"WHERE {' AND '.join(clauses)}" if clauses else ""


def fetch_all_employees():
    return _fetch_all(
        f"SELECT {', '.join(EMPLOYEE_COLUMNS)} FROM employees"
    )   

def fetch_review_periods():
    return _fetch_all(
        f"SELECT {', '.join(REVIEW_PERIOD_COLUMNS)} FROM review_periods"
    )

def fetch_performance_reviews():
    return _fetch_all(
        "SELECT pr.id, pr.employee_id, e.employee_id AS employee_code, "
        "pr.period_id, pr.quality_rating, pr.delivery_rating, "
        "pr.teamwork_rating, pr.average_rating, pr.comments, pr.created_at "
        "FROM performance_reviews AS pr "
        "JOIN employees AS e ON e.id = pr.employee_id"
    )

def fetch_performance_reviews_by_id(id: int):
    return _fetch_all(
        "SELECT pr.id, pr.employee_id, e.employee_id AS employee_code, "
        "pr.period_id, rp.name AS period_name, pr.quality_rating, pr.delivery_rating, "
        "pr.teamwork_rating, pr.average_rating, pr.comments, rp.status, pr.created_at "
        "FROM performance_reviews AS pr "
        "JOIN employees AS e ON e.id = pr.employee_id "
        "JOIN review_periods AS rp ON rp.id = pr.period_id "    
        "WHERE pr.id = %s",
        (id,)
    )

def add_performance_review(employee_id: int, period_id: int, quality_rating: int, delivery_rating: int, teamwork_rating: int,  comments: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO performance_reviews (employee_id, period_id, quality_rating, delivery_rating, teamwork_rating, average_rating, comments) "
            "VALUES (%s, %s, %s, %s, %s, ROUND((%s + %s + %s) / 3.0, 2), %s)",
            (employee_id, period_id, quality_rating, delivery_rating, teamwork_rating,
             quality_rating, delivery_rating, teamwork_rating, comments)
        )
        conn.commit()
        return True
