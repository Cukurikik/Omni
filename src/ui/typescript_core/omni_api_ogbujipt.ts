export interface ClientConfig {
    baseUrl: string;
    apiKey?: string;
}

export class OmniOgbujiPTAPI {
    /** OMNI Interface Layer: OgbujiPT API */
    public static initClient(config: ClientConfig): string {
        return `Client initialized pointing to ${config.baseUrl}`;
    }
}
