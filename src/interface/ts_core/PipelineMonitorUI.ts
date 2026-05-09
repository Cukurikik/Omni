export class PipelineMonitorUI {
    public updateStageStatus(stageId: number, status: 'active' | 'idle'): void {
        console.log(`Pipeline stage ${stageId} is now ${status}`);
    }
}
