import type { Encounter } from '../types';
import PatientRow from './PatientRow';

interface PatientTableProps {
    encounters: Encounter[];
}

export default function PatientTable({ encounters }: PatientTableProps) {
    return (
        <table>
            <thead>
                <tr>
                    <th>Encounter ID</th>
                    <th>Patient ID</th>
                    <th>Age</th>
                    <th>Risk Level</th>
                </tr>
            </thead>
            <tbody>
                {encounters.map((encounter) => (
                    <PatientRow key={encounter.encounter_id} encounter={encounter} />
                ))}
            </tbody>
        </table>
    );
}