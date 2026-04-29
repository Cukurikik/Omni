export interface GameEnvState {
    health: number;
    hunger: number;
    inventory: Record<string, number>;
}

export class OmniVoyagerAPI {
    /** OMNI Interface Layer: Voyager API */
    public static isTaskFeasible(state: GameEnvState, reqItems: Record<string, number>): boolean {
        if (state.health <= 0) return false;
        
        for (const [item, count] of Object.entries(reqItems)) {
            if ((state.inventory[item] || 0) < count) return false;
        }
        return true;
    }
}
