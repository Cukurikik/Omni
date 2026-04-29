export interface CollabState {
    progress: number;
    human_assisted: boolean;
    done: boolean;
}

export class OmniCollabGymAPI {
    /** OMNI Interface Layer: CollabGym API */
    public static renderHUD(state: CollabState): string {
        const bar = '='.repeat(Math.floor(state.progress / 10)) + '-'.repeat(10 - Math.floor(state.progress / 10));
        return `[${bar}] ${state.progress}% | Human Assist: ${state.human_assisted}`;
    }
}
