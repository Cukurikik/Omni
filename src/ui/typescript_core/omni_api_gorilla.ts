export interface APIEndpoint {
    domain: string;
    signature: string;
}

export class OmniGorillaAPI {
    /** OMNI Interface Layer: Gorilla API */
    public static buildDocString(api: APIEndpoint): string {
        return `Domain: ${api.domain}\nUsage: ${api.signature}\nReturns: Expected Output`;
    }
}
