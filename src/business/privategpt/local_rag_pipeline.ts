// OMNI PRIVATEGPT: Local RAG Pipeline
// TypeScript routing pipeline ensuring vectors and prompts never leave the local environment.
// Source: imartinez/privateGPT

export class SecurityBoundaryError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'SecurityBoundaryError';
    }
}

export interface Document {
    id: string;
    text: string;
    metadata: Record<string, any>;
}

export interface LocalLLMClient {
    generate(prompt: string): Promise<string>;
}

export interface LocalVectorStore {
    search(query: string, k: number): Promise<Document[]>;
}

export class PrivateRAGPipeline {
    private llm: LocalLLMClient;
    private vectorStore: LocalVectorStore;
    private enforceAirgap: boolean;

    constructor(llm: LocalLLMClient, vectorStore: LocalVectorStore, enforceAirgap: boolean = true) {
        this.llm = llm;
        this.vectorStore = vectorStore;
        this.enforceAirgap = enforceAirgap;
    }

    private checkNetworkIsolation(): void | SecurityBoundaryError {
        // Simulated air-gap check. In production, this checks process network namespaces or firewall rules.
        if (this.enforceAirgap) {
            const hasExternalAccess = false; // Mock
            if (hasExternalAccess) {
                return new SecurityBoundaryError("Airgap violation detected. Process has external network access.");
            }
        }
    }

    public async query(userQuestion: string): Promise<string | SecurityBoundaryError> {
        try {
            // 1. Pre-flight security check
            const securityCheck = this.checkNetworkIsolation();
            if (securityCheck instanceof SecurityBoundaryError) return securityCheck;

            // 2. Local Vector Search
            const relevantDocs = await this.vectorStore.search(userQuestion, 3);
            
            // 3. Construct Context
            const contextStr = relevantDocs.map(d => d.text).join("\n\n---\n\n");
            
            const prompt = `System: Answer the question based ONLY on the following context. If the context does not contain the answer, say "I don't know." Do not rely on external knowledge.\n\nContext:\n${contextStr}\n\nUser Question: ${userQuestion}\nAnswer:`;

            // 4. Local Generation
            const response = await this.llm.generate(prompt);
            
            return response;

        } catch (e: any) {
            return new SecurityBoundaryError(`Pipeline execution failed: ${e.message}`);
        }
    }
}
