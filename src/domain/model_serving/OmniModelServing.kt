// OmniModelServing.kt — Kotlin Model Serving Orchestrator
// Inspired by: KFServing/Triton patterns for OMNI inference
// Layer: Domain / Kotlin
//
// Coroutine-based model serving orchestrator with request routing,
// model warm-up, A/B traffic splitting, and canary deployment.

package omni.domain.serving

import kotlinx.coroutines.*
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.time.Instant
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong
import kotlin.math.roundToInt

enum class ModelStatus {
    LOADING, WARMING_UP, READY, DRAINING, UNLOADED, FAILED
}

enum class RoutingStrategy {
    ROUND_ROBIN, RANDOM, WEIGHTED, CANARY, AB_TEST
}

data class ModelEndpoint(
    val modelId: String,
    val versionId: String,
    val status: ModelStatus,
    val weight: Double = 1.0,
    val warmupComplete: Boolean = false,
    val loadedAt: Instant? = null,
    val totalRequests: AtomicLong = AtomicLong(0),
    val failedRequests: AtomicLong = AtomicLong(0),
    val totalLatencyMs: AtomicLong = AtomicLong(0)
) {
    val avgLatencyMs: Double
        get() {
            val total = totalRequests.get()
            return if (total > 0) totalLatencyMs.get().toDouble() / total else 0.0
        }

    val errorRate: Double
        get() {
            val total = totalRequests.get()
            return if (total > 0) failedRequests.get().toDouble() / total else 0.0
        }
}

data class InferenceRequest(
    val requestId: String = UUID.randomUUID().toString(),
    val modelId: String,
    val input: Map<String, Any>,
    val priority: Int = 0,
    val deadline: Instant = Instant.now().plusSeconds(30),
    val metadata: Map<String, String> = emptyMap()
)

data class InferenceResponse(
    val requestId: String,
    val modelId: String,
    val versionId: String,
    val output: Map<String, Any>,
    val latencyMs: Long,
    val success: Boolean,
    val error: String? = null
)

interface ModelBackend {
    suspend fun load(modelId: String, versionId: String): Boolean
    suspend fun predict(modelId: String, input: Map<String, Any>): Map<String, Any>
    suspend fun unload(modelId: String): Boolean
    suspend fun warmup(modelId: String, sampleInput: Map<String, Any>): Boolean
}

class TrafficRouter(
    private val strategy: RoutingStrategy = RoutingStrategy.WEIGHTED
) {
    private val counter = AtomicLong(0)

    fun selectEndpoint(endpoints: List<ModelEndpoint>): ModelEndpoint? {
        val ready = endpoints.filter { it.status == ModelStatus.READY && it.warmupComplete }
        if (ready.isEmpty()) return null

        return when (strategy) {
            RoutingStrategy.ROUND_ROBIN -> {
                val idx = (counter.getAndIncrement() % ready.size).toInt()
                ready[idx]
            }
            RoutingStrategy.RANDOM -> {
                ready.random()
            }
            RoutingStrategy.WEIGHTED -> {
                selectWeighted(ready)
            }
            RoutingStrategy.CANARY -> {
                // Route 5% to canary (last endpoint), rest to primary
                val canaryRoll = Math.random()
                if (canaryRoll < 0.05 && ready.size > 1) ready.last()
                else ready.first()
            }
            RoutingStrategy.AB_TEST -> {
                // Split traffic based on weights
                selectWeighted(ready)
            }
        }
    }

    private fun selectWeighted(endpoints: List<ModelEndpoint>): ModelEndpoint {
        val totalWeight = endpoints.sumOf { it.weight }
        var roll = Math.random() * totalWeight
        for (endpoint in endpoints) {
            roll -= endpoint.weight
            if (roll <= 0) return endpoint
        }
        return endpoints.last()
    }
}

class OmniModelServing(
    private val backend: ModelBackend,
    private val routingStrategy: RoutingStrategy = RoutingStrategy.WEIGHTED,
    private val maxConcurrency: Int = 64,
    private val warmupBatchSize: Int = 5
) {
    private val endpoints = ConcurrentHashMap<String, MutableList<ModelEndpoint>>()
    private val router = TrafficRouter(routingStrategy)
    private val requestChannel = Channel<Pair<InferenceRequest, CompletableDeferred<InferenceResponse>>>(maxConcurrency)
    private val mutex = Mutex()
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    private val totalServed = AtomicLong(0)
    private val totalErrors = AtomicLong(0)

    fun start() {
        // Start worker pool
        repeat(maxConcurrency) { workerId ->
            scope.launch {
                for ((request, deferred) in requestChannel) {
                    try {
                        val response = processRequest(request)
                        deferred.complete(response)
                    } catch (e: Exception) {
                        deferred.complete(InferenceResponse(
                            requestId = request.requestId,
                            modelId = request.modelId,
                            versionId = "unknown",
                            output = emptyMap(),
                            latencyMs = 0,
                            success = false,
                            error = e.message
                        ))
                    }
                }
            }
        }
    }

    suspend fun loadModel(modelId: String, versionId: String, weight: Double = 1.0): Boolean {
        val loaded = backend.load(modelId, versionId)
        if (!loaded) return false

        val endpoint = ModelEndpoint(
            modelId = modelId,
            versionId = versionId,
            status = ModelStatus.LOADING,
            weight = weight,
            loadedAt = Instant.now()
        )

        mutex.withLock {
            endpoints.getOrPut(modelId) { mutableListOf() }.add(endpoint)
        }

        // Warmup
        scope.launch {
            warmupModel(modelId, endpoint)
        }

        return true
    }

    private suspend fun warmupModel(modelId: String, endpoint: ModelEndpoint) {
        val sampleInput = mapOf("warmup" to true, "batch_size" to 1)

        repeat(warmupBatchSize) {
            try {
                backend.warmup(modelId, sampleInput)
            } catch (_: Exception) {
                // Warmup failures are non-fatal
            }
        }

        mutex.withLock {
            val list = endpoints[modelId] ?: return
            val idx = list.indexOfFirst { it.versionId == endpoint.versionId }
            if (idx >= 0) {
                list[idx] = list[idx].copy(
                    status = ModelStatus.READY,
                    warmupComplete = true
                )
            }
        }
    }

    suspend fun infer(request: InferenceRequest): InferenceResponse {
        val deferred = CompletableDeferred<InferenceResponse>()
        requestChannel.send(Pair(request, deferred))
        return deferred.await()
    }

    private suspend fun processRequest(request: InferenceRequest): InferenceResponse {
        val modelEndpoints = endpoints[request.modelId]
            ?: return errorResponse(request, "Model not found: ${request.modelId}")

        val endpoint = router.selectEndpoint(modelEndpoints)
            ?: return errorResponse(request, "No ready endpoint for: ${request.modelId}")

        val startTime = System.currentTimeMillis()
        return try {
            val output = backend.predict(request.modelId, request.input)
            val latency = System.currentTimeMillis() - startTime

            endpoint.totalRequests.incrementAndGet()
            endpoint.totalLatencyMs.addAndGet(latency)
            totalServed.incrementAndGet()

            InferenceResponse(
                requestId = request.requestId,
                modelId = request.modelId,
                versionId = endpoint.versionId,
                output = output,
                latencyMs = latency,
                success = true
            )
        } catch (e: Exception) {
            val latency = System.currentTimeMillis() - startTime
            endpoint.totalRequests.incrementAndGet()
            endpoint.failedRequests.incrementAndGet()
            totalErrors.incrementAndGet()

            errorResponse(request, e.message ?: "Inference failed", latency)
        }
    }

    private fun errorResponse(
        request: InferenceRequest, error: String, latencyMs: Long = 0
    ) = InferenceResponse(
        requestId = request.requestId,
        modelId = request.modelId,
        versionId = "unknown",
        output = emptyMap(),
        latencyMs = latencyMs,
        success = false,
        error = error
    )

    suspend fun unloadModel(modelId: String, versionId: String): Boolean {
        mutex.withLock {
            val list = endpoints[modelId] ?: return false
            val idx = list.indexOfFirst { it.versionId == versionId }
            if (idx >= 0) {
                list[idx] = list[idx].copy(status = ModelStatus.DRAINING)
            }
        }
        delay(5000) // Drain grace period
        val result = backend.unload(modelId)
        mutex.withLock {
            endpoints[modelId]?.removeIf { it.versionId == versionId }
        }
        return result
    }

    fun stats(): Map<String, Any> = mapOf(
        "total_served" to totalServed.get(),
        "total_errors" to totalErrors.get(),
        "loaded_models" to endpoints.size,
        "endpoints" to endpoints.flatMap { (_, eps) ->
            eps.map { ep ->
                mapOf(
                    "model" to ep.modelId,
                    "version" to ep.versionId,
                    "status" to ep.status.name,
                    "requests" to ep.totalRequests.get(),
                    "avg_latency_ms" to ep.avgLatencyMs.roundToInt(),
                    "error_rate" to String.format("%.4f", ep.errorRate)
                )
            }
        }
    )

    fun shutdown() {
        requestChannel.close()
        scope.cancel()
    }
}
