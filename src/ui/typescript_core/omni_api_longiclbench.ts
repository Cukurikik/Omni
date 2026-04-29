export interface ICLTask {
    id: string;
    exampleCount: number;
}

export class OmniLongICLAPI {
    /** OMNI Interface Layer: LongICLBench API */
    public static runEvaluation(task: ICLTask): string {
        return `Evaluating ICL Task ${task.id} with ${task.exampleCount} examples.`;
    }
}
