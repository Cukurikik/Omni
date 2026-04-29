class SketchSyncError extends Error {
    constructor(message) {
        super(message);
        this.name = "SketchSyncError";
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
 * OMNI Engine: sketch-sync
 * Event loop synchronization mapping for streaming canvas topologies.
 */
class SketchSyncEngine {
    constructor(maxEventLagMs = 100) {
        this.maxEventLagMs = maxEventLagMs;
    }

    computeEventDesync(eventTimestampMs, currentLoopTimeMs) {
        try {
            if (eventTimestampMs > currentLoopTimeMs) {
                return new Result(null, new SketchSyncError("Temporal causality violation (Event from the future)"));
            }

            const lag = currentLoopTimeMs - eventTimestampMs;

            if (lag > this.maxEventLagMs) {
                return new Result(null, new SketchSyncError(`Event synchronization completely lost (Lag ${lag}ms > ${this.maxEventLagMs}ms)`));
            }

            return new Result({ lag_ms: lag, within_tolerance: true });
        } catch (e) {
            return new Result(null, new SketchSyncError(`Sync computation failed: ${e.message}`));
        }
    }

    evaluateStrokeOverlapProbability(strokeADataPoints, strokeBDataPoints, timeDeltaMs) {
         try {
             if (strokeADataPoints <= 0 || strokeBDataPoints <= 0) {
                  return new Result(null, new SketchSyncError("Zero geometric density in stroke data"));
             }
             
             // Time-decay intersection mapping
             let probability = 1.0 / (1.0 + (timeDeltaMs / 50.0));
             
             // Volume logic
             let mass = Math.min(strokeADataPoints, strokeBDataPoints) / Math.max(strokeADataPoints, strokeBDataPoints);
             probability *= mass;
             
             return new Result({ conflict_probability: probability, requires_mutex: probability > 0.8 });
         } catch(e) {
             return new Result(null, new SketchSyncError(`Overlap eval logic error: ${e.message}`));
         }
    }
}

module.exports = { SketchSyncEngine, Result, SketchSyncError };
