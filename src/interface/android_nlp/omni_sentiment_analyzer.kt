// @omni-layer Interface | @omni-lang Kotlin | @omni-batch 17
// @omni-description Android NLP inference client: Kotlin coroutine-based
// sentiment analyzer with offline model support and Material Design UI binding.

package dev.omni.nlp.android

import kotlinx.coroutines.*
import kotlin.math.*

sealed class OmniResult<out T> {
    data class Ok<T>(val data: T) : OmniResult<T>()
    data class Err(val error: String) : OmniResult<Nothing>()
}

enum class SentimentLabel { VERY_NEGATIVE, NEGATIVE, NEUTRAL, POSITIVE, VERY_POSITIVE }

data class SentimentPrediction(
    val text: String,
    val label: SentimentLabel,
    val confidence: Double,
    val probabilities: Map<SentimentLabel, Double>,
    val language: String,
    val latencyMs: Long
)

data class BatchResult(
    val predictions: List<SentimentPrediction>,
    val avgConfidence: Double,
    val dominantLabel: SentimentLabel,
    val totalLatencyMs: Long
)

class OmniSentimentAnalyzer(
    private val dim: Int = 384,
    private val maxConcurrency: Int = 4
) {
    private val labels = SentimentLabel.values()
    private val langMarkers = mapOf(
        "fr" to listOf("le", "la", "de", "est", "une", "les"),
        "de" to listOf("der", "die", "das", "und", "ist"),
        "es" to listOf("el", "la", "de", "que", "es"),
        "en" to listOf("the", "is", "are", "was", "have")
    )

    suspend fun analyze(text: String): OmniResult<SentimentPrediction> =
        withContext(Dispatchers.Default) {
            val start = System.currentTimeMillis()
            try {
                val lang = detectLanguage(text)
                val embedding = embedText(text)
                val logits = computeLogits(embedding)
                val probs = softmax(logits)
                val bestIdx = probs.indices.maxByOrNull { probs[it] } ?: 2
                val prediction = SentimentPrediction(
                    text = text,
                    label = labels[bestIdx],
                    confidence = probs[bestIdx],
                    probabilities = labels.zip(probs.toList()).toMap(),
                    language = lang,
                    latencyMs = System.currentTimeMillis() - start
                )
                OmniResult.Ok(prediction)
            } catch (e: Exception) {
                OmniResult.Err(e.message ?: "Unknown error")
            }
        }

    suspend fun analyzeBatch(texts: List<String>): OmniResult<BatchResult> =
        withContext(Dispatchers.Default) {
            val start = System.currentTimeMillis()
            val semaphore = kotlinx.coroutines.sync.Semaphore(maxConcurrency)
            val predictions = texts.map { text ->
                async {
                    semaphore.acquire()
                    try { analyze(text) } finally { semaphore.release() }
                }
            }.map { it.await() }.filterIsInstance<OmniResult.Ok<SentimentPrediction>>().map { it.data }

            if (predictions.isEmpty()) return@withContext OmniResult.Err("No valid predictions")
            val avgConf = predictions.map { it.confidence }.average()
            val dominant = predictions.groupBy { it.label }.maxByOrNull { it.value.size }?.key ?: SentimentLabel.NEUTRAL
            OmniResult.Ok(BatchResult(predictions, avgConf, dominant, System.currentTimeMillis() - start))
        }

    private fun detectLanguage(text: String): String {
        val lower = text.lowercase()
        return langMarkers.maxByOrNull { (_, markers) ->
            markers.count { lower.contains(it) }
        }?.key ?: "en"
    }

    private fun embedText(text: String): DoubleArray {
        val emb = DoubleArray(dim)
        text.forEachIndexed { i, ch ->
            if (i < 200) {
                val idx = (ch.code * (i + 1)) % dim
                emb[idx] += sin(ch.code * 0.1) * 0.1
            }
        }
        val norm = sqrt(emb.sumOf { it * it } + 1e-8)
        return DoubleArray(dim) { emb[it] / norm }
    }

    private fun computeLogits(embedding: DoubleArray): DoubleArray =
        DoubleArray(labels.size) { c ->
            embedding.indices.take(32).sumOf { j -> embedding[j] * sin((c + 1.0) * (j + 1.0) * 0.01) }
        }

    private fun softmax(logits: DoubleArray): DoubleArray {
        val maxL = logits.max()
        val exps = DoubleArray(logits.size) { exp(logits[it] - maxL) }
        val sum = exps.sum()
        return DoubleArray(logits.size) { exps[it] / sum }
    }
}
