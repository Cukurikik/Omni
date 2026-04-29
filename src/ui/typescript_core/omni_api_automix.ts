export interface RoutingConfig {
    threshold: number;
    fallbackModel: string;
}

export class OmniAutomixAPI {
    /** OMNI Interface Layer: Automix API */
    public static configureRouter(config: RoutingConfig): string {
        return `Automix active. Threshold: ${config.threshold}. Fallback: ${config.fallbackModel}`;
    }
}
