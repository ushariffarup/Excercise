import type { ReviewCreate} from '../types';

interface ReviewCreateProps {
    employee_id: string;
    period_id: string;
    quality_rating: number;
    delivery_rating: number;
    teamwork_rating: number;
    comments: string;
}

export default function ReviewCreate({ employee_id, period_id, quality_rating, delivery_rating, teamwork_rating, comments }: ReviewCreateProps) {
    return (    
        <div>
            <p>Employee ID: {employee_id}</p>
            <p>Period ID: {period_id}</p>
            <p>Quality Rating: {quality_rating}</p>
            <p>Delivery Rating: {delivery_rating}</p>
            <p>Teamwork Rating: {teamwork_rating}</p>
            <p>Comments: {comments}</p>
        </div>
    );
}