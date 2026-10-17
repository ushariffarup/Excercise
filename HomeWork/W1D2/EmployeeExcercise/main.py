import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
DATA_FILE = "data/employees.json"

app = FastAPI()

class Employee(BaseModel):
    employee_id: str
    name: str
    position: str
    department: str

with open(DATA_FILE, "r") as f:
    employees = json.load(f)

@app.get("/employees")
def get_employees():
    return employees

@app.post("/employees")
def create_employee(employee: Employee):
    for exising_employee in employees:
        if exising_employee["employee_id"] == employee.employee_id:
            raise  HTTPException(status_code=400, detail="Employee with this ID already exists")
    employees.append(employee.dict())
    with open(DATA_FILE, "w") as f:
        json.dump(employees, f, indent=4)
    return employee
