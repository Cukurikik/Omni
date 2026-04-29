export interface TemplateRequest {
    templateString: string;
    variables: Record<string, string>;
}

export class OmniHumanPromptAPI {
    /** OMNI Interface Layer: HumanPrompt API */
    public static extractVariables(template: string): string[] {
        const matches = template.match(/\{([^{}]+)\}/g);
        if (!matches) return [];
        return matches.map(m => m.slice(1, -1));
    }

    public static isComplete(req: TemplateRequest): boolean {
        const vars = this.extractVariables(req.templateString);
        return vars.every(v => req.variables[v] !== undefined);
    }
}
