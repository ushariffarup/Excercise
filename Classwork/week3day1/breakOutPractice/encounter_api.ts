import type { Encounter1 } from "./encounter.ts";

async function getEncounterById(id: number): Promise<Encounter1> {
    const response = await fetch(`http://127.0.0.1:8000/encounters/${id}`);
    if (!response.ok) {
        throw new Error(`Request failed: ${response.status} ${response.statusText}`);
    }
    const data: Encounter1 = await response.json();
    return data;
}

getEncounterById(28236)
    .then((data) => console.log(data))
    .catch((error: unknown) => console.error(error));
/*
const encounter1: Encounter1     = {
    encounter_id: 12345,
    patient_name: "John Doe",
    age: 45,
    risk_level: "High",
    risk_score: 90,
    status: "ASSIGNED"
}


const encounter2: Encounter1 = {
     encounter_id: 67890,
    patient_name: "Umar Doe",
    age: 40,
    risk_level: "High",
    risk_score: 80,
    status: "ASSIGNED"
}

const finalencounters: Encounter1[] = [encounter1  ,encounter2];
console.log(finalencounters);*/