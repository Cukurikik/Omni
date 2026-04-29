// ===========================================================================
// OMNI DEPENDENCY CONTAINER ENGINE (SEMESTER 3 — BATCH 38.3)
// ===========================================================================
// Absorbed From  : Koin + Hilt/Dagger + Kodein DI patterns
// Logic Inherited: Kotlin / UI Mobile Layer (Compile-Safe DI Container)
// ===========================================================================

package omni.ui.di

import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong

/**
 * Lightweight dependency injection container inspired by Koin.
 * Uses reified generics for type-safe resolution without reflection.
 */
class OmniDependencyContainerEngine {

    // ---- Sealed Result ----
    sealed class DIResult<out T> {
        data class Ok<T>(val value: T) : DIResult<T>()
        data class Err(val message: String) : DIResult<Nothing>()

        fun <R> map(transform: (T) -> R): DIResult<R> = when (this) {
            is Ok -> Ok(transform(value))
            is Err -> this
        }
    }

    // ---- Binding Types ----
    enum class Scope { SINGLETON, FACTORY, SCOPED }

    data class Binding<T>(
        val key: String,
        val scope: Scope,
        val factory: () -> T,
        val qualifier: String? = null
    )

    // ---- Container Module (DSL for registration) ----
    class Module(val name: String) {
        internal val bindings = mutableListOf<Binding<*>>()

        inline fun <reified T : Any> single(
            qualifier: String? = null,
            noinline factory: () -> T
        ) {
            bindings.add(Binding(
                key = T::class.qualifiedName ?: T::class.java.name,
                scope = Scope.SINGLETON,
                factory = factory,
                qualifier = qualifier
            ))
        }

        inline fun <reified T : Any> factory(
            qualifier: String? = null,
            noinline factory: () -> T
        ) {
            bindings.add(Binding(
                key = T::class.qualifiedName ?: T::class.java.name,
                scope = Scope.FACTORY,
                factory = factory,
                qualifier = qualifier
            ))
        }

        inline fun <reified T : Any> scoped(
            qualifier: String? = null,
            noinline factory: () -> T
        ) {
            bindings.add(Binding(
                key = T::class.qualifiedName ?: T::class.java.name,
                scope = Scope.SCOPED,
                factory = factory,
                qualifier = qualifier
            ))
        }
    }

    // ---- Scope Instance ----
    class ScopeInstance(val id: String) {
        internal val instances = ConcurrentHashMap<String, Any>()
        var isActive: Boolean = true
            private set

        fun close() {
            isActive = false
            instances.clear()
        }
    }

    // ---- Container Core ----

    private val registry = ConcurrentHashMap<String, Binding<*>>()
    private val singletons = ConcurrentHashMap<String, Any>()
    private val scopes = ConcurrentHashMap<String, ScopeInstance>()
    private val modules = mutableListOf<Module>()

    // Metrics
    private val totalResolutions = AtomicLong(0)
    private val totalSingletonHits = AtomicLong(0)
    private val totalFactoryCreations = AtomicLong(0)
    private val totalScopedCreations = AtomicLong(0)

    /**
     * Load a module into the container.
     */
    fun loadModule(module: Module) {
        modules.add(module)
        for (binding in module.bindings) {
            val key = buildKey(binding.key, binding.qualifier)
            registry[key] = binding
        }
    }

    /**
     * Load multiple modules.
     */
    fun loadModules(vararg modulesToLoad: Module) {
        modulesToLoad.forEach { loadModule(it) }
    }

    /**
     * Resolve a dependency by type (and optional qualifier).
     */
    @Suppress("UNCHECKED_CAST")
    inline fun <reified T : Any> resolve(qualifier: String? = null): DIResult<T> {
        val typeName = T::class.qualifiedName ?: T::class.java.name
        return resolveByKey(typeName, qualifier) as DIResult<T>
    }

    /**
     * Internal resolution by string key.
     */
    @Suppress("UNCHECKED_CAST")
    fun <T> resolveByKey(typeName: String, qualifier: String? = null): DIResult<T> {
        totalResolutions.incrementAndGet()

        val key = buildKey(typeName, qualifier)
        val binding = registry[key] as? Binding<T>
            ?: return DIResult.Err("No binding found for: $key")

        return when (binding.scope) {
            Scope.SINGLETON -> {
                val instance = singletons.getOrPut(key) {
                    binding.factory()!!
                }
                totalSingletonHits.incrementAndGet()
                DIResult.Ok(instance as T)
            }

            Scope.FACTORY -> {
                totalFactoryCreations.incrementAndGet()
                DIResult.Ok(binding.factory())
            }

            Scope.SCOPED -> {
                DIResult.Err("Scoped resolution requires a scope ID. Use resolveScoped().")
            }
        }
    }

    /**
     * Resolve within a specific scope.
     */
    @Suppress("UNCHECKED_CAST")
    inline fun <reified T : Any> resolveScoped(
        scopeId: String,
        qualifier: String? = null
    ): DIResult<T> {
        totalResolutions.incrementAndGet()

        val typeName = T::class.qualifiedName ?: T::class.java.name
        val key = buildKey(typeName, qualifier)

        val binding = registry[key] as? Binding<T>
            ?: return DIResult.Err("No binding found for: $key")

        val scope = scopes.getOrPut(scopeId) { ScopeInstance(scopeId) }
        if (!scope.isActive) return DIResult.Err("Scope '$scopeId' is closed")

        val instance = scope.instances.getOrPut(key) {
            totalScopedCreations.incrementAndGet()
            binding.factory()!!
        }

        return DIResult.Ok(instance as T)
    }

    /**
     * Create a new scope.
     */
    fun createScope(id: String): ScopeInstance {
        val scope = ScopeInstance(id)
        scopes[id] = scope
        return scope
    }

    /**
     * Close and clean up a scope.
     */
    fun closeScope(id: String) {
        scopes[id]?.close()
        scopes.remove(id)
    }

    /**
     * Unload all modules and clear container.
     */
    fun reset() {
        registry.clear()
        singletons.clear()
        scopes.values.forEach { it.close() }
        scopes.clear()
        modules.clear()
    }

    // ---- Internal ----

    private fun buildKey(typeName: String, qualifier: String?): String {
        return if (qualifier != null) "$typeName:$qualifier" else typeName
    }

    // ---- Diagnostics ----

    fun diagnostics(): Map<String, Any> = mapOf(
        "engine" to "OmniDependencyContainerEngine",
        "layer" to "Kotlin UI Mobile",
        "total_bindings" to registry.size,
        "total_singletons_cached" to singletons.size,
        "total_active_scopes" to scopes.count { it.value.isActive },
        "total_resolutions" to totalResolutions.get(),
        "singleton_hits" to totalSingletonHits.get(),
        "factory_creations" to totalFactoryCreations.get(),
        "scoped_creations" to totalScopedCreations.get(),
        "modules_loaded" to modules.map { it.name },
        "learned_logic" to listOf(
            "koin-dsl-module-registration",
            "reified-generics-type-safe-resolve",
            "singleton-factory-scoped-lifecycle",
            "qualifier-named-bindings",
            "concurrent-hashmap-thread-safe",
            "scope-lifecycle-management",
            "lazy-singleton-getOrPut",
            "module-based-organization"
        )
    )
}
