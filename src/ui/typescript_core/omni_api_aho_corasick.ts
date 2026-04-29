export class OmniAhoCorasickAPI {
    public static search(text: string, patterns: string[]): Map<string, number[]> {
        const result = new Map<string, number[]>();
        for (const p of patterns) {
            const positions: number[] = [];
            let idx = text.indexOf(p);
            while (idx !== -1) { positions.push(idx); idx = text.indexOf(p, idx + 1); }
            if (positions.length > 0) result.set(p, positions);
        }
        return result;
    }
}
