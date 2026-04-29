export interface RepoSearch {
    query: string;
    repoName: string;
}

export class OmniRepoCodAPI {
    /** OMNI Interface Layer: RepoCod API */
    public static initiateSearch(req: RepoSearch): string {
        return `Searching ${req.repoName} for "${req.query}"`;
    }
}
