export class OmniMathQAAPI {
    /** OMNI Interface Layer: MathQA API */
    public static sanitizeEquation(eq: string): string {
        return eq.replace(/[^0-9\+\-\*\/\(\)\.]/g, '');
    }

    public static formatSolution(eq: string, result: number): string {
        return `${eq} = ${result}`;
    }
}
