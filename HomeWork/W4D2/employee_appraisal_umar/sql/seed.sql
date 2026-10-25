TRUNCATE TABLE performance_reviews, review_periods, employees RESTART IDENTITY CASCADE;

-- 1) employees (24 records: 22 Active, 2 Inactive)
INSERT INTO employees (employee_id, name, department, email, status) VALUES
    ('EMP101', 'John Smith',        'Engineering', 'john.smith@example.com',        'Active'),
    ('EMP102', 'Sarah Johnson',     'Engineering', 'sarah.johnson@example.com',     'Active'),
    ('EMP103', 'Michael Lee',       'Engineering', 'michael.lee@example.com',       'Active'),
    ('EMP104', 'Priya Sharma',      'QA',          'priya.sharma@example.com',      'Active'),
    ('EMP105', 'Arjun Mehta',       'QA',          'arjun.mehta@example.com',       'Active'),
    ('EMP106', 'Emily Davis',       'QA',          'emily.davis@example.com',       'Active'),
    ('EMP107', 'Ravi Kumar',        'Product',     'ravi.kumar@example.com',        'Active'),
    ('EMP108', 'Lisa Wong',         'Product',     'lisa.wong@example.com',         'Active'),
    ('EMP109', 'Daniel Brown',      'Product',     'daniel.brown@example.com',      'Active'),
    ('EMP110', 'Ananya Iyer',       'HR',          'ananya.iyer@example.com',       'Active'),
    ('EMP111', 'Kevin Wilson',      'HR',          'kevin.wilson@example.com',      'Active'),
    ('EMP112', 'Meera Nair',        'HR',          'meera.nair@example.com',        'Active'),
    ('EMP113', 'Robert Taylor',     'Finance',     'robert.taylor@example.com',     'Active'),
    ('EMP114', 'Divya Raman',       'Finance',     'divya.raman@example.com',       'Active'),
    ('EMP115', 'James Anderson',    'Finance',     'james.anderson@example.com',    'Active'),
    ('EMP116', 'Kavya Reddy',       'Sales',       'kavya.reddy@example.com',       'Active'),
    ('EMP117', 'Thomas Martin',     'Sales',       'thomas.martin@example.com',     'Active'),
    ('EMP118', 'Sneha Pillai',      'Sales',       'sneha.pillai@example.com',      'Active'),
    ('EMP119', 'David Garcia',      'Engineering', 'david.garcia@example.com',      'Active'),
    ('EMP120', 'Lakshmi Prasad',    'Engineering', 'lakshmi.prasad@example.com',    'Active'),
    ('EMP121', 'Chris Thompson',    'QA',          'chris.thompson@example.com',    'Active'),
    ('EMP122', 'Nisha Verma',       'Product',     'nisha.verma@example.com',       'Active'),
    ('EMP123', 'Mark Robinson',     'Sales',       'mark.robinson@example.com',     'Inactive'),
    ('EMP124', 'Pooja Desai',       'HR',          'pooja.desai@example.com',       'Inactive');

-- 2) review_periods (5 records: half-yearly + annual, Open + Closed)
INSERT INTO review_periods (name, start_date, end_date, status) VALUES
    ('H1 2025', '2025-01-01', '2025-06-30', 'Closed'),
    ('H2 2025', '2025-07-01', '2025-12-31', 'Closed'),
    ('FY 2025', '2025-01-01', '2025-12-31', 'Closed'),
    ('H1 2026', '2026-01-01', '2026-06-30', 'Open'),
    ('H2 2026', '2026-07-01', '2026-12-31', 'Open');

-- 3) performance_reviews (12 records), ids looked up by code/name, average computed by SQL
INSERT INTO performance_reviews
    (employee_id, period_id, quality_rating, delivery_rating, teamwork_rating, average_rating, comments)
SELECT e.id,
       p.id,
       v.quality,
       v.delivery,
       v.teamwork,
       ROUND((v.quality + v.delivery + v.teamwork) / 3.0, 2),
       v.comments
FROM (VALUES
    ('EMP101', 'H1 2026', 4, 5, 4, 'Strong ownership and consistently delivers high quality work.'),
    ('EMP102', 'H1 2026', 3, 4, 4, 'Reliable delivery; should improve code review depth.'),
    ('EMP103', 'H1 2026', 5, 5, 5, 'Outstanding across all areas; mentors the team.'),
    ('EMP104', 'H1 2026', 2, 3, 3, 'Needs to improve test coverage and estimation accuracy.'),
    ('EMP105', 'H1 2026', 4, 4, 4, 'Solid and dependable QA contributions.'),
    ('EMP106', 'H1 2026', 3, 3, 4, 'Good team player; build deeper automation skills.'),
    ('EMP101', 'H2 2025', 4, 4, 5, 'Great collaboration with product and QA.'),
    ('EMP102', 'H2 2025', 4, 4, 4, 'Consistent performer throughout the half.'),
    ('EMP107', 'H2 2025', 5, 4, 5, 'Excellent product discovery and stakeholder handling.'),
    ('EMP108', 'H2 2025', 3, 4, 3, 'Meets expectations; improve written specifications.'),
    ('EMP103', 'H1 2025', 4, 5, 5, 'Delivered the platform migration ahead of schedule.'),
    ('EMP123', 'H1 2025', 3, 4, 4, 'Met sales targets for the half.')
) AS v(emp_code, period_name, quality, delivery, teamwork, comments)
JOIN employees      e ON e.employee_id = v.emp_code
JOIN review_periods p ON p.name        = v.period_name;
