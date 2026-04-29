export interface PromptNode {
    type: 'text' | 'variable' | 'instruction';
    content: string;
}

export interface PromptTemplate {
    id: string;
    version: number;
    nodes: PromptNode[];
}

export class PromptError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'PromptError';
    }
}

/**
 * OMNI PROMPTPAPERS: AST-based Prompt Builder
 * Type-safe construction of prompt-tuning templates.
 * Source: thunlp/PromptPapers
 */
export class PromptBuilder {
    private nodes: PromptNode[] = [];

    public addText(text: string): PromptBuilder {
        this.nodes.push({ type: 'text', content: text });
        return this;
    }

    public addVariable(varName: string): PromptBuilder {
        if (!/^[a-zA-Z0-9_]+$/.test(varName)) {
            throw new PromptError(`Invalid variable name: ${varName}`);
        }
        this.nodes.push({ type: 'variable', content: varName });
        return this;
    }

    public addInstruction(instruction: string): PromptBuilder {
        this.nodes.push({ type: 'instruction', content: instruction });
        return this;
    }

    public build(id: string, version: number = 1): PromptTemplate {
        if (this.nodes.length === 0) {
            throw new PromptError("Cannot build an empty prompt template.");
        }
        return {
            id,
            version,
            nodes: [...this.nodes]
        };
    }

    public render(template: PromptTemplate, context: Record<string, string>): string | PromptError {
        try {
            let result = '';
            for (const node of template.nodes) {
                if (node.type === 'text') {
                    result += node.content;
                } else if (node.type === 'variable') {
                    if (!(node.content in context)) {
                        return new PromptError(`Missing context for variable: ${node.content}`);
                    }
                    result += context[node.content];
                } else if (node.type === 'instruction') {
                    result += `\n[INSTRUCTION: ${node.content}]\n`;
                }
            }
            return result;
        } catch (e: any) {
            return new PromptError(`Rendering failed: ${e.message}`);
        }
    }
}
