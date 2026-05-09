// OMNI Interface Layer — Kotlin Android Inference SDK
// On-device transformer inference for Android using NNAPI.

package dev.omni.inference

import kotlinx.coroutines.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import kotlin.math.*

data class InferenceConfig(
    val maxTokens: Int = 256,
    val temperature: Float = 0.7f,
    val topP: Float = 0.9f,
    val topK: Int = 50,
    val repetitionPenalty: Float = 1.1f,
)

data class InferenceResult(
    val text: String,
    val tokensGenerated: Int,
    val latencyMs: Long,
    val finishReason: String,
)

sealed class InferenceError : Exception() {
    data object ModelNotLoaded : InferenceError()
    data class LoadFailed(override val message: String) : InferenceError()
    data class InferenceFailed(override val message: String) : InferenceError()
}

class OmniAndroidEngine(private val config: InferenceConfig = InferenceConfig()) {
    private var modelLoaded = false
    private var vocabulary: Map<String, Int> = emptyMap()
    private var reverseVocab: Map<Int, String> = emptyMap()
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    suspend fun loadModel(modelDir: File): Result<Unit> = withContext(Dispatchers.IO) {
        runCatching {
            val vocabFile = File(modelDir, "vocab.json")
            if (!vocabFile.exists()) throw InferenceError.LoadFailed("vocab.json not found")

            // Load vocabulary
            val vocabJson = vocabFile.readText()
            // Production: parse JSON properly
            vocabulary = mapOf("hello" to 1, "world" to 2, "the" to 3, "is" to 4)
            reverseVocab = vocabulary.entries.associate { (k, v) -> v to k }
            modelLoaded = true
        }
    }

    fun isReady(): Boolean = modelLoaded

    suspend fun generate(prompt: String): Result<InferenceResult> = withContext(Dispatchers.Default) {
        runCatching {
            if (!modelLoaded) throw InferenceError.ModelNotLoaded
            val startTime = System.nanoTime()
            val inputIds = tokenize(prompt)
            val generatedIds = mutableListOf<Int>()
            var finishReason = "max_tokens"

            for (step in 0 until config.maxTokens) {
                val logits = forwardPass(inputIds + generatedIds)
                val nextToken = sample(logits)
                if (nextToken == 0) { // EOS
                    finishReason = "stop"
                    break
                }
                generatedIds.add(nextToken)
            }

            val latency = (System.nanoTime() - startTime) / 1_000_000
            InferenceResult(
                text = detokenize(generatedIds),
                tokensGenerated = generatedIds.size,
                latencyMs = latency,
                finishReason = finishReason,
            )
        }
    }

    fun streamGenerate(prompt: String): Flow<String> = flow {
        if (!modelLoaded) throw InferenceError.ModelNotLoaded
        val inputIds = tokenize(prompt)
        val generatedIds = mutableListOf<Int>()

        for (step in 0 until config.maxTokens) {
            val logits = forwardPass(inputIds + generatedIds)
            val nextToken = sample(logits)
            if (nextToken == 0) break
            generatedIds.add(nextToken)
            emit(reverseVocab[nextToken] ?: "")
        }
    }

    private fun tokenize(text: String): List<Int> =
        text.lowercase().split(" ").mapNotNull { vocabulary[it] }

    private fun detokenize(ids: List<Int>): String =
        ids.mapNotNull { reverseVocab[it] }.joinToString(" ")

    private fun forwardPass(inputIds: List<Int>): FloatArray {
        // Production: actual NNAPI/ONNX forward pass
        val vocabSize = maxOf(vocabulary.size, 100)
        return FloatArray(vocabSize) { (Math.random() * 2 - 1).toFloat() }
    }

    private fun sample(logits: FloatArray): Int {
        // Apply temperature
        val scaled = FloatArray(logits.size) { logits[it] / config.temperature }

        // Softmax
        val maxVal = scaled.max()
        val exps = FloatArray(scaled.size) { exp((scaled[it] - maxVal).toDouble()).toFloat() }
        val sum = exps.sum()
        val probs = FloatArray(exps.size) { exps[it] / sum }

        // Top-p sampling
        val indexed = probs.mapIndexed { i, p -> i to p }.sortedByDescending { it.second }
        var cumProb = 0f
        val candidates = mutableListOf<Pair<Int, Float>>()
        for ((idx, prob) in indexed) {
            cumProb += prob
            candidates.add(idx to prob)
            if (cumProb >= config.topP) break
        }

        val total = candidates.sumOf { it.second.toDouble() }.toFloat()
        var r = (Math.random() * total).toFloat()
        for ((idx, prob) in candidates) {
            r -= prob
            if (r <= 0) return idx
        }
        return candidates.lastOrNull()?.first ?: 0
    }

    fun close() {
        scope.cancel()
        modelLoaded = false
    }
}
