// OMNI MOTHER: TypeScript gRPC Web Client Wrapper (Production Grade)

export class OmniGrpcClient {
    private endpoint: string;

    constructor(endpoint: string) {
        this.endpoint = endpoint;
        console.log(`[OMNI gRPC] Initialized client for ${endpoint}`);
    }

    public async callService<TRequest, TResponse>(
        service: string, 
        method: string, 
        request: TRequest
    ): Promise<TResponse> {
        const url = `${this.endpoint}/${service}/${method}`;
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/grpc-web+json',
                'X-Omni-Source': 'frontend'
            },
            body: JSON.stringify(request)
        });

        if (!response.ok) {
            throw new Error(`gRPC call failed: ${response.statusText}`);
        }

        return await response.json() as TResponse;
    }
}
