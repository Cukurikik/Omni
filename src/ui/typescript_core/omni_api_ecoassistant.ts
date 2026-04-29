export interface RoutingRequest {
    prompt: string;
    maxBudget: number;
}

export class OmniEcoAssistantAPI {
    /** OMNI Interface Layer: EcoAssistant API */
    public static validateBudget(req: RoutingRequest): boolean {
        return req.maxBudget > 0;
    }

    public static formatDecision(model: string, cost: number): string {
        return `Routed to ${model}. Estimated Cost: $${cost.toFixed(4)}`;
    }
}
