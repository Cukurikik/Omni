export interface TuningJob {
    jobId: string;
    status: "pending" | "running" | "completed";
}

export class OmniLLaMAFactoryAPI {
    /** OMNI Interface Layer: LLaMA-Factory API */
    public static updateJob(job: TuningJob): string {
        return `Job ${job.jobId} is ${job.status}`;
    }
}
