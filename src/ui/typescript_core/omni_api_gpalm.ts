// Omni API for GPA-LM Agent
export interface GameAction {
    agentId: string;
    actionType: string;
    targetCoordinates: [number, number];
}

export class OmniGPALMAPI {
    static serializeActionCommand(action: GameAction): string {
        return `CMD:${action.agentId}|${action.actionType}|X${action.targetCoordinates[0]}Y${action.targetCoordinates[1]}`;
    }
}
