export interface CodeCompletionReq {
    prefix: string;
    suffix: string;
}

export class OmniCodeT5PAPI {
    /** OMNI Interface Layer: CodeT5+ API */
    public static constructFIMPrompt(req: CodeCompletionReq): string {
        return `<fim_prefix>${req.prefix}<fim_suffix>${req.suffix}<fim_middle>`;
    }

    public static parseCompletion(response: string): string {
        const middleMatch = response.match(/<fim_middle>(.*?)<fim_end>/s);
        return middleMatch ? middleMatch[1] : response;
    }
}
