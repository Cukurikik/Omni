export interface HALCParams {
    focalWeight: number;
    alpha: number;
}

export class OmniHALCAPI {
    /** OMNI Interface Layer: HALC API */
    public static configureDecoding(params: HALCParams): string {
        return `HALC Active: Focal=${params.focalWeight}, Alpha=${params.alpha}`;
    }
}
