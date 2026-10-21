
interface Encounter {
    encounter_id: number;
    patient_nbr: number;
    age: string;
    risk_level: string;
    status: string;
}


const encounter1: Encounter ={    
    encounter_id: 12345,
    patient_nbr: 7890,
    age: "45",
    risk_level: "High",
    status: "ASSIGNED"
}

const encounter2: Encounter = {
    
    encounter_id: 67890,
    patient_nbr: 23451,
    age: "50",
    risk_level: "Medium",
    status: "ASSIGNED"
}


const encounters: Encounter[] = [encounter1,encounter2];
console.log(encounters);

