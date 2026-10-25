import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ReviewList from './components/ReviewList';
import ReviewDetails from './components/ReviewDetails';
//import EmployeeCard from './components/Employee';
import type { Employee, ReviewCreate, ReviewListItem, ReviewPeriod, View } from './types';
import './App.css';  

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function monthLabel(isoDate: string): string {
    return MONTHS[Number(isoDate.slice(5, 7)) - 1];
}

type RatingKey = 'quality' | 'delivery' | 'teamwork';

const RATING_FIELDS: { key: RatingKey; label: string }[] = [
    { key: 'quality', label: 'Quality of Work' },
    { key: 'delivery', label: 'Delivery & Ownership' },
    { key: 'teamwork', label: 'Teamwork & Collaboration' },
];

const EMPTY_RATINGS: Record<RatingKey, number> = { quality: 0, delivery: 0, teamwork: 0 };

function App() {
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [periods, setPeriods] = useState<ReviewPeriod[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [selectedEmployeeId, setSelectedEmployeeId] = useState<string>('');
    const [selectedPeriodId, setSelectedPeriodId] = useState<string>('');
    const [ratings, setRatings] = useState<Record<RatingKey, number>>(EMPTY_RATINGS);
    const [comments, setComments] = useState<string>('');
    const [ratingError, setRatingError] = useState<boolean>(false);
    const [submitStatus, setSubmitStatus] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
    const [view, setView] = useState<View>('submit');
    const [reviews, setReviews] = useState<ReviewListItem[]>([]);
    const [selectedReviewId, setSelectedReviewId] = useState<number | null>(null);

    useEffect(() => {
        fetch('http://localhost:8003/employees')
            .then(async response => {
                if (!response.ok) throw new Error(`Request failed with status ${response.status}`);
                return response.json();
            })
            .then((data: Employee[]) => setEmployees(data))
            .catch(err => setError(err instanceof Error ? err.message : 'Failed to load employees'));

        fetch('http://localhost:8003/review-periods')
            .then(async response => {
                if (!response.ok) throw new Error(`Request failed with status ${response.status}`);
                return response.json();
            })
            .then((data: ReviewPeriod[]) => setPeriods(data))
            .catch(err => setError(err instanceof Error ? err.message : 'Failed to load review periods'));
    }, []);

    useEffect(() => {
        if (view !== 'list') return;
        fetch('http://localhost:8003/performance-reviews')
            .then(async response => {
                if (!response.ok) throw new Error(`Request failed with status ${response.status}`);
                return response.json();
            })
            .then((data: ReviewListItem[]) => setReviews(data))
            .catch(err => setError(err instanceof Error ? err.message : 'Failed to load reviews'));
    }, [view]);

    function handleView(reviewId: number) {
        setSelectedReviewId(reviewId);
        setView('details');
    }

    function handleReset() {
        setSelectedEmployeeId('');
        setSelectedPeriodId('');
        setRatings(EMPTY_RATINGS);
        setComments('');
        setRatingError(false);
        setSubmitStatus(null);
    }

    async function handleSubmit(e: FormEvent<HTMLFormElement>) {
        e.preventDefault();
        const complete = RATING_FIELDS.every(field => ratings[field.key] > 0);
        setRatingError(!complete);
        if (!complete) return;

        const payload: ReviewCreate = {
            employee_id: Number(selectedEmployeeId),
            period_id: Number(selectedPeriodId),
            quality_rating: ratings.quality,
            delivery_rating: ratings.delivery,
            teamwork_rating: ratings.teamwork,
            comments,
        };

        try {
            const response = await fetch('http://localhost:8003/performance-reviews', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (!response.ok) {
                const body = await response.json().catch(() => null);
                const detail = typeof body?.detail === 'string' ? body.detail : `Request failed with status ${response.status}`;
                throw new Error(detail);
            }
            handleReset();
            setSubmitStatus({ type: 'success', text: 'Performance review submitted successfully.' });
        } catch (err) {
            setSubmitStatus({ type: 'error', text: err instanceof Error ? err.message : 'Failed to submit review' });
        }
    }

    return (
        <div className="App">
            <Header />
            <div style={{ display: 'flex' }}>
                <Sidebar active={view} onSelect={setView} />
                <main id="submit-review" style={{ flex: 1, padding: '1.5rem' }}>
                    {error && <p>Error loading data: {error}</p>}
                {view === 'submit' && (
                    <form onSubmit={handleSubmit} onReset={handleReset}>
                <h2>Submit Performance Review</h2>

                <div>
                    <label htmlFor="employee-select">Employee *</label>
                    <select
                        id="employee-select"
                        required
                        value={selectedEmployeeId}
                        onChange={e => setSelectedEmployeeId(e.target.value)}
                    >
                        <option value="" disabled>Select an employee</option>
                        {employees.map(employee => (
                            <option key={employee.id} value={employee.id}>
                                {employee.employee_id} - {employee.name}
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label htmlFor="period-select">Review Period *</label>
                    <select
                        id="period-select"
                        required
                        value={selectedPeriodId}
                        onChange={e => setSelectedPeriodId(e.target.value)}
                    >
                        <option value="" disabled>Select a review period</option>
                        {periods.map(period => (
                            <option key={period.id} value={period.id}>
                                {period.name} ({monthLabel(period.start_date)} - {monthLabel(period.end_date)})
                            </option>
                        ))}
                    </select>
                </div>

                <h3>Performance Ratings (1 - 5)</h3>
                {ratingError && <p style={{ color: '#dc2626' }}>Please rate all three categories before submitting.</p>}
                {RATING_FIELDS.map(field => (
                    <fieldset key={field.key}>
                        <legend>{field.label} *</legend>
                        {[1, 2, 3, 4, 5].map(value => (
                            <button
                                key={value}
                                type="button"
                                aria-label={`${value} star${value > 1 ? 's' : ''}`}
                                aria-pressed={ratings[field.key] === value}
                                onClick={() => setRatings(prev => ({ ...prev, [field.key]: value }))}
                                style={{
                                    background: 'none',
                                    border: 'none',
                                    padding: '0 2px',
                                    fontSize: '1.8rem',
                                    cursor: 'pointer',
                                    color: value <= ratings[field.key] ? '#facc15' : '#d1d5db',
                                }}
                            >
                                ★
                            </button>
                        ))}
                    </fieldset>
                ))}

                <div>
                    <label htmlFor="comments">Overall Comments *</label>
                    <textarea
                        id="comments"
                        required
                        rows={5}
                        placeholder="Enter your feedback, strengths, areas of improvement..."
                        value={comments}
                        onChange={e => setComments(e.target.value)}
                    />
                </div>

                <div>
                    <button type="reset">Reset</button>
                    <button type="submit">Submit Review</button>
                </div>
                {submitStatus && (
                    <p style={{ color: submitStatus.type === 'success' ? '#16a34a' : '#dc2626' }}>
                        {submitStatus.text}
                    </p>
                )}
                    </form>
                )}
                {view === 'list' && (
                    <ReviewList reviews={reviews} employees={employees} periods={periods} onView={handleView} />
                )}
                {view === 'details' && (
                    selectedReviewId !== null
                        ? <ReviewDetails reviewId={selectedReviewId} employees={employees} onBack={() => setView('list')} />
                        : <p>Select a review from Review List to see its details.</p>
                )}
                </main>
            </div>
        </div>
    );
}

export default App; 