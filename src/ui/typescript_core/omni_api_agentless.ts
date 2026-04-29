export interface PatchCandidate {
    filePath: string;
    line: number;
    score: number;
}

export class OmniAgentlessAPI {
    /** OMNI Interface: Agentless Bug Repair API */
    public static rankCandidates(candidates: PatchCandidate[]): PatchCandidate[] {
        return [...candidates].sort((a, b) => b.score - a.score);
    }
}
