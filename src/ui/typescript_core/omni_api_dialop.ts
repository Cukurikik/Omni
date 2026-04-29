export interface DialogueState {
    turnNumber: number;
    jointUtility: number;
}

export class OmniDialOpAPI {
    /** OMNI Interface Layer: DialOp API */
    public static renderState(state: DialogueState): string {
        return `Turn ${state.turnNumber} | Utility: ${state.jointUtility.toFixed(3)}`;
    }
}
