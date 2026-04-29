export interface CodeGenRequest {
    prompt: string;
    language: string;
}

export class OmniCodeGenAPI {
    /** OMNI Interface Layer: CodeGen API */
    public static formatRequest(req: CodeGenRequest): string {
        return `[${req.language.toUpperCase()}] Generate: ${req.prompt}`;
    }
}
