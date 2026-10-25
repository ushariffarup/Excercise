import type { Review } from '../types';

interface ReviewProps {
    id: number;
    employee_id: string;
    employee_code: string;
    employee_name: string;
    period_id: string;
    period_name: string;
    quality_rating: number;
    delivery_rating: number;
    teamwork_rating: number;
    average_rating: number;
    comments: string;
    status: string;
    created_at: Date;
}

export default function Review({ id, employee_id, employee_code, employee_name, period_id, period_name, quality_rating, delivery_rating, teamwork_rating, average_rating, comments, status, created_at }: ReviewProps) {
    return (
        <div>
            <p>ID: {id}</p>
            <p>Employee ID: {employee_id}</p>
            <p>Employee Code: {employee_code}</p>
            <p>Employee Name: {employee_name}</p>
            <p>Period ID: {period_id}</p>
            <p>Period Name: {period_name}</p>
            <p>Quality Rating: {quality_rating}</p>
            <p>Delivery Rating: {delivery_rating}</p>
            <p>Teamwork Rating: {teamwork_rating}</p>
            <p>Average Rating: {average_rating}</p>
            <p>Comments: {comments}</p>
            <p>Status: {status}</p>
            <p>Created At: {created_at.toDateString()}</p>
        </div>
    );
}