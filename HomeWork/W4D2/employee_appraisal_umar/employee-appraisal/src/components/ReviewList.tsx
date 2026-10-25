import { useMemo, useState } from 'react';
import type { CSSProperties, FormEvent } from 'react';
import type { Employee, ReviewListItem, ReviewPeriod } from '../types';

const PAGE_SIZE = 5;
const TABLE_HEADERS = ['Employee ID', 'Employee Name', 'Period', 'Ratings', 'Average', 'Status', 'Action'];

const cellStyle: CSSProperties = { padding: '0.75rem', textAlign: 'left', borderBottom: '1px solid #e5e7eb' };
const headerCellStyle: CSSProperties = { ...cellStyle, background: '#f3f4f6', fontWeight: 600 };
const labelStyle: CSSProperties = { display: 'block', fontSize: '0.875rem', marginBottom: '0.25rem' };
const selectStyle: CSSProperties = { width: '100%', padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.25rem', background: '#fff' };

function pageButtonStyle(active: boolean): CSSProperties {
    return {
        minWidth: '2rem',
        padding: '0.25rem 0.5rem',
        border: '1px solid #d1d5db',
        borderRadius: '0.25rem',
        background: active ? '#2563eb' : '#fff',
        color: active ? '#fff' : '#1f2937',
        cursor: 'pointer',
    };
}

interface ReviewListProps {
    reviews: ReviewListItem[];
    employees: Employee[];
    periods: ReviewPeriod[];
    onView: (reviewId: number) => void;
}

interface AppliedFilters {
    periodId: string;
    employeeId: string;
}

export default function ReviewList({ reviews, employees, periods, onView }: ReviewListProps) {
    const [periodDraft, setPeriodDraft] = useState('');
    const [employeeDraft, setEmployeeDraft] = useState('');
    const [applied, setApplied] = useState<AppliedFilters>({ periodId: '', employeeId: '' });
    const [page, setPage] = useState(1);

    const filtered = useMemo(
        () => [...reviews]
            .sort((a, b) => b.created_at.localeCompare(a.created_at) || b.id - a.id)
            .filter(review =>
                (applied.periodId === '' || review.period_id === Number(applied.periodId)) &&
                (applied.employeeId === '' || review.employee_id === Number(applied.employeeId))
            ),
        [reviews, applied]
    );

    const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
    const currentPage = Math.min(page, totalPages);
    const startIndex = (currentPage - 1) * PAGE_SIZE;
    const visible = filtered.slice(startIndex, startIndex + PAGE_SIZE);

    function handleSearch(e: FormEvent<HTMLFormElement>) {
        e.preventDefault();
        setApplied({ periodId: periodDraft, employeeId: employeeDraft });
        setPage(1);
    }

    return (
        <section style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem', padding: '1.5rem', maxWidth: '64rem', textAlign: 'left' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginTop: 0 }}>Performance Reviews</h2>

            <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end', flexWrap: 'wrap', marginBottom: '1.5rem' }}>
                <div style={{ flex: '1 1 14rem' }}>
                    <label htmlFor="filter-period" style={labelStyle}>Review Period</label>
                    <select id="filter-period" value={periodDraft} onChange={e => setPeriodDraft(e.target.value)} style={selectStyle}>
                        <option value="">All Periods</option>
                        {periods.map(period => (
                            <option key={period.id} value={period.id}>{period.name}</option>
                        ))}
                    </select>
                </div>

                <div style={{ flex: '1 1 14rem' }}>
                    <label htmlFor="filter-employee" style={labelStyle}>
                        Employee <span style={{ color: '#dc2626' }}>*</span>
                    </label>
                    <select id="filter-employee" value={employeeDraft} onChange={e => setEmployeeDraft(e.target.value)} style={selectStyle}>
                        <option value="">All Employees</option>
                        {employees.map(employee => (
                            <option key={employee.id} value={employee.id}>{employee.employee_id} - {employee.name}</option>
                        ))}
                    </select>
                </div>

                <button type="submit" style={{ padding: '0.5rem 1.25rem', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '0.25rem', cursor: 'pointer' }}>
                    Search
                </button>
            </form>

            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                    <tr>
                        {TABLE_HEADERS.map(header => (
                            <th key={header} style={headerCellStyle}>{header}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {visible.length === 0 && (
                        <tr>
                            <td colSpan={TABLE_HEADERS.length} style={{ ...cellStyle, textAlign: 'center', color: '#6b7280' }}>
                                No reviews found.
                            </td>
                        </tr>
                    )}
                    {visible.map(review => {
                        const employee = employees.find(e => e.id === review.employee_id);
                        const period = periods.find(p => p.id === review.period_id);
                        return (
                            <tr key={review.id}>
                                <td style={cellStyle}>{review.employee_code}</td>
                                <td style={cellStyle}>{employee?.name ?? '-'}</td>
                                <td style={cellStyle}>{period?.name ?? '-'}</td>
                                <td style={cellStyle}>{review.quality_rating}, {review.delivery_rating}, {review.teamwork_rating}</td>
                                <td style={cellStyle}>{Number(review.average_rating).toFixed(1)}</td>
                                <td style={cellStyle}>
                                    <span style={{ background: '#bbf7d0', color: '#166534', padding: '0.25rem 0.75rem', borderRadius: '9999px', fontSize: '0.875rem' }}>
                                        Completed
                                    </span>
                                </td>
                                <td style={cellStyle}>
                                    <button
                                        type="button"
                                        onClick={() => onView(review.id)}
                                        style={{ background: 'none', border: 'none', padding: 0, color: '#2563eb', cursor: 'pointer', fontSize: 'inherit', fontFamily: 'inherit' }}
                                    >
                                        View
                                    </button>
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                <span style={{ color: '#4b5563' }}>
                    {filtered.length === 0
                        ? 'Showing 0 reviews'
                        : `Showing ${startIndex + 1} to ${startIndex + visible.length} of ${filtered.length} reviews`}
                </span>
                <div style={{ display: 'flex', gap: '0.25rem' }}>
                    <button type="button" style={pageButtonStyle(false)} disabled={currentPage === 1} onClick={() => setPage(currentPage - 1)}>
                        ‹
                    </button>
                    {Array.from({ length: totalPages }, (_, i) => i + 1).map(pageNumber => (
                        <button
                            key={pageNumber}
                            type="button"
                            style={pageButtonStyle(pageNumber === currentPage)}
                            onClick={() => setPage(pageNumber)}
                        >
                            {pageNumber}
                        </button>
                    ))}
                    <button type="button" style={pageButtonStyle(false)} disabled={currentPage === totalPages} onClick={() => setPage(currentPage + 1)}>
                        ›
                    </button>
                </div>
            </div>
        </section>
    );
}
