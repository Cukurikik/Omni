export class VideoTimelineError extends Error {
    constructor(message: string) {
        super(`Video Timeline Error: ${message}`);
        this.name = "VideoTimelineError";
    }
}

export class Result<T> {
    constructor(public readonly value: T | null, public readonly error: Error | null = null) {}

    isOk(): boolean {
        return this.error === null;
    }

    unwrap(): T {
        if (!this.isOk()) {
            throw this.error;
        }
        return this.value as T;
    }
}

/**
 * OMNI Engine: videodb-timeline
 * UI constraints mapping for temporal scrubbing block ranges and keyframe alignments.
 */
export class VideoDBTimelineEngine {
    constructor(private readonly timelinePixelWidth: number) {}

    public calculateScrubCoordinate(playheadTimestampSec: number, totalDurationSec: number): Result<{ pixel_x: number }> {
        try {
            if (totalDurationSec <= 0.0) {
                return new Result(null, new VideoTimelineError("Video geometry is zero, infinite bounds required"));
            }
            if (playheadTimestampSec < 0.0 || playheadTimestampSec > totalDurationSec) {
                return new Result(null, new VideoTimelineError("Playhead geometrically outside time bounds"));
            }
            if (this.timelinePixelWidth <= 0.0) {
                 return new Result(null, new VideoTimelineError("Screen width physically negative"));
            }

            const ratio = playheadTimestampSec / totalDurationSec;
            const pixelPos = ratio * this.timelinePixelWidth;

            return new Result({ pixel_x: pixelPos });
        } catch (e: any) {
            return new Result(null, new VideoTimelineError(`Scrub map fault: ${e.message}`));
        }
    }

    public alignKeyframeToNearestGrid(timestampSec: number, gridIntervalSec: number): Result<{ aligned_sec: number }> {
         try {
              if (gridIntervalSec <= 0.0) {
                   return new Result(null, new VideoTimelineError("Grid interval physically impossible"));
              }
              const snapped = Math.round(timestampSec / gridIntervalSec) * gridIntervalSec;
              return new Result({ aligned_sec: snapped });
         } catch(e: any) {
              return new Result(null, new VideoTimelineError(`Keyframe snap fault: ${e.message}`));
         }
    }
}
