import type { ReviewPeriod } from '../types';

interface ReviewPeriodProps {
    id: number;
    name: string;
    start_date: Date;
    end_date: Date;
    status: string;
}

export default function ReviewPeriod({ id, name, start_date, end_date, status }: ReviewPeriodProps) {
    return (
        <div>
            <p>ID: {id}</p>
            <p>Name: {name}</p>
            <p>Start Date: {start_date.toDateString()}</p>
            <p>End Date: {end_date.toDateString()}</p>
            <p>Status: {status}</p>
        </div>
    );
}