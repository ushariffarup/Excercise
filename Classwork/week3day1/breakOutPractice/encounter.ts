export interface Encounter1 {
    encounter_id: number;
    patient_nbr: number;
    age: string;
    time_in_hospital: number | null;
    risk_score: number;
    risk_level: string;
    readmitted: string | null;
}
/*
const encounter12: Encounter1 = {
    
    encounter_id: 12345,
    patient_name: "John Doe",
    age: 45,
    risk_level: "High",
    risk_score: 90,
    status: "ASSIGNED"
}

const encounter23: Encounter1 = {
    
    encounter_id: 7890,
    patient_name: "Umar Shariff",
    age: 45,
    risk_level: "MEDIUM",
    risk_score: 90,
    status: "ASSIGNED"
}
const finalencounters: Encounter1[] = [encounter12  ,encounter23];
console.log(finalencounters);
*/
