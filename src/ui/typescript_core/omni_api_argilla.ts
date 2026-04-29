export interface AnnotationRecord {
    id: string;
    label: string;
    confidence: number;
}

export class OmniArgillaAPI {
    /** OMNI Interface: Argilla Data Annotation API */
    public static summarize(records: AnnotationRecord[]): string {
        const avgConf = records.reduce((s, r) => s + r.confidence, 0) / Math.max(1, records.length);
        return `Argilla: ${records.length} annotations, avg confidence=${avgConf.toFixed(3)}`;
    }
}
