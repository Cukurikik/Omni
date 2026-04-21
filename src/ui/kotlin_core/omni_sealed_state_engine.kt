// ===========================================================================
// OMNI SEALED STATE ENGINE (SEMESTER 3 — BATCH 38.3)
// ===========================================================================
// Absorbed From  : MVI + Redux + Kotlin sealed class state management
// Logic Inherited: Kotlin / UI Mobile Layer (Unidirectional Data Flow)
// ===========================================================================

package omni.ui.state

import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.atomic.AtomicLong

/**
 * Model-View-Intent (MVI) state engine using Kotlin sealed classes
 * for exhaustive, type-safe state representation.
 */
class OmniSealedStateEngine<State, Intent, Effect>(
    private val initialState: State,
    private val reducer: (State, Intent) -> ReducerResult<State, Effect>
) {

    // ---- Reducer Result (State + Optional Side Effects) ----

    data class ReducerResult<State, Effect>(
        val newState: State,
        val effects: List<Effect> = emptyList()
    )

    // ---- State Store ----

    @Volatile
    private var _state: State = initialState
    val state: State get() = _state

    private val stateHistory = mutableListOf(initialState)
    private val intentLog = mutableListOf<Intent>()
    private val stateListeners = CopyOnWriteArrayList<(State) -> Unit>()
    private val effectHandlers = CopyOnWriteArrayList<(Effect) -> Unit>()

    // Metrics
    private val totalIntentsProcessed = AtomicLong(0)
    private val totalStateTransitions = AtomicLong(0)
    private val totalEffectsEmitted = AtomicLong(0)

    /**
     * Dispatch an intent to the reducer.
     * Pure function: (currentState, intent) → (newState, effects)
     */
    fun dispatch(intent: Intent) {
        intentLog.add(intent)
        totalIntentsProcessed.incrementAndGet()

        val result = reducer(_state, intent)

        if (result.newState != _state) {
            _state = result.newState
            stateHistory.add(_state)
            totalStateTransitions.incrementAndGet()

            // Notify state observers
            stateListeners.forEach { it(_state) }
        }

        // Execute side effects
        for (effect in result.effects) {
            totalEffectsEmitted.incrementAndGet()
            effectHandlers.forEach { it(effect) }
        }
    }

    /**
     * Subscribe to state changes.
     */
    fun observeState(listener: (State) -> Unit) {
        stateListeners.add(listener)
        listener(_state) // Emit current state immediately
    }

    /**
     * Subscribe to side effects.
     */
    fun handleEffects(handler: (Effect) -> Unit) {
        effectHandlers.add(handler)
    }

    // ---- Time Travel Debugging ----

    /**
     * Get state at a specific point in history.
     */
    fun stateAt(index: Int): State? {
        return stateHistory.getOrNull(index)
    }

    /**
     * Undo: revert to previous state.
     */
    fun undo(): Boolean {
        if (stateHistory.size <= 1) return false
        stateHistory.removeAt(stateHistory.lastIndex)
        _state = stateHistory.last()
        stateListeners.forEach { it(_state) }
        return true
    }

    /**
     * Get the full intent log (for replay/debugging).
     */
    fun getIntentLog(): List<Intent> = intentLog.toList()

    /**
     * Get state history length.
     */
    val historySize: Int get() = stateHistory.size

    // ---- Diagnostics ----

    fun diagnostics(): Map<String, Any> = mapOf(
        "engine" to "OmniSealedStateEngine",
        "layer" to "Kotlin UI Mobile",
        "current_state" to (_state?.toString() ?: "null"),
        "history_size" to stateHistory.size,
        "intent_log_size" to intentLog.size,
        "state_listeners" to stateListeners.size,
        "effect_handlers" to effectHandlers.size,
        "total_intents_processed" to totalIntentsProcessed.get(),
        "total_state_transitions" to totalStateTransitions.get(),
        "total_effects_emitted" to totalEffectsEmitted.get(),
        "learned_logic" to listOf(
            "mvi-model-view-intent",
            "sealed-class-exhaustive-state",
            "unidirectional-data-flow",
            "pure-reducer-function",
            "side-effect-separation",
            "time-travel-debugging",
            "copy-on-write-thread-safe-listeners",
            "volatile-state-visibility"
        )
    )
}

/**
 * Convenience builder for creating MVI stores.
 */
object OmniMviStore {
    fun <S, I, E> create(
        initialState: S,
        reducer: (S, I) -> OmniSealedStateEngine.ReducerResult<S, E>
    ): OmniSealedStateEngine<S, I, E> {
        return OmniSealedStateEngine(initialState, reducer)
    }
}
