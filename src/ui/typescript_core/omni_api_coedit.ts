export class OmniCoEdITAPI {
    /** OMNI Interface Layer: CoEdIT API */
    public static validateTask(task: string): boolean {
        const valid = ['gec', 'simplification', 'paraphrase', 'coherence'];
        return valid.includes(task.toLowerCase());
    }

    public static diffStrings(original: string, edited: string): string {
        if (original === edited) return "No changes made.";
        return `[Before]: ${original}\n[After ]: ${edited}`;
    }
}
