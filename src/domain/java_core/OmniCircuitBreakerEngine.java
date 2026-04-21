// ===========================================================================
// OMNI CIRCUIT BREAKER ENGINE (SEMESTER 3 — BATCH 38.2)
// ===========================================================================
// Absorbed From  : Resilience4j + Hystrix + Sentinel patterns
// Logic Inherited: Java / Domain Layer (Fault Tolerance / Circuit Breaking)
// ===========================================================================

package omni.domain.resilience;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Supplier;

public final class OmniCircuitBreakerEngine {

    public enum CircuitState { CLOSED, OPEN, HALF_OPEN }

    public static final class CircuitConfig {
        public final int failureThreshold;
        public final long openDurationMs;
        public final int halfOpenMaxCalls;
        public final double failureRateThreshold;

        public CircuitConfig(int failureThreshold, long openDurationMs,
                             int halfOpenMaxCalls, double failureRateThreshold) {
            this.failureThreshold = failureThreshold;
            this.openDurationMs = openDurationMs;
            this.halfOpenMaxCalls = halfOpenMaxCalls;
            this.failureRateThreshold = failureRateThreshold;
        }

        public static CircuitConfig defaults() {
            return new CircuitConfig(5, 30_000, 3, 0.5);
        }
    }

    // ---- Sliding Window (Ring Buffer) ----

    private static final class SlidingWindow {
        private final boolean[] outcomes; // true=success, false=failure
        private int head;
        private int count;

        SlidingWindow(int size) {
            this.outcomes = new boolean[size];
            this.head = 0;
            this.count = 0;
        }

        void record(boolean success) {
            outcomes[head] = success;
            head = (head + 1) % outcomes.length;
            if (count < outcomes.length) count++;
        }

        double failureRate() {
            if (count == 0) return 0.0;
            int failures = 0;
            for (int i = 0; i < count; i++) {
                if (!outcomes[i]) failures++;
            }
            return (double) failures / count;
        }

        void reset() {
            Arrays.fill(outcomes, true);
            head = 0;
            count = 0;
        }
    }

    // ---- Circuit Breaker Instance ----

    public static final class CircuitBreaker {
        private final String name;
        private final CircuitConfig config;
        private volatile CircuitState state;
        private final SlidingWindow window;
        private final AtomicInteger consecutiveFailures;
        private final AtomicInteger halfOpenCalls;
        private volatile long openedAt;

        // Metrics
        private final AtomicLong totalCalls;
        private final AtomicLong totalSuccesses;
        private final AtomicLong totalFailures;
        private final AtomicLong totalRejected;
        private final AtomicInteger stateTransitions;

        CircuitBreaker(String name, CircuitConfig config) {
            this.name = name;
            this.config = config;
            this.state = CircuitState.CLOSED;
            this.window = new SlidingWindow(100);
            this.consecutiveFailures = new AtomicInteger(0);
            this.halfOpenCalls = new AtomicInteger(0);
            this.openedAt = 0;
            this.totalCalls = new AtomicLong(0);
            this.totalSuccesses = new AtomicLong(0);
            this.totalFailures = new AtomicLong(0);
            this.totalRejected = new AtomicLong(0);
            this.stateTransitions = new AtomicInteger(0);
        }

        /**
         * Execute a supplier through the circuit breaker.
         * CLOSED: allow calls, track failures
         * OPEN: reject immediately (fail fast)
         * HALF_OPEN: allow limited probe calls
         */
        public <T> Result<T> execute(Supplier<T> supplier) {
            totalCalls.incrementAndGet();

            switch (state) {
                case OPEN:
                    if (shouldTransitionToHalfOpen()) {
                        transitionTo(CircuitState.HALF_OPEN);
                    } else {
                        totalRejected.incrementAndGet();
                        return Result.err("Circuit OPEN — call rejected for: " + name);
                    }
                    // fall through to HALF_OPEN

                case HALF_OPEN:
                    if (halfOpenCalls.incrementAndGet() > config.halfOpenMaxCalls) {
                        totalRejected.incrementAndGet();
                        return Result.err("Circuit HALF_OPEN — max probe calls exceeded");
                    }
                    break;

                case CLOSED:
                default:
                    break;
            }

            // Execute the call
            try {
                T result = supplier.get();
                onSuccess();
                return Result.ok(result);
            } catch (Exception e) {
                onFailure();
                return Result.err("Call failed: " + e.getMessage());
            }
        }

        private void onSuccess() {
            totalSuccesses.incrementAndGet();
            window.record(true);
            consecutiveFailures.set(0);

            if (state == CircuitState.HALF_OPEN) {
                transitionTo(CircuitState.CLOSED);
                halfOpenCalls.set(0);
                window.reset();
            }
        }

        private void onFailure() {
            totalFailures.incrementAndGet();
            window.record(false);
            int failures = consecutiveFailures.incrementAndGet();

            if (state == CircuitState.HALF_OPEN) {
                transitionTo(CircuitState.OPEN);
                openedAt = System.currentTimeMillis();
                halfOpenCalls.set(0);
            } else if (state == CircuitState.CLOSED) {
                if (failures >= config.failureThreshold ||
                    window.failureRate() >= config.failureRateThreshold) {
                    transitionTo(CircuitState.OPEN);
                    openedAt = System.currentTimeMillis();
                }
            }
        }

        private boolean shouldTransitionToHalfOpen() {
            return (System.currentTimeMillis() - openedAt) >= config.openDurationMs;
        }

        private void transitionTo(CircuitState newState) {
            this.state = newState;
            stateTransitions.incrementAndGet();
        }

        public CircuitState getState() { return state; }
        public String getName() { return name; }

        public Map<String, Object> getMetrics() {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("name", name);
            m.put("state", state.name());
            m.put("total_calls", totalCalls.get());
            m.put("successes", totalSuccesses.get());
            m.put("failures", totalFailures.get());
            m.put("rejected", totalRejected.get());
            m.put("failure_rate", String.format("%.1f%%", window.failureRate() * 100));
            m.put("state_transitions", stateTransitions.get());
            return m;
        }
    }

    // ---- Result Type ----

    public static final class Result<T> {
        private final T value;
        private final String error;
        private final boolean ok;

        private Result(T v, String e, boolean ok) { this.value = v; this.error = e; this.ok = ok; }
        public static <T> Result<T> ok(T v) { return new Result<>(v, null, true); }
        public static <T> Result<T> err(String e) { return new Result<>(null, e, false); }
        public boolean isOk() { return ok; }
        public T getValue() { return value; }
        public String getError() { return error; }
    }

    // ---- Engine (manages multiple breakers) ----

    private final Map<String, CircuitBreaker> breakers;

    public OmniCircuitBreakerEngine() {
        this.breakers = new ConcurrentHashMap<>();
    }

    public CircuitBreaker createBreaker(String name, CircuitConfig config) {
        CircuitBreaker cb = new CircuitBreaker(name, config);
        breakers.put(name, cb);
        return cb;
    }

    public CircuitBreaker createBreaker(String name) {
        return createBreaker(name, CircuitConfig.defaults());
    }

    public CircuitBreaker getBreaker(String name) {
        return breakers.get(name);
    }

    public <T> Result<T> execute(String breakerName, Supplier<T> supplier) {
        CircuitBreaker cb = breakers.get(breakerName);
        if (cb == null) return Result.err("Unknown breaker: " + breakerName);
        return cb.execute(supplier);
    }

    // ---- Diagnostics ----

    public Map<String, Object> diagnostics() {
        Map<String, Object> info = new LinkedHashMap<>();
        info.put("engine", "OmniCircuitBreakerEngine");
        info.put("layer", "Java Domain");
        info.put("total_breakers", breakers.size());

        List<Map<String, Object>> breakerMetrics = new ArrayList<>();
        for (CircuitBreaker cb : breakers.values()) {
            breakerMetrics.add(cb.getMetrics());
        }
        info.put("breakers", breakerMetrics);
        info.put("learned_logic", List.of(
            "resilience4j-circuit-states",
            "closed-open-half-open-fsm",
            "sliding-window-ring-buffer",
            "failure-rate-threshold",
            "consecutive-failure-counting",
            "half-open-probe-calls",
            "fail-fast-rejection",
            "volatile-state-visibility"
        ));
        return info;
    }
}
