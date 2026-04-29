export interface TranslationTask {
    sourceText: string;
    targetLang: string;
}

export class OmniNiuTransAPI {
    /** OMNI Interface Layer: NiuTrans API */
    public static validateTask(task: TranslationTask): boolean {
        return task.sourceText.length > 0 && task.targetLang.length === 2; // e.g., 'en', 'fr'
    }
}
