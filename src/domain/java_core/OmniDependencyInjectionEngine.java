// ===========================================================================
// OMNI DEPENDENCY INJECTION ENGINE (POLYLINGUAL REMEDIATION — BATCH 37.7)
// ===========================================================================
// Absorbed From  : Spring Framework + Google Guice + Dagger concepts
// Logic Inherited: Java / Domain Layer (Reflection-Based IoC Container)
// Domain Layer   : Domain (Java Core)
// ===========================================================================
//
// By studying Spring's ApplicationContext, Google Guice's Injector, and
// Dagger's compile-time DI, Mother learned that a production IoC
// container requires:
//   1. Binding registry: maps interfaces to implementations
//   2. Lifecycle scopes: Singleton, Prototype (new instance each time)
//   3. Constructor injection via reflection
//   4. Circular dependency detection
//   5. Named qualifiers for multiple implementations of same interface
//
// Java's reflection API enables runtime class inspection and constructor
// invocation, while ConcurrentHashMap provides thread-safe binding storage.

package dev.omni.engine.di;

import java.lang.annotation.*;
import java.lang.reflect.Constructor;
import java.lang.reflect.Parameter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Marks a class as injectable (managed by the container).
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface Injectable {
    Scope scope() default Scope.SINGLETON;
}

/**
 * Marks a constructor for dependency injection.
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.CONSTRUCTOR)
@interface Inject {
}

/**
 * Qualifies a binding with a name (for multiple impls of same interface).
 */
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.PARAMETER, ElementType.TYPE})
@interface Named {
    String value();
}

/**
 * Lifecycle scope for managed instances.
 */
enum Scope {
    /** Single shared instance (default). */
    SINGLETON,
    /** New instance created on each resolution. */
    PROTOTYPE
}

/**
 * A binding definition: maps a type (+ optional name) to a provider.
 */
final class Binding {
    final Class<?> type;
    final Class<?> implementation;
    final String name;
    final Scope scope;
    Object singletonInstance;

    Binding(Class<?> type, Class<?> implementation, String name, Scope scope) {
        this.type = type;
        this.implementation = implementation;
        this.name = name;
        this.scope = scope;
    }

    String key() {
        return name.isEmpty() ? type.getName() : type.getName() + ":" + name;
    }
}

/**
 * Builder for fluent binding configuration.
 */
final class BindingBuilder<T> {
    private final OmniDependencyInjectionEngine container;
    private final Class<T> type;
    private Class<? extends T> implementation;
    private String name = "";
    private Scope scope = Scope.SINGLETON;

    BindingBuilder(OmniDependencyInjectionEngine container, Class<T> type) {
        this.container = container;
        this.type = type;
        this.implementation = type;
    }

    /**
     * Bind to a specific implementation class.
     */
    @SuppressWarnings("unchecked")
    public <I extends T> BindingBuilder<T> to(Class<I> impl) {
        this.implementation = impl;
        return this;
    }

    /**
     * Set the binding name (qualifier).
     */
    public BindingBuilder<T> named(String name) {
        this.name = name;
        return this;
    }

    /**
     * Set lifecycle scope.
     */
    public BindingBuilder<T> in_(Scope scope) {
        this.scope = scope;
        return this;
    }

    /**
     * Register the binding into the container.
     */
    public void register() {
        Binding binding = new Binding(type, implementation, name, scope);
        container.registerBinding(binding);
    }
}

/**
 * Production IoC container with constructor injection, scoping,
 * circular dependency detection, and named qualifiers.
 */
public final class OmniDependencyInjectionEngine {

    /** All registered bindings, keyed by type+name. */
    private final ConcurrentHashMap<String, Binding> bindings = new ConcurrentHashMap<>();

    /** Singleton instance cache. */
    private final ConcurrentHashMap<String, Object> singletons = new ConcurrentHashMap<>();

    /** Tracks types currently being resolved (circular dependency detection). */
    private final ThreadLocal<Set<String>> resolutionStack =
            ThreadLocal.withInitial(HashSet::new);

    /** Metrics. */
    private final AtomicLong totalResolutions = new AtomicLong(0);
    private final AtomicLong totalCreations = new AtomicLong(0);
    private final AtomicLong totalCacheHits = new AtomicLong(0);
    private final AtomicLong totalErrors = new AtomicLong(0);

    // ---- Binding API ----

    /**
     * Start a fluent binding for the given type.
     * Usage: container.bind(MyService.class).to(MyServiceImpl.class).register();
     */
    public <T> BindingBuilder<T> bind(Class<T> type) {
        return new BindingBuilder<>(this, type);
    }

    /**
     * Register a pre-built singleton instance directly.
     */
    public <T> void bindInstance(Class<T> type, T instance) {
        bindInstance(type, instance, "");
    }

    public <T> void bindInstance(Class<T> type, T instance, String name) {
        Binding binding = new Binding(type, type, name, Scope.SINGLETON);
        binding.singletonInstance = instance;
        registerBinding(binding);
        singletons.put(binding.key(), instance);
    }

    /**
     * Internal: register a binding.
     */
    void registerBinding(Binding binding) {
        bindings.put(binding.key(), binding);
    }

    // ---- Resolution API ----

    /**
     * Resolve a type from the container.
     */
    public <T> T resolve(Class<T> type) {
        return resolve(type, "");
    }

    /**
     * Resolve a named type from the container.
     */
    @SuppressWarnings("unchecked")
    public <T> T resolve(Class<T> type, String name) {
        totalResolutions.incrementAndGet();

        String key = name.isEmpty() ? type.getName() : type.getName() + ":" + name;

        Binding binding = bindings.get(key);
        if (binding == null) {
            // Try without name as fallback
            binding = bindings.get(type.getName());
            if (binding == null) {
                totalErrors.incrementAndGet();
                throw new IllegalStateException(
                        "No binding found for: " + type.getSimpleName() +
                                (name.isEmpty() ? "" : " (named: " + name + ")"));
            }
        }

        // Singleton: check cache first
        if (binding.scope == Scope.SINGLETON) {
            Object cached = singletons.get(key);
            if (cached != null) {
                totalCacheHits.incrementAndGet();
                return (T) cached;
            }
        }

        // Create new instance
        T instance = (T) createInstance(binding);

        // Cache if singleton
        if (binding.scope == Scope.SINGLETON) {
            singletons.putIfAbsent(key, instance);
            return (T) singletons.get(key);
        }

        return instance;
    }

    /**
     * Check if a type is registered.
     */
    public boolean has(Class<?> type) {
        return bindings.containsKey(type.getName());
    }

    // ---- Instance Creation (Constructor Injection) ----

    private Object createInstance(Binding binding) {
        String key = binding.key();
        Set<String> stack = resolutionStack.get();

        // Circular dependency check
        if (stack.contains(key)) {
            totalErrors.incrementAndGet();
            throw new IllegalStateException(
                    "Circular dependency detected: " + String.join(" → ", stack) + " → " + key);
        }

        stack.add(key);
        try {
            Class<?> impl = binding.implementation;
            Constructor<?> constructor = findInjectableConstructor(impl);
            Parameter[] params = constructor.getParameters();

            if (params.length == 0) {
                totalCreations.incrementAndGet();
                return constructor.newInstance();
            }

            // Resolve all constructor parameters recursively
            Object[] args = new Object[params.length];
            for (int i = 0; i < params.length; i++) {
                Class<?> paramType = params[i].getType();
                String paramName = "";

                // Check for @Named qualifier
                Named named = params[i].getAnnotation(Named.class);
                if (named != null) {
                    paramName = named.value();
                }

                args[i] = resolve(paramType, paramName);
            }

            totalCreations.incrementAndGet();
            return constructor.newInstance(args);

        } catch (IllegalStateException e) {
            throw e; // Re-throw circular dependency
        } catch (Exception e) {
            totalErrors.incrementAndGet();
            throw new IllegalStateException(
                    "Failed to create instance of " + binding.implementation.getSimpleName() +
                            ": " + e.getMessage(), e);
        } finally {
            stack.remove(key);
        }
    }

    /**
     * Find the constructor to use for injection.
     * Priority: @Inject-annotated > single constructor > no-arg constructor.
     */
    private Constructor<?> findInjectableConstructor(Class<?> clazz) {
        Constructor<?>[] constructors = clazz.getDeclaredConstructors();

        // 1. Look for @Inject
        for (Constructor<?> c : constructors) {
            if (c.isAnnotationPresent(Inject.class)) {
                c.setAccessible(true);
                return c;
            }
        }

        // 2. Single constructor
        if (constructors.length == 1) {
            constructors[0].setAccessible(true);
            return constructors[0];
        }

        // 3. No-arg constructor
        for (Constructor<?> c : constructors) {
            if (c.getParameterCount() == 0) {
                c.setAccessible(true);
                return c;
            }
        }

        throw new IllegalStateException(
                "No suitable constructor found for " + clazz.getSimpleName() +
                        ". Use @Inject on the desired constructor.");
    }

    // ---- Lifecycle ----

    /**
     * Clear all singletons (useful for testing).
     */
    public void clearSingletons() {
        singletons.clear();
    }

    /**
     * Remove all bindings and cached instances.
     */
    public void reset() {
        bindings.clear();
        singletons.clear();
    }

    // ---- Query ----

    public int getBindingCount() {
        return bindings.size();
    }

    public int getSingletonCount() {
        return singletons.size();
    }

    public Set<String> getRegisteredTypes() {
        return new HashSet<>(bindings.keySet());
    }

    // ---- Diagnostics ----

    public Map<String, Object> diagnostics() {
        Map<String, Object> info = new LinkedHashMap<>();
        info.put("engine", "OmniDependencyInjectionEngine");
        info.put("layer", "Java Domain");
        info.put("total_bindings", bindings.size());
        info.put("singleton_cache_size", singletons.size());
        info.put("total_resolutions", totalResolutions.get());
        info.put("total_creations", totalCreations.get());
        info.put("total_cache_hits", totalCacheHits.get());
        info.put("total_errors", totalErrors.get());
        info.put("cache_hit_rate",
                totalResolutions.get() > 0
                        ? String.format("%.1f%%",
                    (double) totalCacheHits.get() / totalResolutions.get() * 100)
                        : "N/A");
        info.put("binding_keys", new ArrayList<>(bindings.keySet()));
        info.put("learned_logic", Arrays.asList(
                "constructor-injection-reflection",
                "singleton-prototype-scoping",
                "circular-dependency-threadlocal-stack",
                "named-qualifier-disambiguation",
                "fluent-builder-binding-api",
                "inject-annotation-constructor-priority",
                "concurrent-hashmap-thread-safety"
        ));
        return info;
    }
}
