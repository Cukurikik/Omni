// Omni API for Conversant Persona Engine
export interface PersonaState {
    id: string;
    memoryLength: number;
    activeTraits: string[];
}

export class OmniConversantAPI {
    static validatePersonaConfig(state: PersonaState): boolean {
        if (!state.id || state.id.trim() === '') return false;
        if (state.memoryLength < 0 || state.memoryLength > 10000) return false;
        if (!state.activeTraits || state.activeTraits.length === 0) return false;
        return true;
    }
}
