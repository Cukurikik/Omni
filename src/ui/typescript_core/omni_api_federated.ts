// Omni API for Federated Aggregator
export interface FederatedClientStatus {
    clientId: string;
    dataSamples: number;
    gradientNorm: number;
}

export class OmniFederatedAPI {
    static filterMaliciousClients(clients: FederatedClientStatus[], maxNormThreshold: number): FederatedClientStatus[] {
        // Drop clients with exploding gradients to prevent poisoning attacks
        return clients.filter(c => c.gradientNorm <= maxNormThreshold);
    }
}
