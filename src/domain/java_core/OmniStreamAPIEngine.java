// ===========================================================================
// OMNI STREAM API ENGINE (SEMESTER 3 — BATCH 38.9)
// ===========================================================================
// Absorbed From  : Java Streams + Optional + Collectors + Project Reactor
// Logic Inherited: Java / Domain Layer (Functional Stream Processing)
// ===========================================================================
//
// By studying Java Streams and Project Reactor, Mother learned:
//   1. Stream is a lazy pipeline: source → intermediate ops → terminal op
//   2. Intermediate: map, filter, flatMap, sorted, distinct, peek
//   3. Terminal: collect, reduce, forEach, count, findFirst, toList
//   4. Collector: toList, toMap, groupingBy, partitioningBy, joining
//   5. Optional: monadic wrapper for nullable values

package omni.domain.java;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.*;
import java.util.stream.Collectors;

// ============================================================
// PART 1: OmniStream (Lazy Pipeline)
// ============================================================

/**
 * OmniStream: a lazy, chainable processing pipeline.
 * Intermediate operations return a new OmniStream (deferred).
 * Terminal operations trigger evaluation.
 */
public class OmniStreamEngine {

    public static class OmniStream<T> {
        private final Supplier<List<T>> source;
        private static final AtomicLong totalPipelines = new AtomicLong(0);
        private static final AtomicLong totalElements = new AtomicLong(0);

        private OmniStream(Supplier<List<T>> source) {
            this.source = source;
            totalPipelines.incrementAndGet();
        }

        /** Create stream from a collection. */
        public static <T> OmniStream<T> of(Collection<T> collection) {
            return new OmniStream<>(() -> new ArrayList<>(collection));
        }

        /** Create stream from varargs. */
        @SafeVarargs
        public static <T> OmniStream<T> of(T... items) {
            return new OmniStream<>(() -> Arrays.asList(items));
        }

        /** Create stream from a range. */
        public static OmniStream<Integer> range(int startInclusive, int endExclusive) {
            return new OmniStream<>(() -> {
                List<Integer> list = new ArrayList<>();
                for (int i = startInclusive; i < endExclusive; i++) {
                    list.add(i);
                }
                return list;
            });
        }

        /** Create infinite stream via generator. */
        public static <T> OmniStream<T> generate(Supplier<T> supplier, int limit) {
            return new OmniStream<>(() -> {
                List<T> list = new ArrayList<>();
                for (int i = 0; i < limit; i++) {
                    list.add(supplier.get());
                }
                return list;
            });
        }

        // ============================================================
        // Intermediate Operations (Lazy)
        // ============================================================

        /** Transform each element. */
        public <R> OmniStream<R> map(Function<T, R> mapper) {
            Supplier<List<T>> prevSource = this.source;
            return new OmniStream<>(() -> {
                List<R> result = new ArrayList<>();
                for (T item : prevSource.get()) {
                    result.add(mapper.apply(item));
                }
                return result;
            });
        }

        /** Filter elements by predicate. */
        public OmniStream<T> filter(Predicate<T> predicate) {
            Supplier<List<T>> prevSource = this.source;
            return new OmniStream<>(() -> {
                List<T> result = new ArrayList<>();
                for (T item : prevSource.get()) {
                    if (predicate.test(item)) {
                        result.add(item);
                    }
                }
                return result;
            });
        }

        /** FlatMap: map + flatten. */
        public <R> OmniStream<R> flatMap(Function<T, OmniStream<R>> mapper) {
            Supplier<List<T>> prevSource = this.source;
            return new OmniStream<>(() -> {
                List<R> result = new ArrayList<>();
                for (T item : prevSource.get()) {
                    result.addAll(mapper.apply(item).toList());
                }
                return result;
            });
        }

        /** Remove duplicates. */
        public OmniStream<T> distinct() {
            Supplier<List<T>> prevSource = this.source;
            return new OmniStream<>(() -> new ArrayList<>(new LinkedHashSet<>(prevSource.get())));
        }

        /** Sort elements. */
        public OmniStream<T> sorted(Comparator<T> comparator) {
            Supplier<List<T>> prevSource = this.source;
            return new OmniStream<>(() -> {
                List<T> list = new ArrayList<>(prevSource.get());
                list.sort(comparator);
                return list;
            });
        }

        /** Limit to first N elements. */
        public OmniStream<T> limit(int maxSize) {
            Supplier<List<T>> prevSource = this.source;
            return new OmniStream<>(() -> {
                List<T> all = prevSource.get();
                return all.subList(0, Math.min(maxSize, all.size()));
            });
        }

        /** Skip first N elements. */
        public OmniStream<T> skip(int n) {
            Supplier<List<T>> prevSource = this.source;
            return new OmniStream<>(() -> {
                List<T> all = prevSource.get();
                return all.subList(Math.min(n, all.size()), all.size());
            });
        }

        /** Peek: side-effect without modifying stream. */
        public OmniStream<T> peek(Consumer<T> action) {
            Supplier<List<T>> prevSource = this.source;
            return new OmniStream<>(() -> {
                List<T> all = prevSource.get();
                all.forEach(action);
                return all;
            });
        }

        // ============================================================
        // Terminal Operations (Eager)
        // ============================================================

        /** Collect to list. */
        public List<T> toList() {
            List<T> result = source.get();
            totalElements.addAndGet(result.size());
            return result;
        }

        /** Collect to set. */
        public Set<T> toSet() {
            return new LinkedHashSet<>(toList());
        }

        /** Collect to map. */
        public <K, V> Map<K, V> toMap(
                Function<T, K> keyMapper,
                Function<T, V> valueMapper) {
            Map<K, V> result = new LinkedHashMap<>();
            for (T item : toList()) {
                result.put(keyMapper.apply(item), valueMapper.apply(item));
            }
            return result;
        }

        /** Reduce to single value. */
        public Optional<T> reduce(BinaryOperator<T> accumulator) {
            List<T> list = toList();
            if (list.isEmpty()) return Optional.empty();
            T result = list.get(0);
            for (int i = 1; i < list.size(); i++) {
                result = accumulator.apply(result, list.get(i));
            }
            return Optional.of(result);
        }

        /** Reduce with initial value. */
        public T reduce(T identity, BinaryOperator<T> accumulator) {
            T result = identity;
            for (T item : toList()) {
                result = accumulator.apply(result, item);
            }
            return result;
        }

        /** For each element. */
        public void forEach(Consumer<T> action) {
            toList().forEach(action);
        }

        /** Count elements. */
        public long count() {
            return toList().size();
        }

        /** Find first element. */
        public Optional<T> findFirst() {
            List<T> list = toList();
            return list.isEmpty() ? Optional.empty() : Optional.of(list.get(0));
        }

        /** Check if any element matches. */
        public boolean anyMatch(Predicate<T> predicate) {
            return toList().stream().anyMatch(predicate);
        }

        /** Check if all elements match. */
        public boolean allMatch(Predicate<T> predicate) {
            return toList().stream().allMatch(predicate);
        }

        /** Check if no elements match. */
        public boolean noneMatch(Predicate<T> predicate) {
            return toList().stream().noneMatch(predicate);
        }

        /** Group by a classifier. */
        public <K> Map<K, List<T>> groupBy(Function<T, K> classifier) {
            return toList().stream().collect(Collectors.groupingBy(classifier));
        }

        /** Partition by a predicate. */
        public Map<Boolean, List<T>> partitionBy(Predicate<T> predicate) {
            return toList().stream().collect(Collectors.partitioningBy(predicate));
        }

        /** Join strings. */
        public String joining(Function<T, String> mapper, String delimiter) {
            return toList().stream().map(mapper).collect(Collectors.joining(delimiter));
        }
    }

    // ============================================================
    // PART 2: OmniOptional (Enhanced Optional)
    // ============================================================

    /**
     * OmniOptional: enhanced Optional with monadic operations.
     */
    public static class OmniOptional<T> {
        private final T value;

        private OmniOptional(T value) {
            this.value = value;
        }

        public static <T> OmniOptional<T> of(T value) {
            Objects.requireNonNull(value, "Value cannot be null");
            return new OmniOptional<>(value);
        }

        public static <T> OmniOptional<T> ofNullable(T value) {
            return new OmniOptional<>(value);
        }

        public static <T> OmniOptional<T> empty() {
            return new OmniOptional<>(null);
        }

        public boolean isPresent() { return value != null; }
        public boolean isEmpty() { return value == null; }

        public T get() {
            if (value == null) throw new NoSuchElementException("No value present");
            return value;
        }

        public T orElse(T other) {
            return value != null ? value : other;
        }

        public T orElseGet(Supplier<T> supplier) {
            return value != null ? value : supplier.get();
        }

        public <X extends Throwable> T orElseThrow(Supplier<X> exceptionSupplier) throws X {
            if (value != null) return value;
            throw exceptionSupplier.get();
        }

        public <U> OmniOptional<U> map(Function<T, U> mapper) {
            if (value == null) return empty();
            return OmniOptional.ofNullable(mapper.apply(value));
        }

        public <U> OmniOptional<U> flatMap(Function<T, OmniOptional<U>> mapper) {
            if (value == null) return empty();
            return mapper.apply(value);
        }

        public OmniOptional<T> filter(Predicate<T> predicate) {
            if (value == null || !predicate.test(value)) return empty();
            return this;
        }

        public void ifPresent(Consumer<T> action) {
            if (value != null) action.accept(value);
        }

        public void ifPresentOrElse(Consumer<T> action, Runnable emptyAction) {
            if (value != null) action.accept(value);
            else emptyAction.run();
        }

        public OmniOptional<T> or(Supplier<OmniOptional<T>> supplier) {
            if (value != null) return this;
            return supplier.get();
        }

        @Override
        public String toString() {
            return value != null ? "OmniOptional[" + value + "]" : "OmniOptional.empty";
        }
    }

    // ============================================================
    // Diagnostics
    // ============================================================

    public static Map<String, Object> diagnostics() {
        Map<String, Object> diag = new LinkedHashMap<>();
        diag.put("engine", "OmniStreamAPIEngine");
        diag.put("layer", "Java Domain");
        diag.put("components", Arrays.asList(
            "OmniStream<T>", "OmniOptional<T>"
        ));
        diag.put("intermediate_ops", Arrays.asList(
            "map", "filter", "flatMap", "distinct", "sorted", "limit", "skip", "peek"
        ));
        diag.put("terminal_ops", Arrays.asList(
            "toList", "toSet", "toMap", "reduce", "forEach", "count",
            "findFirst", "anyMatch", "allMatch", "groupBy", "partitionBy", "joining"
        ));
        diag.put("learned_logic", Arrays.asList(
            "stream-lazy-pipeline-evaluation",
            "intermediate-deferred-terminal-eager",
            "supplier-based-lazy-source",
            "optional-monadic-null-safety",
            "collector-groupingBy-partitioning",
            "reduce-identity-accumulator",
            "flatMap-one-to-many-flatten",
            "functional-interface-lambda"
        ));
        return diag;
    }
}
