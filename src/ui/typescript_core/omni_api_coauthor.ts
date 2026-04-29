export interface LatexContext {
    packages: string[];
    body: string;
}

export class OmniCoauthorAPI {
    /** OMNI Interface Layer: Coauthor API */
    public static compilePreamble(ctx: LatexContext): string {
        return ctx.packages.map(p => `\\usepackage{${p}}`).join('\n');
    }
}
