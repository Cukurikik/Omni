// ===========================================================================
// OMNI FLOW PIPELINE ENGINE (SEMESTER 3 — BATCH 38.3)
// ===========================================================================
// Absorbed From  : Kotlin Flow + SharedFlow + StateFlow + Channel
// Logic Inherited: Kotlin / UI Mobile Layer (Coroutine-Based Reactive Streams)
// ===========================================================================
//
// By studying Kotlin Coroutines Flow API, Mother learned that Kotlin's
// structured concurrency enables cold & hot stream processing:
//   1. Flow is cold — only executes when collected
//   2. StateFlow holds current value (like BehaviorSubject)
//   3. SharedFlow broadcasts to multiple collectors (like PublishSubject)
//   4. Operators (map, filter, transform) are suspending functions
//   5. flowOn switches the dispatcher (thread pool) for upstream

package omni.ui.flow

import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.channels.*
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong

/**
 * Production-grade Flow pipeline engine implementing Kotlin's
 * structured concurrency patterns for reactive data streams.
 */
class OmniFlowPipelineEngine {

    // ---- Pipeline Step Definition ----

    sealed class PipelineResult<out T> {
        data class Success<T>(val value: T) : PipelineResult<T>()
        data class Error(val message: String) : PipelineResult<Nothing>()

        fun <R> map(transform: (T) -> R): PipelineResult<R> = when (this) {
            is Success -> Success(transform(value))
            is Error -> this
        }

        fun <R> flatMap(transform: (T) -> PipelineResult<R>): PipelineResult<R> = when (this) {
            is Success -> transform(value)
            is Error -> this
        }
    }

    // ---- State Container (StateFlow-inspired) ----

    /**
     * Holds a mutable state value and emits changes to all observers.
     * Thread-safe via Kotlin's MutableStateFlow.
     */
    class OmniStateHolder<T>(initialValue: T) {
        private val _state = MutableStateFlow(initialValue)
        val state: StateFlow<T> = _state.asStateFlow()

        val value: T get() = _state.value

        fun update(newValue: T) {
            _state.value = newValue
        }

        fun update(transform: (T) -> T) {
            _state.update(transform)
        }

        suspend fun collect(collector: suspend (T) -> Unit) {
            _state.collect(collector)
        }
    }

    // ---- Event Bus (SharedFlow-inspired) ----

    /**
     * Broadcasts events to multiple collectors.
     * Events emitted before subscription are buffered up to replay count.
     */
    class OmniEventBus<T>(
        private val replay: Int = 0,
        private val extraBufferCapacity: Int = 64
    ) {
        private val _events = MutableSharedFlow<T>(
            replay = replay,
            extraBufferCapacity = extraBufferCapacity,
            onBufferOverflow = BufferOverflow.DROP_OLDEST
        )
        val events: SharedFlow<T> = _events.asSharedFlow()

        private val totalEmitted = AtomicLong(0)
        private val subscriberCount = AtomicLong(0)

        suspend fun emit(event: T) {
            _events.emit(event)
            totalEmitted.incrementAndGet()
        }

        fun tryEmit(event: T): Boolean {
            val result = _events.tryEmit(event)
            if (result) totalEmitted.incrementAndGet()
            return result
        }

        suspend fun collect(collector: suspend (T) -> Unit) {
            subscriberCount.incrementAndGet()
            try {
                _events.collect(collector)
            } finally {
                subscriberCount.decrementAndGet()
            }
        }

        fun getMetrics(): Map<String, Any> = mapOf(
            "total_emitted" to totalEmitted.get(),
            "subscriber_count" to subscriberCount.get(),
            "replay_cache_size" to _events.replayCache.size
        )
    }

    // ---- Data Pipeline Builder ----

    /**
     * Fluent builder for constructing Flow-based data pipelines.
     * Each step is a suspending transformation applied lazily.
     */
    class Pipeline<T>(private val source: Flow<T>) {
        private var steps = mutableListOf<String>()

        fun filter(name: String = "filter", predicate: suspend (T) -> Boolean): Pipeline<T> {
            steps.add(name)
            return Pipeline(source.filter(predicate))
        }

        fun <R> map(name: String = "map", transform: suspend (T) -> R): Pipeline<R> {
            steps.add(name)
            return Pipeline(source.map(transform))
        }

        fun onEach(name: String = "onEach", action: suspend (T) -> Unit): Pipeline<T> {
            steps.add(name)
            return Pipeline(source.onEach(action))
        }

        fun take(count: Int): Pipeline<T> {
            steps.add("take($count)")
            return Pipeline(source.take(count))
        }

        fun debounce(timeoutMs: Long): Pipeline<T> {
            steps.add("debounce(${timeoutMs}ms)")
            return Pipeline(source.debounce(timeoutMs))
        }

        fun distinctUntilChanged(): Pipeline<T> {
            steps.add("distinctUntilChanged")
            return Pipeline(source.distinctUntilChanged())
        }

        fun buffer(capacity: Int = Channel.BUFFERED): Pipeline<T> {
            steps.add("buffer($capacity)")
            return Pipeline(source.buffer(capacity))
        }

        fun catch(handler: suspend FlowCollector<T>.(Throwable) -> Unit): Pipeline<T> {
            steps.add("catch")
            return Pipeline(source.catch(handler))
        }

        /**
         * Terminal operation: collect all values.
         */
        suspend fun collect(collector: suspend (T) -> Unit) {
            source.collect(collector)
        }

        /**
         * Terminal operation: collect to a list.
         */
        suspend fun toList(): List<T> = source.toList()

        /**
         * Terminal operation: fold/reduce.
         */
        suspend fun <R> fold(initial: R, operation: suspend (R, T) -> R): R =
            source.fold(initial, operation)

        /**
         * Terminal operation: first value.
         */
        suspend fun first(): T = source.first()

        val stepDescriptions: List<String> get() = steps.toList()
    }

    // ---- Engine Core ----

    private val stateHolders = ConcurrentHashMap<String, OmniStateHolder<*>>()
    private val eventBuses = ConcurrentHashMap<String, OmniEventBus<*>>()
    private val totalPipelinesCreated = AtomicLong(0)

    /**
     * Create a new pipeline from a list of values.
     */
    fun <T> pipelineOf(vararg values: T): Pipeline<T> {
        totalPipelinesCreated.incrementAndGet()
        return Pipeline(flowOf(*values))
    }

    /**
     * Create a pipeline from a Flow builder.
     */
    fun <T> pipelineFrom(builder: suspend FlowCollector<T>.() -> Unit): Pipeline<T> {
        totalPipelinesCreated.incrementAndGet()
        return Pipeline(flow(builder))
    }

    /**
     * Create a pipeline that emits integers in a range.
     */
    fun rangeFlow(start: Int, endExclusive: Int): Pipeline<Int> {
        totalPipelinesCreated.incrementAndGet()
        return Pipeline((start until endExclusive).asFlow())
    }

    /**
     * Create or get a named StateHolder.
     */
    @Suppress("UNCHECKED_CAST")
    fun <T> stateHolder(name: String, initialValue: T): OmniStateHolder<T> {
        return stateHolders.getOrPut(name) {
            OmniStateHolder(initialValue)
        } as OmniStateHolder<T>
    }

    /**
     * Create or get a named EventBus.
     */
    @Suppress("UNCHECKED_CAST")
    fun <T> eventBus(name: String, replay: Int = 0): OmniEventBus<T> {
        return eventBuses.getOrPut(name) {
            OmniEventBus<T>(replay = replay)
        } as OmniEventBus<T>
    }

    // ---- Fan-Out / Fan-In Patterns ----

    /**
     * Fan-out: distribute items from a single flow to multiple workers.
     */
    fun <T> fanOut(
        source: Flow<T>,
        workerCount: Int,
        process: suspend (T) -> Unit
    ): Flow<Unit> = flow {
        coroutineScope {
            val channel = source.produceIn(this)
            repeat(workerCount) {
                launch {
                    for (item in channel) {
                        process(item)
                    }
                }
            }
        }
        emit(Unit)
    }

    /**
     * Fan-in: merge multiple flows into one.
     */
    fun <T> fanIn(vararg sources: Flow<T>): Flow<T> = merge(*sources)

    // ---- Diagnostics ----

    fun diagnostics(): Map<String, Any> = mapOf(
        "engine" to "OmniFlowPipelineEngine",
        "layer" to "Kotlin UI Mobile",
        "total_pipelines_created" to totalPipelinesCreated.get(),
        "state_holders" to stateHolders.size,
        "event_buses" to eventBuses.size,
        "event_bus_metrics" to eventBuses.mapValues { (_, bus) ->
            @Suppress("UNCHECKED_CAST")
            (bus as OmniEventBus<*>).getMetrics()
        },
        "learned_logic" to listOf(
            "kotlin-flow-cold-streams",
            "stateflow-current-value-holder",
            "sharedflow-broadcast-events",
            "structured-concurrency-scope",
            "flow-operators-map-filter-debounce",
            "channel-fan-out-distribution",
            "merge-fan-in-combination",
            "buffer-overflow-drop-oldest",
            "suspending-function-composition"
        )
    )
}
