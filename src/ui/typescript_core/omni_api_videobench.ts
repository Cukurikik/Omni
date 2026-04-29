export interface VideoEvalRequest {
    videoId: string;
    timestamps: number[];
}

export class OmniVideoBenchAPI {
    /** OMNI Interface Layer: Video-Bench API */
    public static validateTimestamps(req: VideoEvalRequest, duration: number): boolean {
        return req.timestamps.every(ts => ts >= 0 && ts <= duration);
    }

    public static formatResults(score: number): string {
        return `[VideoBench] Evaluation Score: ${(score * 100).toFixed(2)}/100`;
    }
}
