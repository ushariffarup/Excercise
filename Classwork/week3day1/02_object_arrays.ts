export {};

const encounter1 = {
    
    encounter_id: 12345,
    patient_nbr: 7890,
    age: "45",
    risk_level: "High",
    status: "ASSIGNED"
}

const encounter2 = {
    
    encounter_id: 67890,
    patient_nbr: 23451,
    age: "50",
    risk_level: "Medium",
    status: "ASSIGNED"
}
//console.log(encounter1,encounter2);

const  encounters = [encounter1,encounter2];
console.log(encounters);

