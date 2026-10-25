import { useEffect, useState } from 'react';
import type { CSSProperties } from 'react';
import type { Employee, ReviewDetail } from '../types';

const MAX_RATING = 5;

const boxStyle: CSSProperties = { border: '1px solid #e5e7eb', borderRadius: '0.375rem', padding: '0.75rem', flex: '1 1 12rem' };
const boxLabelStyle: CSSProperties = { fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.5rem' };
const cellStyle: CSSProperties = { padding: '0.75rem', textAlign: 'left', borderBottom: '1px solid #e5e7eb' };

function Stars({ rating }: { rating: number }) {
    return (
        <span aria-label={`${rating} out of ${MAX_RATING}`}>
            {Array.from({ length: MAX_RATING }, (_, i) => (
                <span key={i} style={{ color: i < rating ? '#facc15' : '#d1d5db', fontSize: '1.25rem' }}>★</span>
            ))}
        </span>
    );
}

interface ReviewDetailsProps {
    reviewId: number;
    employees: Employee[];
    onBack: () => void;
}

export default function ReviewDetails({ reviewId, employees, onBack }: ReviewDetailsProps) {
    const [detail, setDetail] = useState<ReviewDetail | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        setDetail(null);
        setError(null);
        fetch(`http://localhost:8003/performance-reviews/${reviewId}`)
            .then(async response => {
                if (!response.ok) throw new Error(`Request failed with status ${response.status}`);
                return response.json();
            })
            .then((data: ReviewDetail[]) => {
                if (data.length === 0) throw new Error('Review not found');
                setDetail(data[0]);
            })
            .catch(err => setError(err instanceof Error ? err.message : 'Failed to load review'));
    }, [reviewId]);

    const employee = detail ? employees.find(e => e.id === detail.employee_id) : undefined;

    return (
        <section style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1.5rem', maxWidth: '64rem', textAlign: 'left' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 600, margin: 0 }}>Review Details</h2>
                <button
                    type="button"
                    onClick={onBack}
                    style={{ padding: '0.375rem 0.875rem', background: '#eff6ff', color: '#2563eb', border: '1px solid #bfdbfe', borderRadius: '0.25rem', cursor: 'pointer' }}
                >
                    Back to List
                </button>
            </div>

            {error && <p style={{ color: '#dc2626' }}>{error}</p>}
            {!error && !detail && <p style={{ color: '#6b7280' }}>Loading review…</p>}

            {detail && (
                <>
                    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
                        <div style={boxStyle}>
                            <div style={boxLabelStyle}>Employee</div>
                            <div>{detail.employee_code}{employee ? ` - ${employee.name}` : ''}</div>
                        </div>
                        <div style={boxStyle}>
                            <div style={boxLabelStyle}>Review Period</div>
                            <div>{detail.period_name}</div>
                        </div>
                        <div style={boxStyle}>
                            <div style={boxLabelStyle}>Overall Rating</div>
                            <div style={{ background: '#dcfce7', color: '#15803d', borderRadius: '0.375rem', padding: '0.5rem', fontSize: '1.5rem', fontWeight: 700, textAlign: 'center' }}>
                                {Number(detail.average_rating).toFixed(1)} <span style={{ fontSize: '1rem', fontWeight: 400 }}>/ {MAX_RATING}</span>
                            </div>
                        </div>
                    </div>

                    <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>Performance Criteria</h3>
                    <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '1.5rem' }}>
                        <thead>
                            <tr>
                                <th style={{ ...cellStyle, background: '#f3f4f6', fontWeight: 600 }}>Criteria</th>
                                <th style={{ ...cellStyle, background: '#f3f4f6', fontWeight: 600 }}>Rating</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style={cellStyle}>Quality of Work</td>
                                <td style={cellStyle}><Stars rating={detail.quality_rating} /></td>
                            </tr>
                            <tr>
                                <td style={cellStyle}>Delivery &amp; Ownership</td>
                                <td style={cellStyle}><Stars rating={detail.delivery_rating} /></td>
                            </tr>
                            <tr>
                                <td style={cellStyle}>Teamwork &amp; Collaboration</td>
                                <td style={cellStyle}><Stars rating={detail.teamwork_rating} /></td>
                            </tr>
                        </tbody>
                    </table>

                    <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>Manager Comments</h3>
                    <div style={{ background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '0.375rem', padding: '0.75rem', whiteSpace: 'pre-wrap' }}>
                        {detail.comments}
                    </div>
                </>
            )}
        </section>
    );
}
