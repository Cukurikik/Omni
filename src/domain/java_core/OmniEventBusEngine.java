// ===========================================================================
// OMNI EVENT BUS ENGINE (POLYLINGUAL REMEDIATION — BATCH 37.6)
// ===========================================================================
// Absorbed From  : Guava EventBus + greenrobot/EventBus + RxJava concepts
// Logic Inherited: Java / Domain Layer (Thread-Safe Pub/Sub Event Bus)
// Domain Layer   : Domain (Java Core)
// ===========================================================================
//
// By studying Guava's EventBus and greenrobot EventBus, Mother learned
// that a production event bus requires:
//   1. Type-safe event routing (events dispatched by class type)
//   2. Thread safety via ConcurrentHashMap + CopyOnWriteArrayList
//   3. Subscriber priority ordering
//   4. Sticky events (late subscribers receive last event)
//   5. Dead event detection (events with no subscribers)
//   6. Async dispatch option with ExecutorService
//
// Java's ConcurrentHashMap provides lock-free reads for event routing,
// while CopyOnWriteArrayList ensures iterator safety during dispatch.

package dev.omni.engine.eventbus;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import java.lang.reflect.Method;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Annotation to mark methods as event subscribers.
 * Methods must accept exactly one parameter (the event type).
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Subscribe {
    /** Higher priority subscribers are invoked first. Default: 0. */
    int priority() default 0;
    /** If true, this subscriber receives the event on a background thread. */
    boolean async() default false;
    /** If true, this subscriber receives the last sticky event upon registration. */
    boolean sticky() default false;
}

/**
 * Event wrapper for events that have no subscribers.
 */
final class DeadEvent {
    private final Object originalEvent;
    private final long timestamp;

    DeadEvent(Object event) {
        this.originalEvent = event;
        this.timestamp = System.currentTimeMillis();
    }

    public Object getOriginalEvent() { return originalEvent; }
    public long getTimestamp() { return timestamp; }

    @Override
    public String toString() {
        return "DeadEvent{type=" + originalEvent.getClass().getSimpleName() +
               ", timestamp=" + timestamp + "}";
    }
}

/**
 * Internal representation of a subscriber method binding.
 */
final class SubscriberBinding implements Comparable<SubscriberBinding> {
    final Object target;
    final Method method;
    final Class<?> eventType;
    final int priority;
    final boolean async;
    final boolean sticky;

    SubscriberBinding(Object target, Method method, Class<?> eventType,
                      int priority, boolean async, boolean sticky) {
        this.target = target;
        this.method = method;
        this.eventType = eventType;
        this.priority = priority;
        this.async = async;
        this.sticky = sticky;
        this.method.setAccessible(true);
    }

    @Override
    public int compareTo(SubscriberBinding other) {
        // Higher priority first (descending)
        return Integer.compare(other.priority, this.priority);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof SubscriberBinding)) return false;
        SubscriberBinding that = (SubscriberBinding) o;
        return target == that.target && method.equals(that.method);
    }

    @Override
    public int hashCode() {
        return Objects.hash(System.identityHashCode(target), method);
    }
}

/**
 * Production-grade thread-safe event bus with type-safe routing,
 * priority ordering, sticky events, and async dispatch.
 */
public final class OmniEventBusEngine {

    /** Event type → sorted list of subscriber bindings. */
    private final ConcurrentHashMap<Class<?>, CopyOnWriteArrayList<SubscriberBinding>>
            subscribers = new ConcurrentHashMap<>();

    /** Sticky event cache: event type → last posted event. */
    private final ConcurrentHashMap<Class<?>, Object>
            stickyEvents = new ConcurrentHashMap<>();

    /** Dead event log (circular buffer). */
    private final List<DeadEvent> deadEvents =
            Collections.synchronizedList(new ArrayList<>());

    /** Executor for async dispatch. */
    private final ExecutorService asyncExecutor;

    /** Metrics. */
    private final AtomicLong totalEventsPosted = new AtomicLong(0);
    private final AtomicLong totalDeliveries = new AtomicLong(0);
    private final AtomicLong totalDeadEvents = new AtomicLong(0);
    private final AtomicLong totalErrors = new AtomicLong(0);
    private final AtomicLong totalRegistrations = new AtomicLong(0);

    private static final int MAX_DEAD_EVENTS = 100;

    // ---- Constructors ----

    /**
     * Create an event bus with a default cached thread pool for async dispatch.
     */
    public OmniEventBusEngine() {
        this(Executors.newCachedThreadPool(r -> {
            Thread t = new Thread(r, "omni-eventbus-async");
            t.setDaemon(true);
            return t;
        }));
    }

    /**
     * Create an event bus with a custom executor.
     */
    public OmniEventBusEngine(ExecutorService asyncExecutor) {
        this.asyncExecutor = asyncExecutor;
    }

    // ---- Registration ----

    /**
     * Register all @Subscribe-annotated methods on the target object.
     * Scans the class hierarchy for subscriber methods.
     */
    public void register(Object subscriber) {
        Objects.requireNonNull(subscriber, "Subscriber must not be null");

        List<SubscriberBinding> bindings = scanSubscriberMethods(subscriber);

        for (SubscriberBinding binding : bindings) {
            CopyOnWriteArrayList<SubscriberBinding> list =
                    subscribers.computeIfAbsent(binding.eventType,
                            k -> new CopyOnWriteArrayList<>());

            if (!list.contains(binding)) {
                list.add(binding);
                // Re-sort by priority (CopyOnWriteArrayList is snapshot-safe)
                list.sort(null);
                totalRegistrations.incrementAndGet();
            }

            // Deliver sticky event if subscriber opted in
            if (binding.sticky) {
                Object stickyEvent = stickyEvents.get(binding.eventType);
                if (stickyEvent != null) {
                    invokeSubscriber(binding, stickyEvent);
                }
            }
        }
    }

    /**
     * Unregister all subscriber methods from the target object.
     */
    public void unregister(Object subscriber) {
        Objects.requireNonNull(subscriber, "Subscriber must not be null");

        for (CopyOnWriteArrayList<SubscriberBinding> list : subscribers.values()) {
            list.removeIf(binding -> binding.target == subscriber);
        }
    }

    // ---- Event Posting ----

    /**
     * Post an event to all registered subscribers.
     * Dispatches synchronously for sync subscribers, async for async subscribers.
     */
    public void post(Object event) {
        Objects.requireNonNull(event, "Event must not be null");
        totalEventsPosted.incrementAndGet();

        Class<?> eventType = event.getClass();
        boolean delivered = false;

        // Walk the class hierarchy (event → superclass → interfaces)
        Set<Class<?>> eventTypes = resolveEventTypes(eventType);

        for (Class<?> type : eventTypes) {
            CopyOnWriteArrayList<SubscriberBinding> list = subscribers.get(type);
            if (list != null && !list.isEmpty()) {
                for (SubscriberBinding binding : list) {
                    invokeSubscriber(binding, event);
                    totalDeliveries.incrementAndGet();
                    delivered = true;
                }
            }
        }

        // Dead event detection
        if (!delivered) {
            totalDeadEvents.incrementAndGet();
            DeadEvent dead = new DeadEvent(event);

            synchronized (deadEvents) {
                deadEvents.add(dead);
                while (deadEvents.size() > MAX_DEAD_EVENTS) {
                    deadEvents.remove(0);
                }
            }
        }
    }

    /**
     * Post a sticky event. The last event of each type is cached
     * and delivered to future subscribers that opt in.
     */
    public void postSticky(Object event) {
        Objects.requireNonNull(event, "Event must not be null");
        stickyEvents.put(event.getClass(), event);
        post(event);
    }

    /**
     * Remove a sticky event by type.
     */
    public void removeStickyEvent(Class<?> eventType) {
        stickyEvents.remove(eventType);
    }

    /**
     * Get the current sticky event for a type.
     */
    @SuppressWarnings("unchecked")
    public <T> T getStickyEvent(Class<T> eventType) {
        return (T) stickyEvents.get(eventType);
    }

    // ---- Internal ----

    /**
     * Invoke a single subscriber, either sync or async.
     */
    private void invokeSubscriber(SubscriberBinding binding, Object event) {
        if (binding.async) {
            asyncExecutor.submit(() -> safeInvoke(binding, event));
        } else {
            safeInvoke(binding, event);
        }
    }

    /**
     * Safe reflective invocation with error containment.
     */
    private void safeInvoke(SubscriberBinding binding, Object event) {
        try {
            binding.method.invoke(binding.target, event);
        } catch (Exception e) {
            totalErrors.incrementAndGet();
            // Subscriber errors should NOT crash the bus
            System.err.println("[OmniEventBus] Error in subscriber " +
                    binding.target.getClass().getSimpleName() + "." +
                    binding.method.getName() + ": " + e.getMessage());
        }
    }

    /**
     * Scan a class for @Subscribe-annotated methods.
     */
    private List<SubscriberBinding> scanSubscriberMethods(Object subscriber) {
        List<SubscriberBinding> bindings = new ArrayList<>();
        Class<?> clazz = subscriber.getClass();

        // Walk class hierarchy
        while (clazz != null && clazz != Object.class) {
            for (Method method : clazz.getDeclaredMethods()) {
                Subscribe annotation = method.getAnnotation(Subscribe.class);
                if (annotation == null) continue;

                Class<?>[] paramTypes = method.getParameterTypes();
                if (paramTypes.length != 1) {
                    throw new IllegalArgumentException(
                            "@Subscribe method must have exactly one parameter: " +
                                    clazz.getSimpleName() + "." + method.getName());
                }

                bindings.add(new SubscriberBinding(
                        subscriber, method, paramTypes[0],
                        annotation.priority(), annotation.async(), annotation.sticky()
                ));
            }
            clazz = clazz.getSuperclass();
        }

        return bindings;
    }

    /**
     * Resolve all types an event can match: its class + all superclasses + interfaces.
     */
    private Set<Class<?>> resolveEventTypes(Class<?> eventType) {
        Set<Class<?>> types = new LinkedHashSet<>();
        Class<?> current = eventType;

        while (current != null && current != Object.class) {
            types.add(current);
            Collections.addAll(types, current.getInterfaces());
            current = current.getSuperclass();
        }

        return types;
    }

    // ---- Query ----

    /**
     * Number of registered subscriber bindings across all event types.
     */
    public int getSubscriberCount() {
        int count = 0;
        for (CopyOnWriteArrayList<SubscriberBinding> list : subscribers.values()) {
            count += list.size();
        }
        return count;
    }

    /**
     * Number of distinct event types with subscribers.
     */
    public int getEventTypeCount() {
        return subscribers.size();
    }

    /**
     * Recent dead events.
     */
    public List<DeadEvent> getRecentDeadEvents(int limit) {
        synchronized (deadEvents) {
            int start = Math.max(0, deadEvents.size() - limit);
            return new ArrayList<>(deadEvents.subList(start, deadEvents.size()));
        }
    }

    // ---- Lifecycle ----

    /**
     * Shutdown the async executor. Call on application exit.
     */
    public void shutdown() {
        asyncExecutor.shutdown();
        try {
            if (!asyncExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                asyncExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            asyncExecutor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }

    // ---- Diagnostics ----

    /**
     * Structured diagnostics for the OMNI Engine Registry.
     */
    public Map<String, Object> diagnostics() {
        Map<String, Object> info = new LinkedHashMap<>();
        info.put("engine", "OmniEventBusEngine");
        info.put("layer", "Java Domain");
        info.put("subscriber_bindings", getSubscriberCount());
        info.put("event_types_registered", getEventTypeCount());
        info.put("sticky_events_cached", stickyEvents.size());
        info.put("total_events_posted", totalEventsPosted.get());
        info.put("total_deliveries", totalDeliveries.get());
        info.put("total_dead_events", totalDeadEvents.get());
        info.put("total_errors", totalErrors.get());
        info.put("total_registrations", totalRegistrations.get());
        info.put("dead_event_buffer_size", deadEvents.size());
        info.put("learned_logic", Arrays.asList(
                "annotation-based-subscriber-scanning",
                "class-hierarchy-event-routing",
                "concurrent-hashmap-lock-free-reads",
                "copyonwritearraylist-iterator-safety",
                "priority-ordered-dispatch",
                "sticky-event-late-delivery",
                "dead-event-detection",
                "async-executor-dispatch"
        ));
        return info;
    }
}
