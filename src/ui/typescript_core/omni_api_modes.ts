export interface ExpertRoute {
    tokenId: string;
    expertId: number;
}

export class OmniMoDESAPI {
    /** OMNI Interface Layer: MoDES API */
    public static logRouting(route: ExpertRoute): string {
        return `Token ${route.tokenId} routed to Expert-${route.expertId}`;
    }
}
