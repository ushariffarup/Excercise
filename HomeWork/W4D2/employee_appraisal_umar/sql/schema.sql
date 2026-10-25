DROP TABLE IF EXISTS performance_reviews;
DROP TABLE IF EXISTS review_periods;
DROP TABLE IF EXISTS employees;

CREATE TABLE employees (
    id          SERIAL       PRIMARY KEY,
    employee_id VARCHAR(20)  NOT NULL UNIQUE,
    name        VARCHAR(100) NOT NULL,
    department  VARCHAR(100),
    email       VARCHAR(100) UNIQUE,
    status      VARCHAR(20)  NOT NULL DEFAULT 'Active'
        CHECK (status IN ('Active', 'Inactive'))
);

CREATE TABLE review_periods (
    id          SERIAL      PRIMARY KEY,
    name        VARCHAR(50) NOT NULL UNIQUE,
    start_date  DATE        NOT NULL,
    end_date    DATE        NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'Open'
        CHECK (status IN ('Open', 'Closed')),
    CONSTRAINT chk_period_dates CHECK (end_date > start_date)
);

CREATE TABLE performance_reviews (
    id              SERIAL       PRIMARY KEY,
    employee_id     INTEGER      NOT NULL
        REFERENCES employees(id) ON DELETE RESTRICT,
    period_id       INTEGER      NOT NULL
        REFERENCES review_periods(id) ON DELETE RESTRICT,
    quality_rating  INTEGER      NOT NULL CHECK (quality_rating  BETWEEN 1 AND 5),
    delivery_rating INTEGER      NOT NULL CHECK (delivery_rating BETWEEN 1 AND 5),
    teamwork_rating INTEGER      NOT NULL CHECK (teamwork_rating BETWEEN 1 AND 5),
    average_rating  NUMERIC(3,2) NOT NULL,
    comments        TEXT         NOT NULL CHECK (length(trim(comments)) > 0),
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_review_employee_period UNIQUE (employee_id, period_id),
    CONSTRAINT chk_average_rating CHECK (
        average_rating = ROUND((quality_rating + delivery_rating + teamwork_rating) / 3.0, 2)
    )
);

CREATE INDEX idx_reviews_period ON performance_reviews(period_id);
