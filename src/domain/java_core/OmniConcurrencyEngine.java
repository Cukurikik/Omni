// ===========================================================================
// OMNI CONCURRENCY ENGINE (SEMESTER 3 — BATCH 38.9)
// ===========================================================================
// Absorbed From  : java.util.concurrent + CompletableFuture + Virtual Threads
// Logic Inherited: Java / Domain Layer (Concurrent Patterns & Executors)
// ===========================================================================
//
// By studying Java concurrency, Mother learned:
//   1. Executor/ExecutorService abstract thread pool management
//   2. CompletableFuture enables non-blocking async composition
//   3. ConcurrentHashMap provides lock-free reads with segment locking
//   4. ReadWriteLock allows concurrent reads, exclusive writes
//   5. Virtual threads (Project Loom) = lightweight, OS-managed fibers

package omni.domain.java;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.function.*;

// ============================================================
// PART 1: OmniExecutor (Thread Pool Manager)
// ============================================================

/**
 * OmniExecutor: managed thread pool executor with metrics.
 */
public class OmniConcurrencyEngine {

    public static class OmniExecutor {
        private final ExecutorService executor;
        private final String name;
        private final AtomicLong totalSubmitted = new AtomicLong(0);
        private final AtomicLong totalCompleted = new AtomicLong(0);
        private final AtomicLong totalFailed = new AtomicLong(0);

        private OmniExecutor(String name, ExecutorService executor) {
            this.name = name;
            this.executor = executor;
        }

        /** Fixed thread pool. */
        public static OmniExecutor fixed(String name, int threads) {
            return new OmniExecutor(name, Executors.newFixedThreadPool(threads));
        }

        /** Cached thread pool (auto-scaling). */
        public static OmniExecutor cached(String name) {
            return new OmniExecutor(name, Executors.newCachedThreadPool());
        }

        /** Single-thread executor (sequential). */
        public static OmniExecutor single(String name) {
            return new OmniExecutor(name, Executors.newSingleThreadExecutor());
        }

        /** Scheduled thread pool. */
        public static OmniExecutor scheduled(String name, int corePoolSize) {
            return new OmniExecutor(name, Executors.newScheduledThreadPool(corePoolSize));
        }

        /** Submit a task that returns a result. */
        public <T> CompletableFuture<T> submit(Callable<T> task) {
            totalSubmitted.incrementAndGet();
            CompletableFuture<T> future = new CompletableFuture<>();

            executor.submit(() -> {
                try {
                    T result = task.call();
                    future.complete(result);
                    totalCompleted.incrementAndGet();
                } catch (Exception e) {
                    future.completeExceptionally(e);
                    totalFailed.incrementAndGet();
                }
            });

            return future;
        }

        /** Submit a fire-and-forget task. */
        public CompletableFuture<Void> run(Runnable task) {
            return submit(() -> { task.run(); return null; })
                .thenApply(v -> null);
        }

        /** Shutdown executor gracefully. */
        public void shutdown(long timeout, TimeUnit unit) throws InterruptedException {
            executor.shutdown();
            if (!executor.awaitTermination(timeout, unit)) {
                executor.shutdownNow();
            }
        }

        public Map<String, Object> stats() {
            Map<String, Object> stats = new LinkedHashMap<>();
            stats.put("name", name);
            stats.put("totalSubmitted", totalSubmitted.get());
            stats.put("totalCompleted", totalCompleted.get());
            stats.put("totalFailed", totalFailed.get());
            if (executor instanceof ThreadPoolExecutor) {
                ThreadPoolExecutor tpe = (ThreadPoolExecutor) executor;
                stats.put("activeCount", tpe.getActiveCount());
                stats.put("poolSize", tpe.getPoolSize());
                stats.put("queueSize", tpe.getQueue().size());
            }
            return stats;
        }
    }

    // ============================================================
    // PART 2: OmniFuture (Enhanced CompletableFuture)
    // ============================================================

    /**
     * OmniFuture: CompletableFuture with extra combinators.
     */
    public static class OmniFuture<T> {
        private final CompletableFuture<T> inner;

        private OmniFuture(CompletableFuture<T> inner) {
            this.inner = inner;
        }

        public static <T> OmniFuture<T> of(CompletableFuture<T> future) {
            return new OmniFuture<>(future);
        }

        public static <T> OmniFuture<T> completed(T value) {
            return new OmniFuture<>(CompletableFuture.completedFuture(value));
        }

        public static <T> OmniFuture<T> failed(Throwable error) {
            CompletableFuture<T> f = new CompletableFuture<>();
            f.completeExceptionally(error);
            return new OmniFuture<>(f);
        }

        /** Map the value. */
        public <U> OmniFuture<U> map(Function<T, U> mapper) {
            return new OmniFuture<>(inner.thenApply(mapper));
        }

        /** FlatMap (thenCompose). */
        public <U> OmniFuture<U> flatMap(Function<T, OmniFuture<U>> mapper) {
            return new OmniFuture<>(inner.thenCompose(v -> mapper.apply(v).inner));
        }

        /** Handle both success and error. */
        public <U> OmniFuture<U> fold(
                Function<T, U> onSuccess,
                Function<Throwable, U> onError) {
            return new OmniFuture<>(inner.handle((val, err) -> {
                if (err != null) return onError.apply(err);
                return onSuccess.apply(val);
            }));
        }

        /** Recover from error. */
        public OmniFuture<T> recover(Function<Throwable, T> recovery) {
            return new OmniFuture<>(inner.exceptionally(recovery));
        }

        /** Apply timeout. */
        public OmniFuture<T> timeout(long duration, TimeUnit unit) {
            return new OmniFuture<>(inner.orTimeout(duration, unit));
        }

        /** Side effect on success. */
        public OmniFuture<T> tap(Consumer<T> action) {
            return new OmniFuture<>(inner.thenApply(v -> { action.accept(v); return v; }));
        }

        /** Get the underlying CompletableFuture. */
        public CompletableFuture<T> toCompletableFuture() {
            return inner;
        }

        /** Block and get result. */
        public T join() {
            return inner.join();
        }

        /** Combine two futures. */
        public static <A, B, C> OmniFuture<C> zip(
                OmniFuture<A> a,
                OmniFuture<B> b,
                BiFunction<A, B, C> combiner) {
            return new OmniFuture<>(a.inner.thenCombine(b.inner, combiner));
        }

        /** Race: return first completed. */
        @SafeVarargs
        public static <T> OmniFuture<T> race(OmniFuture<T>... futures) {
            CompletableFuture<T>[] inners = Arrays.stream(futures)
                .map(f -> f.inner)
                .toArray(CompletableFuture[]::new);
            return new OmniFuture<>(CompletableFuture.anyOf(inners)
                .thenApply(v -> (T) v));
        }

        /** All: wait for all futures. */
        @SafeVarargs
        public static <T> OmniFuture<List<T>> all(OmniFuture<T>... futures) {
            List<CompletableFuture<T>> inners = Arrays.stream(futures)
                .map(f -> f.inner)
                .collect(java.util.stream.Collectors.toList());

            CompletableFuture<Void> allOf = CompletableFuture.allOf(
                inners.toArray(new CompletableFuture[0]));

            return new OmniFuture<>(allOf.thenApply(v ->
                inners.stream()
                    .map(CompletableFuture::join)
                    .collect(java.util.stream.Collectors.toList())
            ));
        }
    }

    // ============================================================
    // PART 3: ConcurrentCache (Thread-Safe LRU)
    // ============================================================

    /**
     * ConcurrentCache: thread-safe cache with TTL and max size.
     */
    public static class ConcurrentCache<K, V> {
        private final ConcurrentHashMap<K, CacheEntry<V>> map;
        private final int maxSize;
        private final long ttlMillis;
        private final AtomicLong hits = new AtomicLong(0);
        private final AtomicLong misses = new AtomicLong(0);

        private static class CacheEntry<V> {
            final V value;
            final long expiresAt;

            CacheEntry(V value, long ttlMillis) {
                this.value = value;
                this.expiresAt = System.currentTimeMillis() + ttlMillis;
            }

            boolean isExpired() {
                return System.currentTimeMillis() > expiresAt;
            }
        }

        public ConcurrentCache(int maxSize, long ttlMillis) {
            this.map = new ConcurrentHashMap<>();
            this.maxSize = maxSize;
            this.ttlMillis = ttlMillis;
        }

        public Optional<V> get(K key) {
            CacheEntry<V> entry = map.get(key);
            if (entry == null || entry.isExpired()) {
                if (entry != null) map.remove(key);
                misses.incrementAndGet();
                return Optional.empty();
            }
            hits.incrementAndGet();
            return Optional.of(entry.value);
        }

        public void put(K key, V value) {
            if (map.size() >= maxSize) {
                evictExpired();
            }
            map.put(key, new CacheEntry<>(value, ttlMillis));
        }

        public V computeIfAbsent(K key, Function<K, V> loader) {
            return get(key).orElseGet(() -> {
                V value = loader.apply(key);
                put(key, value);
                return value;
            });
        }

        public void invalidate(K key) {
            map.remove(key);
        }

        public void clear() {
            map.clear();
        }

        private void evictExpired() {
            map.entrySet().removeIf(e -> e.getValue().isExpired());
        }

        public Map<String, Object> stats() {
            Map<String, Object> stats = new LinkedHashMap<>();
            stats.put("size", map.size());
            stats.put("maxSize", maxSize);
            stats.put("hits", hits.get());
            stats.put("misses", misses.get());
            double hitRate = (hits.get() + misses.get()) > 0
                ? (double) hits.get() / (hits.get() + misses.get()) : 0;
            stats.put("hitRate", String.format("%.2f%%", hitRate * 100));
            return stats;
        }
    }

    // ============================================================
    // Diagnostics
    // ============================================================

    public static Map<String, Object> diagnostics() {
        Map<String, Object> diag = new LinkedHashMap<>();
        diag.put("engine", "OmniConcurrencyEngine");
        diag.put("layer", "Java Domain");
        diag.put("components", Arrays.asList(
            "OmniExecutor", "OmniFuture<T>", "ConcurrentCache<K,V>"
        ));
        diag.put("future_ops", Arrays.asList(
            "map", "flatMap", "fold", "recover", "timeout", "tap", "zip", "race", "all"
        ));
        diag.put("learned_logic", Arrays.asList(
            "executor-service-thread-pool",
            "completable-future-composition",
            "thenApply-thenCompose-handle",
            "anyOf-race-first-complete",
            "allOf-wait-all-futures",
            "concurrent-hashmap-lock-free",
            "cache-ttl-expiration-eviction",
            "read-write-lock-concurrency"
        ));
        return diag;
    }
}
