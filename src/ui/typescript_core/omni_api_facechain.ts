export interface IdentityRequest {
    userId: string;
    style: string;
}

export class OmniFaceChainAPI {
    /** OMNI Interface Layer: FaceChain API */
    public static generateAvatar(req: IdentityRequest): string {
        return `Generating avatar for ${req.userId} in ${req.style} style.`;
    }
}
