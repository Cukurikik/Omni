export interface AUVState {
    depth: number;
    velocity: number;
}

export class OmniOceanGymAPI {
    /** OMNI Interface Layer: OceanGym API */
    public static renderTelemetry(state: AUVState): string {
        return `AUV Telemetry | Depth: ${state.depth}m | Vel: ${state.velocity}m/s`;
    }
}
