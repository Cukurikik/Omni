// ===========================================================================
// OMNI COROUTINE SCHEDULER ENGINE (POLYLINGUAL REMEDIATION — BATCH 37.6)
// ===========================================================================
// Absorbed From  : Kotlin coroutines library + Android WorkManager concepts
// Logic Inherited: Kotlin / UI Layer (Structured Concurrency Task Scheduler)
// Domain Layer   : UI Mobile (Kotlin Core)
// ===========================================================================
//
// By studying Kotlin coroutines and Android WorkManager, Mother learned
// that modern mobile task scheduling requires structured concurrency:
//   1. Parent-child coroutine relationships (cancellation propagates)
//   2. CoroutineScope isolation per lifecycle owner
//   3. Dispatcher-based thread pool control (Main, IO, Default)
//   4. Exponential backoff retry with configurable policies
//
// Kotlin's suspend functions + CoroutineScope provide native structured
// concurrency that is superior to manual thread pool management.

package dev.omni.engine.scheduler

import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong
import kotlin.math.min
import kotlin.math.pow

// ---- Enums ----

enum class TaskPriority(val weight: Int) {
    CRITICAL(100),
    HIGH(75),
    NORMAL(50),
    LOW(25),
    BACKGROUND(10)
}

enum class TaskState {
    PENDING,
    RUNNING,
    COMPLETED,
    FAILED,
    CANCELLED,
    RETRYING
}

enum class DispatcherType {
    MAIN,      // UI thread (Android main looper)
    IO,        // Disk/network I/O
    DEFAULT,   // CPU-intensive computation
    UNCONFINED // Immediate, no dispatch
}

// ---- Data Models ----

data class RetryPolicy(
    val maxRetries: Int = 3,
    val baseDelayMs: Long = 1000,
    val maxDelayMs: Long = 30_000,
    val multiplier: Double = 2.0,
    val jitterFactor: Double = 0.25
) {
    /**
     * Compute delay for attempt N using exponential backoff with jitter.
     * Formula: min(baseDelay * multiplier^attempt, maxDelay) * (1 ± jitter)
     */
    fun delayForAttempt(attempt: Int): Long {
        val exponential = baseDelayMs * multiplier.pow(attempt.toDouble())
        val capped = min(exponential, maxDelayMs.toDouble())
        val jitter = capped * jitterFactor * (Math.random() * 2 - 1)
        return (capped + jitter).toLong().coerceAtLeast(0)
    }
}

data class TaskDescriptor(
    val id: String,
    val name: String,
    val priority: TaskPriority = TaskPriority.NORMAL,
    val dispatcher: DispatcherType = DispatcherType.DEFAULT,
    val retryPolicy: RetryPolicy = RetryPolicy(),
    val timeoutMs: Long = 30_000,
    val tags: Set<String> = emptySet()
)

data class TaskResult(
    val taskId: String,
    val state: TaskState,
    val durationMs: Long,
    val attempts: Int,
    val output: Any? = null,
    val error: String? = null
)

// ---- Internal Task Wrapper ----

internal class ManagedTask(
    val descriptor: TaskDescriptor,
    val action: suspend () -> Any?,
    var state: TaskState = TaskState.PENDING,
    var attempts: Int = 0,
    var job: Job? = null,
    val createdAt: Long = System.currentTimeMillis()
)

// ---- Core Engine ----

class OmniCoroutineSchedulerEngine(
    private val parentScope: CoroutineScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
) {
    private val tasks = ConcurrentHashMap<String, ManagedTask>()
    private val results = ConcurrentHashMap<String, TaskResult>()
    private val idGenerator = AtomicLong(0)
    private val stats = SchedulerStats()

    // ---- Task Scheduling ----

    /**
     * Schedule a suspending task for execution.
     * Returns the task ID for tracking.
     */
    fun schedule(
        descriptor: TaskDescriptor,
        action: suspend () -> Any?
    ): String {
        val task = ManagedTask(descriptor, action)
        tasks[descriptor.id] = task
        stats.totalScheduled.incrementAndGet()

        val dispatcher = resolveDispatcher(descriptor.dispatcher)

        task.job = parentScope.launch(dispatcher) {
            executeWithRetry(task)
        }

        return descriptor.id
    }

    /**
     * Schedule with auto-generated ID.
     */
    fun scheduleSimple(
        name: String,
        priority: TaskPriority = TaskPriority.NORMAL,
        action: suspend () -> Any?
    ): String {
        val id = "task-${idGenerator.incrementAndGet()}"
        val descriptor = TaskDescriptor(id = id, name = name, priority = priority)
        return schedule(descriptor, action)
    }

    // ---- Execution with Retry ----

    private suspend fun executeWithRetry(task: ManagedTask) {
        val maxAttempts = task.descriptor.retryPolicy.maxRetries + 1

        for (attempt in 0 until maxAttempts) {
            task.attempts = attempt + 1
            task.state = if (attempt == 0) TaskState.RUNNING else TaskState.RETRYING
            stats.totalExecutions.incrementAndGet()

            try {
                val output = withTimeout(task.descriptor.timeoutMs) {
                    task.action()
                }

                // Success
                task.state = TaskState.COMPLETED
                stats.totalCompleted.incrementAndGet()

                results[task.descriptor.id] = TaskResult(
                    taskId = task.descriptor.id,
                    state = TaskState.COMPLETED,
                    durationMs = System.currentTimeMillis() - task.createdAt,
                    attempts = task.attempts,
                    output = output
                )
                return

            } catch (e: CancellationException) {
                // Cooperative cancellation — do not retry
                task.state = TaskState.CANCELLED
                stats.totalCancelled.incrementAndGet()

                results[task.descriptor.id] = TaskResult(
                    taskId = task.descriptor.id,
                    state = TaskState.CANCELLED,
                    durationMs = System.currentTimeMillis() - task.createdAt,
                    attempts = task.attempts,
                    error = "Cancelled"
                )
                return

            } catch (e: Exception) {
                stats.totalRetries.incrementAndGet()

                if (attempt + 1 >= maxAttempts) {
                    // All retries exhausted
                    task.state = TaskState.FAILED
                    stats.totalFailed.incrementAndGet()

                    results[task.descriptor.id] = TaskResult(
                        taskId = task.descriptor.id,
                        state = TaskState.FAILED,
                        durationMs = System.currentTimeMillis() - task.createdAt,
                        attempts = task.attempts,
                        error = "${e::class.simpleName}: ${e.message}"
                    )
                    return
                }

                // Exponential backoff before retry
                val delay = task.descriptor.retryPolicy.delayForAttempt(attempt)
                delay(delay)
            }
        }
    }

    // ---- Task Management ----

    /**
     * Cancel a specific task by ID.
     */
    fun cancel(taskId: String): Boolean {
        val task = tasks[taskId] ?: return false
        task.job?.cancel()
        return true
    }

    /**
     * Cancel all tasks matching a tag.
     */
    fun cancelByTag(tag: String) {
        tasks.values
            .filter { tag in it.descriptor.tags }
            .forEach { it.job?.cancel() }
    }

    /**
     * Cancel all tasks.
     */
    fun cancelAll() {
        tasks.values.forEach { it.job?.cancel() }
    }

    // ---- Query ----

    fun getTaskState(taskId: String): TaskState? = tasks[taskId]?.state

    fun getResult(taskId: String): TaskResult? = results[taskId]

    fun getPendingCount(): Int = tasks.values.count {
        it.state == TaskState.PENDING || it.state == TaskState.RUNNING || it.state == TaskState.RETRYING
    }

    fun getCompletedResults(): List<TaskResult> =
        results.values.filter { it.state == TaskState.COMPLETED }.toList()

    fun getFailedResults(): List<TaskResult> =
        results.values.filter { it.state == TaskState.FAILED }.toList()

    // ---- Dispatcher Resolution ----

    private fun resolveDispatcher(type: DispatcherType): CoroutineDispatcher = when (type) {
        DispatcherType.MAIN -> Dispatchers.Main
        DispatcherType.IO -> Dispatchers.IO
        DispatcherType.DEFAULT -> Dispatchers.Default
        DispatcherType.UNCONFINED -> Dispatchers.Unconfined
    }

    // ---- Lifecycle ----

    /**
     * Gracefully shutdown the scheduler.
     * Waits for all running tasks to complete or cancel.
     */
    suspend fun shutdown() {
        parentScope.coroutineContext[Job]?.cancelAndJoin()
    }

    // ---- Diagnostics ----

    fun diagnostics(): Map<String, Any> = mapOf(
        "engine" to "OmniCoroutineSchedulerEngine",
        "layer" to "Kotlin UI Mobile",
        "total_tasks" to tasks.size,
        "pending" to getPendingCount(),
        "completed" to stats.totalCompleted.get(),
        "failed" to stats.totalFailed.get(),
        "cancelled" to stats.totalCancelled.get(),
        "total_retries" to stats.totalRetries.get(),
        "total_executions" to stats.totalExecutions.get(),
        "results_cached" to results.size,
        "learned_logic" to listOf(
            "structured-concurrency-parent-child",
            "supervisor-job-isolation",
            "exponential-backoff-with-jitter",
            "coroutine-dispatcher-thread-pool",
            "with-timeout-cancellation",
            "concurrent-hashmap-thread-safety",
            "cooperative-cancellation-exception"
        )
    )
}

// ---- Stats ----

internal class SchedulerStats {
    val totalScheduled = AtomicLong(0)
    val totalExecutions = AtomicLong(0)
    val totalCompleted = AtomicLong(0)
    val totalFailed = AtomicLong(0)
    val totalCancelled = AtomicLong(0)
    val totalRetries = AtomicLong(0)
}
