// OMNI Interface — TypeScript Dashboard Definitions
// Shared type contracts for the UI Layer

export type ClusterHealthStatus = 'ONLINE' | 'DEGRADED' | 'OFFLINE';

export interface GPUStats {
    id: string;
    temperatureCelsius: number;
    memoryUtilizedMb: number;
    memoryTotalMb: number;
    computeUtilizationPercent: number;
}

export interface NodeMetrics {
    nodeId: string;
    ipAddress: string;
    status: ClusterHealthStatus;
    gpus: GPUStats[];
    activeConnections: number;
    uptimeSeconds: number;
}

export interface InferenceEvent {
    eventId: string;
    modelId: string;
    promptTokens: number;
    completionTokens: number;
    latencyMs: number;
    timestampIso: string;
}

export interface UserContext {
    userId: string;
    role: 'ADMIN' | 'ENTERPRISE' | 'STANDARD';
    tenantId: string;
}
