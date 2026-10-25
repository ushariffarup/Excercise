import type { CSSProperties } from 'react';
import type { View } from '../types';

interface NavButtonProps {
    label: string;
    view: View;
    active: View;
    onSelect: (view: View) => void;
}

function NavButton({ label, view, active, onSelect }: NavButtonProps) {
    const isActive = active === view;
    const style: CSSProperties = {
        display: 'block',
        width: '100%',
        textAlign: 'left',
        padding: '0.5rem 0.75rem',
        borderRadius: '0.25rem',
        border: 'none',
        background: isActive ? '#dbeafe' : 'transparent',
        color: isActive ? '#1d4ed8' : '#1f2937',
        fontWeight: isActive ? 600 : 400,
        fontSize: 'inherit',
        fontFamily: 'inherit',
        cursor: 'pointer',
    };
    return (
        <button type="button" style={style} aria-current={isActive ? 'page' : undefined} onClick={() => onSelect(view)}>
            {label}
        </button>
    );
}

interface SidebarProps {
    active: View;
    onSelect: (view: View) => void;
}

export default function Sidebar({ active, onSelect }: SidebarProps) {
    return (
        <nav style={{ width: '14rem', minHeight: '100vh', background: '#f3f4f6', borderRight: '1px solid #e5e7eb', padding: '1rem' }}>
            <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
                <li>
                    <NavButton label="Submit Review" view="submit" active={active} onSelect={onSelect} />
                </li>
                <li>
                    <NavButton label="Review List" view="list" active={active} onSelect={onSelect} />
                    <ul style={{ listStyle: 'none', margin: '0.25rem 0 0', padding: '0 0 0 1rem' }}>
                        <li>
                            <NavButton label="Review Details" view="details" active={active} onSelect={onSelect} />
                        </li>
                    </ul>
                </li>
            </ul>
        </nav>
    );
}
