import type { Employee } from '../types';

interface EmployeeProps {
    employee: Employee;
}

export default function EmployeeCard({ employee }: EmployeeProps) {
    return (
        <div>
            <p>ID: {employee.id}</p>
            <p>Employee Code: {employee.employee_id}</p>
            <p>Name: {employee.name}</p>
            <p>Department: {employee.department}</p>
            <p>Email: {employee.email}</p>
            <p>Status: {employee.status}</p>
        </div>
    );
}
