// moe_capacity_admin.ts — UI / Admin
// Layer: Interface / UI — MoE Capacity Reservation Admin
//
// Inspired by reserve-rec-admin.
// A centralized admin controller for reserving expert capacity for VIP tenants.
// Instead of reserving recreation sites, it reserves tokens/sec bandwidth
// on specific high-value MoE domains (e.g., Coding Expert, Medical Expert).

export interface TenantReservation {
    tenantId: string;
    expertId: number;
    tokensPerSecond: number;
    startTimeIso: string;
    endTimeIso: string;
}

export class CapacityAdminController {
    private reservations: TenantReservation[] = [];
    private readonly MAX_EXPERT_CAPACITY_TPS = 100000; // 100k TPS hardware limit

    constructor() {
        console.log("[Admin UI] Initialized Capacity Admin Controller.");
    }

    /**
     * Attempts to reserve capacity for a tenant on a specific expert.
     */
    public createReservation(reservation: TenantReservation): boolean {
        // Calculate current allocated capacity for this expert
        const currentLoad = this.reservations
            .filter(r => r.expertId === reservation.expertId)
            .reduce((sum, r) => sum + r.tokensPerSecond, 0);

        if (currentLoad + reservation.tokensPerSecond > this.MAX_EXPERT_CAPACITY_TPS) {
            console.error(`[Admin UI] Reservation Failed: Expert ${reservation.expertId} is over capacity.`);
            return false;
        }

        this.reservations.push(reservation);
        console.log(`[Admin UI] Success: Reserved ${reservation.tokensPerSecond} TPS on Expert ${reservation.expertId} for Tenant ${reservation.tenantId}`);
        
        // In production, this would persist to PostgreSQL and sync to the Go Gateway
        this.syncToGateway();
        return true;
    }

    public getActiveReservations(expertId: number): TenantReservation[] {
        return this.reservations.filter(r => r.expertId === expertId);
    }

    private syncToGateway(): void {
        // Sends the updated capacity mapping to the Go Load Balancer
        console.log("[Admin UI] Syncing new QoS limits to network gateway...");
    }
}
