export interface ReflexionLog {
    attempt: number;
    trajectory: string;
    reflection: string;
}

export class OmniReflexionAPI {
    /** OMNI Interface Layer: Reflexion API */
    public static compileMemory(logs: ReflexionLog[]): string {
        return logs.map(l => `Attempt ${l.attempt}:\n${l.trajectory}\nReflection: ${l.reflection}`).join('\n\n');
    }
}
