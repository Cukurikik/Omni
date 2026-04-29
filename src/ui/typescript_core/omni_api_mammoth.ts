export interface ProofContext {
    axioms: string[];
    hypothesis: string;
}

export class OmniMAmmoTHAPI {
    /** OMNI Interface Layer: MAmmoTH API */
    public static checkContext(ctx: ProofContext): boolean {
        return ctx.axioms.length > 0;
    }
}
