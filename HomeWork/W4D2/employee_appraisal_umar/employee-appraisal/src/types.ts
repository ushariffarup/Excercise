export interface Employee {
    id: number;
    employee_id: string;
    name: string;
    department: string;
    email: string;
    status: string;
}

export interface ReviewPeriod{
    id: number;
    name: string;
    start_date: string;
    end_date: string;
    status: string;
}

export interface ReviewCreate{
    employee_id: number;
    period_id: number;
    quality_rating: number;
    delivery_rating: number;
    teamwork_rating: number;
    comments: string;
}

export type View = 'submit' | 'list' | 'details';

export interface ReviewListItem {
    id: number;
    employee_id: number;
    employee_code: string;
    period_id: number;
    quality_rating: number;
    delivery_rating: number;
    teamwork_rating: number;
    average_rating: number;
    comments: string;
    created_at: string;
}

export interface ReviewDetail {
    id: number;
    employee_id: number;
    employee_code: string;
    period_id: number;
    period_name: string;
    quality_rating: number;
    delivery_rating: number;
    teamwork_rating: number;
    average_rating: number;
    comments: string;
    status: string;
    created_at: string;
}

export interface Review{
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

export interface ErrorResponse {
    code: string;
    message: string;
}

export interface ValidationIssue {
    loc: string[];
    msg: string;
    type: string;
}

export interface HTTPValidationError{
    detail?: ValidationIssue[];
}