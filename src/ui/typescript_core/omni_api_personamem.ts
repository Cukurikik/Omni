export interface PersonaUpdate {
    userId: string;
    fact: string;
}

export class OmniPersonaMemAPI {
    /** OMNI Interface Layer: PersonaMem API */
    public static formatMemoryRetrieval(userId: string, facts: string[]): string {
        if (facts.length === 0) return `No persona memory for user ${userId}.`;
        return `Persona Facts for ${userId}:\n` + facts.map(f => `- ${f}`).join('\n');
    }

    public static validateUpdate(update: PersonaUpdate): boolean {
        return update.userId.trim() !== '' && update.fact.trim() !== '';
    }
}
