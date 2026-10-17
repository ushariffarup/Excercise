employees = [{'name': 'John Doe', 'position': 'Manager', 'salary': 6000},
             {'name': 'Jane Smith', 'position': 'Supervisor', 'salary': 4500},
             {'name': 'Alice Johnson', 'position': 'Director', 'salary': 8000},
             {'name': 'Bob Brown', 'position': 'Intern', 'salary': 2000},
             {'name': 'Charlie Davis', 'position': 'Consultant', 'salary': 5000},
             {'name': 'Eve White', 'position': 'Analyst', 'salary': 4000}
            ]

for employee in employees:
    if len(employee['name']) > 5 and employee['salary'] > 4000:
        print(f"Employee name: {employee['name']}, Length: {len(employee['name'])}, Salary: {employee['salary']}")
        