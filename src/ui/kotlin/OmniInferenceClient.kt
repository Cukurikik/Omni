// OMNI Interface — Kotlin Android Inference Client
// Material 3 UI with coroutine-based inference API.

package dev.omni.android.inference

import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import java.net.HttpURLConnection
import java.net.URL
import org.json.JSONObject

data class InferenceConfig(
    val baseUrl: String = "http://10.0.2.2:8080/api/v1",
    val maxTokens: Int = 256,
    val temperature: Float = 0.7f,
    val timeoutMs: Int = 30000
)

data class InferenceResult(
    val text: String,
    val tokens: Int,
    val latencyMs: Long,
    val requestId: String
)

sealed class InferenceState {
    data object Idle : InferenceState()
    data object Loading : InferenceState()
    data class Success(val result: InferenceResult) : InferenceState()
    data class Error(val message: String) : InferenceState()
}

class OmniInferenceClient(private val config: InferenceConfig) {
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private val _state = MutableStateFlow<InferenceState>(InferenceState.Idle)
    val state: StateFlow<InferenceState> = _state.asStateFlow()

    private var totalRequests = 0L
    private var totalLatency = 0L
    private var errorCount = 0L

    suspend fun infer(prompt: String): InferenceResult = withContext(Dispatchers.IO) {
        _state.value = InferenceState.Loading
        val start = System.currentTimeMillis()
        totalRequests++

        try {
            val url = URL("${config.baseUrl}/infer")
            val conn = (url.openConnection() as HttpURLConnection).apply {
                requestMethod = "POST"
                setRequestProperty("Content-Type", "application/json")
                connectTimeout = config.timeoutMs
                readTimeout = config.timeoutMs
                doOutput = true
            }

            val body = JSONObject().apply {
                put("prompt", prompt)
                put("max_tokens", config.maxTokens)
                put("temperature", config.temperature.toDouble())
            }

            conn.outputStream.use { it.write(body.toString().toByteArray()) }

            val response = conn.inputStream.bufferedReader().readText()
            val json = JSONObject(response)
            val latency = System.currentTimeMillis() - start
            totalLatency += latency

            val result = InferenceResult(
                text = json.optString("generated_text", ""),
                tokens = json.optInt("tokens_generated", 0),
                latencyMs = latency,
                requestId = json.optString("request_id", "")
            )

            _state.value = InferenceState.Success(result)
            conn.disconnect()
            result
        } catch (e: Exception) {
            errorCount++
            val error = InferenceState.Error(e.message ?: "Unknown error")
            _state.value = error
            throw e
        }
    }

    fun inferAsync(prompt: String, callback: (Result<InferenceResult>) -> Unit) {
        scope.launch {
            try {
                val result = infer(prompt)
                withContext(Dispatchers.Main) { callback(Result.success(result)) }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) { callback(Result.failure(e)) }
            }
        }
    }

    fun getStats(): Map<String, Any> = mapOf(
        "total_requests" to totalRequests,
        "avg_latency_ms" to if (totalRequests > 0) totalLatency / totalRequests else 0L,
        "error_count" to errorCount
    )

    fun shutdown() { scope.cancel() }
}
