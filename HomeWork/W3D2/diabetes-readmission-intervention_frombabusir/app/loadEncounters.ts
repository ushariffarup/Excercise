
const API_BASE_URL = "http://127.0.0.1:8001";
const PAGE_SIZE = 500;

type RiskLevel = "LOW" | "MEDIUM" | "HIGH";

type Encounter = {
    encounter_id: number;
    patient_nbr: number;
    risk_score: number;
    risk_level: RiskLevel;
};

function isEncounter(value: unknown): value is Encounter {
    if (typeof value !== "object" || value === null) {
        return false;
    }
    const encounter = value as Record<string, unknown>;
    return (
        typeof encounter.encounter_id === "number" &&
        typeof encounter.patient_nbr === "number" &&
        typeof encounter.risk_score === "number" &&
        ["LOW", "MEDIUM", "HIGH"].includes(String(encounter.risk_level))
    );
}

async function fetchEncounters(riskLevel?: RiskLevel): Promise<Encounter[]> {
    const encounters: Encounter[] = [];

    for (let offset = 0; ; offset += PAGE_SIZE) {
        const params = new URLSearchParams({
            limit: String(PAGE_SIZE),
            offset: String(offset),
        });
        if (riskLevel) {
            params.set("risk_level", riskLevel);
        }

        const response = await fetch(`${API_BASE_URL}/encounters?${params}`);
        const result: unknown = await response.json();
        if (!response.ok) {
            const detail =
                typeof result === "object" && result !== null && "detail" in result
                    ? JSON.stringify(result.detail)
                    : JSON.stringify(result);
            throw new Error(detail || `HTTP error: ${response.status}`);
        }
        if (!Array.isArray(result) || !result.every(isEncounter)) {
            throw new Error("The API response was not a valid list of encounters.");
        }

        encounters.push(...result);
        if (result.length < PAGE_SIZE) {
            return encounters;
        }
    }
}

async function main(): Promise<void> {
    const prompt = createInterface({ input: stdin, output: stdout });
    try {
        const patientInput = (await prompt.question("Patient number (blank for any): ")).trim();
        const riskInput = (await prompt.question("Risk level LOW, MEDIUM, HIGH (blank for any): "))
            .trim()
            .toUpperCase();
        const scoreInput = (await prompt.question("Risk score (blank for any): ")).trim();

        if (patientInput && !/^\d+$/.test(patientInput)) {
            throw new Error("Patient number must be a whole number.");
        }
        if (riskInput && !["LOW", "MEDIUM", "HIGH"].includes(riskInput)) {
            throw new Error("Risk level must be LOW, MEDIUM, or HIGH.");
        }
        if (scoreInput && (!/^\d+$/.test(scoreInput) || Number(scoreInput) > 8)) {
            throw new Error("Risk score must be a whole number from 0 to 8.");
        }
        if (!patientInput && !riskInput && !scoreInput) {
            throw new Error("Enter at least one search filter.");
        }

        const riskLevel = riskInput ? (riskInput as RiskLevel) : undefined;
        const encounters = await fetchEncounters(riskLevel);
        const matches = encounters.filter((encounter) =>
            (!patientInput || encounter.patient_nbr === Number(patientInput)) &&
            (!scoreInput || encounter.risk_score === Number(scoreInput))
        );

        if (matches.length === 0) {
            console.log("No encounters matched those filters.");
            return;
        }

        console.table(matches.map(({ encounter_id, patient_nbr, risk_level, risk_score }) => ({
            encounter_id,
            patient_nbr,
            risk_level,
            risk_score,
        })));
        console.log(`${matches.length} matching encounter(s).`);
    } finally {
        prompt.close();
    }
}

