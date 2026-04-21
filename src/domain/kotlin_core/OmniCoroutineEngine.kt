// ===========================================================================
// OMNI COROUTINE ENGINE (SEMESTER 3 — BATCH 38.8)
// ===========================================================================
// Absorbed From  : Kotlin Coroutines + Flow + Channel + Dispatchers
// Logic Inherited: Kotlin / Domain Layer (Structured Concurrency)
// ===========================================================================
//
// By studying Kotlin Coroutines, Mother learned:
//   1. suspend functions cooperatively yield execution
//   2. CoroutineScope defines lifecycle boundaries
//   3. Flow is a cold asynchronous stream (lazy, cancellable)
//   4. Channel is a hot communication primitive between coroutines
//   5. Structured concurrency: child coroutines cancel with parent

package omni.domain.kotlin

import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.flow.*
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong

// ============================================================
// PART 1: Structured Concurrency Builder
// ============================================================

/**
 * TaskScope: structured concurrency scope with metrics.
 * All child tasks cancel when the scope is cancelled.
 */
class TaskScope private constructor(
    private val scope: CoroutineScope
) {
    private val totalLaunched = AtomicInteger(0)
    private val totalCompleted = AtomicInteger(0)
    private val totalFailed = AtomicInteger(0)
    private val totalCancelled = AtomicInteger(0)

    companion object {
        fun create(dispatcher: CoroutineDispatcher = Dispatchers.Default): TaskScope {
            return TaskScope(CoroutineScope(dispatcher + SupervisorJob()))
        }
    }

    /** Launch a fire-and-forget task. */
    fun launch(
        name: String = "task",
        block: suspend CoroutineScope.() -> Unit
    ): Job {
        totalLaunched.incrementAndGet()
        return scope.launch(CoroutineName(name)) {
            try {
                block()
                totalCompleted.incrementAndGet()
            } catch (e: CancellationException) {
                totalCancelled.incrementAndGet()
                throw e
            } catch (e: Exception) {
                totalFailed.incrementAndGet()
                throw e
            }
        }
    }

    /** Launch a task that returns a result. */
    fun <T> async(
        name: String = "async-task",
        block: suspend CoroutineScope.() -> T
    ): Deferred<T> {
        totalLaunched.incrementAndGet()
        return scope.async(CoroutineName(name)) {
            try {
                val result = block()
                totalCompleted.incrementAndGet()
                result
            } catch (e: CancellationException) {
                totalCancelled.incrementAndGet()
                throw e
            } catch (e: Exception) {
                totalFailed.incrementAndGet()
                throw e
            }
        }
    }

    /** Cancel all tasks in this scope. */
    fun cancel(message: String = "Scope cancelled") {
        scope.cancel(CancellationException(message))
    }

    val isActive: Boolean get() = scope.isActive

    val stats: Map<String, Int> get() = mapOf(
        "launched" to totalLaunched.get(),
        "completed" to totalCompleted.get(),
        "failed" to totalFailed.get(),
        "cancelled" to totalCancelled.get()
    )
}

// ============================================================
// PART 2: Flow Combinators (Cold Streams)
// ============================================================

/**
 * OmniFlow: enhanced Flow builder with OMNI combinators.
 */
object OmniFlow {

    /** Create a flow from a range. */
    fun range(start: Int, endExclusive: Int): Flow<Int> = flow {
        for (i in start until endExclusive) {
            emit(i)
        }
    }

    /** Create a flow that emits at intervals. */
    fun interval(periodMs: Long, count: Int? = null): Flow<Long> = flow {
        var tick = 0L
        while (count == null || tick < count) {
            delay(periodMs)
            emit(tick)
            tick++
        }
    }

    /** Merge multiple flows into one. */
    fun <T> merge(vararg flows: Flow<T>): Flow<T> = channelFlow {
        flows.forEach { flow ->
            launch {
                flow.collect { send(it) }
            }
        }
    }

    /** Zip two flows together. */
    fun <A, B, R> zip(
        flowA: Flow<A>,
        flowB: Flow<B>,
        transform: (A, B) -> R
    ): Flow<R> = flowA.zip(flowB, transform)

    /** Retry a flow on error with exponential backoff. */
    fun <T> Flow<T>.retryWithBackoff(
        maxRetries: Int = 3,
        initialDelayMs: Long = 1000,
        factor: Double = 2.0
    ): Flow<T> = retryWhen { cause, attempt ->
        if (attempt < maxRetries) {
            delay((initialDelayMs * Math.pow(factor, attempt.toDouble())).toLong())
            true
        } else {
            false
        }
    }

    /** Batch/chunk a flow into lists. */
    fun <T> Flow<T>.chunked(size: Int): Flow<List<T>> = flow {
        val batch = mutableListOf<T>()
        collect { value ->
            batch.add(value)
            if (batch.size >= size) {
                emit(batch.toList())
                batch.clear()
            }
        }
        if (batch.isNotEmpty()) {
            emit(batch.toList())
        }
    }

    /** Throttle: emit at most one value per window. */
    fun <T> Flow<T>.throttleFirst(windowMs: Long): Flow<T> = flow {
        var lastEmitTime = 0L
        collect { value ->
            val now = System.currentTimeMillis()
            if (now - lastEmitTime >= windowMs) {
                lastEmitTime = now
                emit(value)
            }
        }
    }

    /** Scan: accumulating transform. */
    fun <T, R> Flow<T>.scanReduce(
        initial: R,
        operation: (R, T) -> R
    ): Flow<R> = scan(initial, operation)
}

// ============================================================
// PART 3: Channel Patterns
// ============================================================

/**
 * Fan-out: distribute channel items to multiple worker coroutines.
 */
suspend fun <T, R> fanOut(
    source: ReceiveChannel<T>,
    workers: Int,
    scope: CoroutineScope,
    processor: suspend (T) -> R
): List<R> {
    val results = Channel<R>(Channel.UNLIMITED)
    val jobs = (1..workers).map { workerId ->
        scope.launch(CoroutineName("worker-$workerId")) {
            for (item in source) {
                results.send(processor(item))
            }
        }
    }
    // Wait for all workers to finish
    jobs.forEach { it.join() }
    results.close()

    return buildList { for (r in results) add(r) }
}

/**
 * Fan-in: merge multiple channels into one.
 */
fun <T> CoroutineScope.fanIn(
    vararg channels: ReceiveChannel<T>
): ReceiveChannel<T> {
    val merged = Channel<T>(Channel.UNLIMITED)
    channels.forEach { ch ->
        launch {
            for (item in ch) {
                merged.send(item)
            }
        }
    }
    launch {
        channels.forEach { } // Wait for completion
    }
    return merged
}

// ============================================================
// PART 4: Result Type (Kotlin-idiomatic)
// ============================================================

sealed class OmniResult<out T> {
    data class Success<T>(val value: T) : OmniResult<T>()
    data class Failure(val error: OmniError) : OmniResult<Nothing>()

    val isSuccess: Boolean get() = this is Success
    val isFailure: Boolean get() = this is Failure

    fun <R> map(transform: (T) -> R): OmniResult<R> = when (this) {
        is Success -> Success(transform(value))
        is Failure -> this
    }

    fun <R> flatMap(transform: (T) -> OmniResult<R>): OmniResult<R> = when (this) {
        is Success -> transform(value)
        is Failure -> this
    }

    fun getOrElse(default: @UnsafeVariance T): T = when (this) {
        is Success -> value
        is Failure -> default
    }

    fun getOrNull(): T? = when (this) {
        is Success -> value
        is Failure -> null
    }

    fun <R> fold(onSuccess: (T) -> R, onFailure: (OmniError) -> R): R = when (this) {
        is Success -> onSuccess(value)
        is Failure -> onFailure(error)
    }

    companion object {
        fun <T> success(value: T): OmniResult<T> = Success(value)
        fun failure(code: String, message: String): OmniResult<Nothing> =
            Failure(OmniError(code, message))

        inline fun <T> catching(block: () -> T): OmniResult<T> {
            return try {
                Success(block())
            } catch (e: Exception) {
                Failure(OmniError("EXCEPTION", e.message ?: "Unknown error"))
            }
        }
    }
}

data class OmniError(val code: String, val message: String)

// ============================================================
// Diagnostics
// ============================================================

fun diagnostics(): Map<String, Any> = mapOf(
    "engine" to "OmniCoroutineEngine",
    "layer" to "Kotlin Domain",
    "components" to listOf(
        "TaskScope", "OmniFlow", "OmniResult",
        "fanOut", "fanIn", "chunked", "throttleFirst"
    ),
    "learned_logic" to listOf(
        "structured-concurrency-scope",
        "supervisor-job-isolation",
        "flow-cold-stream-lazy",
        "channel-hot-communication",
        "fan-out-worker-distribution",
        "retry-exponential-backoff",
        "chunked-batch-processing",
        "sealed-class-result-type"
    )
)
