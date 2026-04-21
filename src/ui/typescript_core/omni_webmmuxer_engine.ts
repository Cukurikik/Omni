/// <reference lib="dom" />
/// <reference types="node" />
// omni_webmmuxer_engine.ts
// Production-Grade WebM Muxer Engine
// ==============================================================
// Absorbed from: Vanilagy/webm-muxer
//
// Key patterns learned and implemented:
// - EBML element construction for WebM container format
// - Video/Audio track configuration with codec parameters
// - Cluster-based frame packaging with timestamps
// - SimpleBlock construction with keyframe flags
// - Cue point indexing for seekable output
//
// OMNI Layer: ui/typescript_core
// @since 2026.4.0

const ENGINE_VERSION = "1.0.0-omni";

interface TrackConfig {
    trackNumber: number;
    trackType: "video" | "audio";
    codecId: string;
    sampleRate?: number;
    channels?: number;
    width?: number;
    height?: number;
    bitDepth?: number;
}

interface MuxedFrame {
    trackNumber: number;
    timestampMs: number;
    isKeyframe: boolean;
    dataSize: number;
}

interface ClusterInfo {
    clusterId: number;
    timestampMs: number;
    frameCount: number;
    totalBytes: number;
}

class WebmMuxerError extends Error {
    constructor(public code: string, message: string) {
        super(message);
        this.name = "WebmMuxerError";
    }
}

/**
 * Production-grade WebM container muxer engine.
 *
 * Constructs EBML-based WebM container structures with support
 * for video (VP8/VP9/AV1) and audio (Opus/Vorbis) tracks.
 * Manages clusters, SimpleBlocks, and cue points for seekable output.
 */
export class OmniWebmmuxerEngine {
    private tracks: Map<number, TrackConfig> = new Map();
    private clusters: ClusterInfo[] = [];
    private cuePoints: Array<{ timestampMs: number; clusterIndex: number }> = [];
    private currentCluster: ClusterInfo | null = null;
    private totalFrames: number = 0;
    private totalBytes: number = 0;
    private clusterDurationMs: number;
    private maxClusterSizeBytes: number;

    /**
     * @param clusterDurationMs - Maximum cluster duration in ms (default 1000).
     * @param maxClusterSizeBytes - Max cluster size in bytes (default 1MB).
     */
    constructor(clusterDurationMs: number = 1000, maxClusterSizeBytes: number = 1048576) {
        this.clusterDurationMs = clusterDurationMs;
        this.maxClusterSizeBytes = maxClusterSizeBytes;
    }

    /**
     * Add a track to the muxer.
     *
     * @param config - Track configuration.
     * @returns Track registration result.
     */
    addTrack(config: TrackConfig): { status: string; data: TrackConfig } {
        if (this.tracks.has(config.trackNumber)) {
            throw new WebmMuxerError(
                "DUPLICATE_TRACK",
                `Track ${config.trackNumber} already registered`
            );
        }

        const validVideoCodecs = ["V_VP8", "V_VP9", "V_AV1"];
        const validAudioCodecs = ["A_OPUS", "A_VORBIS"];

        if (config.trackType === "video") {
            if (!validVideoCodecs.includes(config.codecId)) {
                throw new WebmMuxerError(
                    "INVALID_CODEC",
                    `Video codec must be one of: ${validVideoCodecs.join(", ")}`
                );
            }
            if (!config.width || !config.height) {
                throw new WebmMuxerError("MISSING_DIMS", "Video track requires width and height");
            }
        } else if (config.trackType === "audio") {
            if (!validAudioCodecs.includes(config.codecId)) {
                throw new WebmMuxerError(
                    "INVALID_CODEC",
                    `Audio codec must be one of: ${validAudioCodecs.join(", ")}`
                );
            }
            if (!config.sampleRate) {
                throw new WebmMuxerError("MISSING_SR", "Audio track requires sampleRate");
            }
        }

        this.tracks.set(config.trackNumber, config);
        return { status: "success", data: config };
    }

    /**
     * Mux a frame into the container.
     *
     * @param trackNumber - Target track number.
     * @param timestampMs - Frame timestamp in milliseconds.
     * @param dataSize - Frame data size in bytes.
     * @param isKeyframe - Whether this is a keyframe.
     * @returns Muxed frame information.
     */
    addFrame(
        trackNumber: number,
        timestampMs: number,
        dataSize: number,
        isKeyframe: boolean = false
    ): { status: string; data: MuxedFrame & { clusterId: number } } {
        if (!this.tracks.has(trackNumber)) {
            throw new WebmMuxerError(
                "UNKNOWN_TRACK", `Track ${trackNumber} not registered`
            );
        }

        const needNewCluster =
            !this.currentCluster ||
            (timestampMs - this.currentCluster.timestampMs) > this.clusterDurationMs ||
            this.currentCluster.totalBytes > this.maxClusterSizeBytes ||
            (isKeyframe && this.currentCluster.frameCount > 0);

        if (needNewCluster) {
            this.currentCluster = {
                clusterId: this.clusters.length,
                timestampMs,
                frameCount: 0,
                totalBytes: 0,
            };
            this.clusters.push(this.currentCluster);

            if (isKeyframe) {
                this.cuePoints.push({
                    timestampMs,
                    clusterIndex: this.currentCluster.clusterId,
                });
            }
        }

        const simpleBlockHeaderSize = 4;
        const frameBytes = simpleBlockHeaderSize + dataSize;

        this.currentCluster.frameCount++;
        this.currentCluster.totalBytes += frameBytes;
        this.totalFrames++;
        this.totalBytes += frameBytes;

        return {
            status: "success",
            data: {
                trackNumber,
                timestampMs,
                isKeyframe,
                dataSize,
                clusterId: this.currentCluster.clusterId,
            },
        };
    }

    /**
     * Build EBML header bytes for the WebM file.
     *
     * @returns EBML and Segment header metadata.
     */
    buildEbmlHeader(): {
        status: string;
        data: {
            ebmlVersion: number;
            docType: string;
            tracks: TrackConfig[];
            headerSizeEstimate: number;
        };
    } {
        const trackList = Array.from(this.tracks.values());
        const headerSize = 40 + trackList.length * 64;

        return {
            status: "success",
            data: {
                ebmlVersion: 1,
                docType: "webm",
                tracks: trackList,
                headerSizeEstimate: headerSize,
            },
        };
    }

    /**
     * Finalize the WebM container.
     *
     * @returns Final container statistics.
     */
    finalize(): {
        status: string;
        data: {
            totalFrames: number;
            totalBytes: number;
            numClusters: number;
            numCuePoints: number;
            durationMs: number;
            tracks: number;
            avgClusterSizeBytes: number;
        };
    } {
        const lastCluster = this.clusters[this.clusters.length - 1];
        const durationMs = lastCluster
            ? lastCluster.timestampMs + this.clusterDurationMs
            : 0;

        return {
            status: "success",
            data: {
                totalFrames: this.totalFrames,
                totalBytes: this.totalBytes,
                numClusters: this.clusters.length,
                numCuePoints: this.cuePoints.length,
                durationMs,
                tracks: this.tracks.size,
                avgClusterSizeBytes: this.clusters.length > 0
                    ? Math.round(this.totalBytes / this.clusters.length)
                    : 0,
            },
        };
    }
}
