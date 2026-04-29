class TIGERDialogueSyncError extends Error {
    constructor(message) {
        super(message);
        this.name = "TIGERDialogueSyncError";
    }
}

class Result {
    constructor(value, error = null) {
        this.value = value;
        this.error = error;
    }

    isOk() {
        return this.error === null;
    }

    unwrap() {
        if (!this.isOk()) {
            throw this.error;
        }
        return this.value;
    }
}

/**
 * OMNI Engine: tiger-sync
 * Event loop frame blocking for generative dialogue frameworks.
 */
class TIGERDialogueSyncEngine {
    constructor(maxEventDelayMs = 250) {
        this.maxEventDelay = maxEventDelayMs;
    }

    validateDialogueGenerationDelay(computeTimeMs) {
        try {
            if (computeTimeMs < 0) {
                return new Result(null, new TIGERDialogueSyncError("Temporal loop matrix null"));
            }

            if (computeTimeMs > this.maxEventDelay) {
                return new Result(null, new TIGERDialogueSyncError(`Generation delay ${computeTimeMs}ms blocked node event loop`));
            }

            return new Result({ sync_valid: true, buffer_time: this.maxEventDelay - computeTimeMs });
        } catch (e) {
            return new Result(null, new TIGERDialogueSyncError(`Dialogue event blocker crushed: ${e.message}`));
        }
    }
}

module.exports = { TIGERDialogueSyncEngine, Result, TIGERDialogueSyncError };
