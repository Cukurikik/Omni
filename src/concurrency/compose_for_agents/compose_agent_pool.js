// Compose for Agents - Agent Pool Scheduler
class OmniResult {
    constructor(isOk, value, error) {
        this.isOk = isOk;
        this.value = value;
        this.error = error;
    }
}

class AgentPool {
    constructor(maxWorkers) {
        this.maxWorkers = maxWorkers;
        this.workers = new Set();
        this.taskQueue = [];
    }

    async scheduleTask(task) {
        if (!task || typeof task !== 'function') {
            return new OmniResult(false, null, "Invalid task");
        }
        
        return new Promise((resolve) => {
            this.taskQueue.push({ task, resolve });
            this._processQueue();
        });
    }

    async _processQueue() {
        if (this.workers.size >= this.maxWorkers || this.taskQueue.length === 0) return;
        
        const workerId = Symbol('worker');
        this.workers.add(workerId);
        const { task, resolve } = this.taskQueue.shift();
        
        try {
            const result = await task();
            resolve(new OmniResult(true, result, null));
        } catch (error) {
            resolve(new OmniResult(false, null, error.message));
        } finally {
            this.workers.delete(workerId);
            this._processQueue();
        }
    }
}

module.exports = { AgentPool, OmniResult };
