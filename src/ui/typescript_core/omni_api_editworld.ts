export interface WorldState {
    y: number;
    vy: number;
}

export class OmniEditWorldAPI {
    /** OMNI Interface Layer: EditWorld API */
    public static renderState(state: WorldState): string {
        return `[EditWorld] POS Y: ${state.y.toFixed(2)}m | VEL Y: ${state.vy.toFixed(2)}m/s`;
    }

    public static parseInstruction(instruction: string): number {
        if (instruction.includes("drop")) return 0.0;
        if (instruction.includes("throw")) return 5.0; // Init velocity
        return 0.0;
    }
}
