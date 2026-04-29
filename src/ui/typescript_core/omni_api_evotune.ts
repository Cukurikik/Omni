export interface EvoTuneIndividual {
    id: string;
    prompt: string;
    fitnessScore: number;
}

export class OmniEvoTuneAPI {
    /** OMNI Interface Layer: EvoTune API */
    public static sortPopulation(pop: EvoTuneIndividual[]): EvoTuneIndividual[] {
        return [...pop].sort((a, b) => b.fitnessScore - a.fitnessScore);
    }

    public static getBest(pop: EvoTuneIndividual[]): EvoTuneIndividual | null {
        if (pop.length === 0) return null;
        return this.sortPopulation(pop)[0];
    }
}
