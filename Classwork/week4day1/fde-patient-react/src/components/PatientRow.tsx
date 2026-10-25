import type { Encounter } from '../types';

interface PatientRowProps {
    encounter: Encounter;
}

export default function PatientRow({ encounter }: PatientRowProps) {
    return (
        <tr>
            <td>{encounter.encounter_id}</td>
            <td>{encounter.patient_nbr}</td>
            <td>{encounter.age}</td>
            <td>{encounter.risk_level}</td>
        </tr>
    );
}