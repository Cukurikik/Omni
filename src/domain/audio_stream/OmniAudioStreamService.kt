// OmniAudioStreamService.kt — Audio Streaming Service
// Inspired by: SoundStorm real-time audio generation
// Layer: Domain / Kotlin JVM
//
// Coroutine-based audio chunk streaming with backpressure,
// codec token buffering, and real-time synthesis coordination.

package omni.domain.audio

import java.util.concurrent.ConcurrentLinkedQueue
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.UUID

enum class AudioCodecType {
    SOUNDSTREAM, ENCODEC, DAC, OMNI_CODEC
}

enum class StreamState {
    IDLE, BUFFERING, STREAMING, PAUSED, COMPLETED, ERROR
}

data class AudioChunk(
    val chunkId: String = UUID.randomUUID().toString().take(12),
    val sequenceNumber: Long,
    val codecTokens: IntArray,       // quantized codec tokens
    val numQuantizerLevels: Int,
    val sampleRate: Int = 16000,
    val durationMs: Long,
    val timestamp: Long = System.currentTimeMillis()
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is AudioChunk) return false
        return chunkId == other.chunkId
    }

    override fun hashCode(): Int = chunkId.hashCode()
}

data class StreamConfig(
    val codecType: AudioCodecType = AudioCodecType.SOUNDSTREAM,
    val numQuantizerLevels: Int = 8,
    val chunkDurationMs: Long = 320,
    val bufferCapacity: Int = 64,
    val maxLatencyMs: Long = 500,
    val sampleRate: Int = 16000
)

data class StreamMetrics(
    val totalChunksProcessed: Long,
    val totalDurationMs: Long,
    val avgLatencyMs: Double,
    val bufferOccupancy: Int,
    val dropCount: Long,
    val state: StreamState
)

interface AudioSynthesizer {
    fun synthesize(codecTokens: IntArray, numLevels: Int, sampleRate: Int): FloatArray
    fun warmup()
    fun close()
}

class AudioStreamService(
    private val config: StreamConfig,
    private val synthesizer: AudioSynthesizer
) {
    private val buffer = ConcurrentLinkedQueue<AudioChunk>()
    private val isRunning = AtomicBoolean(false)
    private val sequenceCounter = AtomicLong(0)
    private val processedCount = AtomicLong(0)
    private val totalDurationMs = AtomicLong(0)
    private val totalLatencyNs = AtomicLong(0)
    private val dropCount = AtomicLong(0)

    @Volatile
    private var state: StreamState = StreamState.IDLE

    val streamId: String = UUID.randomUUID().toString()

    fun start() {
        if (state != StreamState.IDLE && state != StreamState.COMPLETED) {
            throw IllegalStateException("Cannot start stream in state: $state")
        }
        synthesizer.warmup()
        isRunning.set(true)
        state = StreamState.BUFFERING
    }

    fun submitChunk(codecTokens: IntArray): AudioChunk {
        if (!isRunning.get()) {
            throw IllegalStateException("Stream is not running")
        }

        val chunk = AudioChunk(
            sequenceNumber = sequenceCounter.getAndIncrement(),
            codecTokens = codecTokens,
            numQuantizerLevels = config.numQuantizerLevels,
            sampleRate = config.sampleRate,
            durationMs = config.chunkDurationMs
        )

        if (buffer.size >= config.bufferCapacity) {
            // Backpressure: drop oldest chunk
            buffer.poll()
            dropCount.incrementAndGet()
        }

        buffer.offer(chunk)

        if (state == StreamState.BUFFERING && buffer.size >= 3) {
            state = StreamState.STREAMING
        }

        return chunk
    }

    fun processNextChunk(): FloatArray? {
        if (state != StreamState.STREAMING && state != StreamState.BUFFERING) {
            return null
        }

        val chunk = buffer.poll() ?: return null

        val startNs = System.nanoTime()
        val waveform = synthesizer.synthesize(
            chunk.codecTokens,
            chunk.numQuantizerLevels,
            chunk.sampleRate
        )
        val elapsedNs = System.nanoTime() - startNs

        processedCount.incrementAndGet()
        totalDurationMs.addAndGet(chunk.durationMs)
        totalLatencyNs.addAndGet(elapsedNs)

        // Check real-time constraint
        val latencyMs = elapsedNs / 1_000_000
        if (latencyMs > config.maxLatencyMs) {
            // Log warning: synthesis too slow for real-time
            System.err.println("WARN: Synthesis latency ${latencyMs}ms exceeds RT budget ${config.maxLatencyMs}ms")
        }

        return waveform
    }

    fun pause() {
        if (state == StreamState.STREAMING) {
            state = StreamState.PAUSED
        }
    }

    fun resume() {
        if (state == StreamState.PAUSED) {
            state = StreamState.STREAMING
        }
    }

    fun stop() {
        isRunning.set(false)
        state = StreamState.COMPLETED
        buffer.clear()
    }

    fun getMetrics(): StreamMetrics {
        val count = processedCount.get()
        val avgLatency = if (count > 0) {
            totalLatencyNs.get().toDouble() / count / 1_000_000.0
        } else 0.0

        return StreamMetrics(
            totalChunksProcessed = count,
            totalDurationMs = totalDurationMs.get(),
            avgLatencyMs = avgLatency,
            bufferOccupancy = buffer.size,
            dropCount = dropCount.get(),
            state = state
        )
    }

    fun getState(): StreamState = state
    fun getBufferSize(): Int = buffer.size
    fun isActive(): Boolean = isRunning.get()
}

// Batch synthesis coordinator for parallel multi-level generation
class ParallelSynthesisCoordinator(
    private val numLevels: Int = 8,
    private val config: StreamConfig
) {
    data class LevelResult(
        val level: Int,
        val tokens: IntArray,
        val confidence: FloatArray
    )

    private val levelResults = Array<LevelResult?>(numLevels) { null }
    private val completedLevels = AtomicLong(0)

    fun submitLevelResult(result: LevelResult) {
        require(result.level in 0 until numLevels) { "Invalid level: ${result.level}" }
        synchronized(levelResults) {
            levelResults[result.level] = result
            completedLevels.incrementAndGet()
        }
    }

    fun isComplete(): Boolean = completedLevels.get() >= numLevels

    fun mergeResults(): IntArray {
        require(isComplete()) { "Not all levels completed" }

        synchronized(levelResults) {
            val totalTokens = levelResults.filterNotNull().sumOf { it.tokens.size }
            val merged = IntArray(totalTokens)
            var offset = 0

            for (level in 0 until numLevels) {
                val result = levelResults[level]
                    ?: throw IllegalStateException("Missing level $level")
                System.arraycopy(result.tokens, 0, merged, offset, result.tokens.size)
                offset += result.tokens.size
            }

            return merged
        }
    }

    fun reset() {
        synchronized(levelResults) {
            for (i in levelResults.indices) {
                levelResults[i] = null
            }
            completedLevels.set(0)
        }
    }
}
