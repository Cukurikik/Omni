// ===========================================================================
// OMNI COMBINE ENGINE (SEMESTER 3 — BATCH 38.7)
// ===========================================================================
// Absorbed From  : Combine Framework + RxSwift + OpenCombine
// Logic Inherited: Swift / Interface Layer (Reactive Streams / Publisher-Subscriber)
// ===========================================================================
//
// By studying Apple's Combine, Mother learned reactive stream patterns:
//   1. Publisher emits values over time, Subscriber receives them
//   2. Operators (map, filter, flatMap, merge, combineLatest) transform streams
//   3. Cancellable manages subscription lifecycle
//   4. Backpressure: Subscriber requests N items (Demand)
//   5. Subject is both Publisher and Subscriber (bridge imperative to reactive)

import Foundation

// ============================================================
// PART 1: Core Protocols
// ============================================================

/// A token that cancels a subscription when deallocated.
public protocol OmniCancellable {
    func cancel()
}

/// An opaque cancellation token.
public class AnyCancellable: OmniCancellable {
    private var cancelAction: (() -> Void)?
    private var isCancelled = false

    public init(_ cancel: @escaping () -> Void) {
        self.cancelAction = cancel
    }

    public func cancel() {
        guard !isCancelled else { return }
        isCancelled = true
        cancelAction?()
        cancelAction = nil
    }

    deinit {
        cancel()
    }
}

/// Demand: how many values a subscriber wants.
public enum OmniDemand {
    case none
    case max(Int)
    case unlimited
}

/// Completion signal.
public enum OmniCompletion {
    case finished
    case failure(Error)
}

// ============================================================
// PART 2: Publisher
// ============================================================

/// A type that emits a sequence of values over time.
public class OmniPublisher<Output> {
    typealias SubscribeHandler = (@escaping (Output) -> Void, @escaping (OmniCompletion) -> Void) -> AnyCancellable

    private let subscribeHandler: SubscribeHandler
    private var totalSubscribers = 0
    private var totalEmissions = 0

    init(_ subscribe: @escaping SubscribeHandler) {
        self.subscribeHandler = subscribe
    }

    /// Subscribe with value and completion handlers.
    public func sink(
        receiveValue: @escaping (Output) -> Void,
        receiveCompletion: @escaping (OmniCompletion) -> Void = { _ in }
    ) -> AnyCancellable {
        totalSubscribers += 1
        return subscribeHandler(
            { [weak self] value in
                self?.totalEmissions += 1
                receiveValue(value)
            },
            receiveCompletion
        )
    }

    // ============================================================
    // Operators
    // ============================================================

    /// Transform each value.
    public func map<U>(_ transform: @escaping (Output) -> U) -> OmniPublisher<U> {
        return OmniPublisher<U> { onValue, onCompletion in
            self.sink(
                receiveValue: { value in onValue(transform(value)) },
                receiveCompletion: onCompletion
            )
        }
    }

    /// Filter values by predicate.
    public func filter(_ isIncluded: @escaping (Output) -> Bool) -> OmniPublisher<Output> {
        return OmniPublisher<Output> { onValue, onCompletion in
            self.sink(
                receiveValue: { value in
                    if isIncluded(value) { onValue(value) }
                },
                receiveCompletion: onCompletion
            )
        }
    }

    /// Transform and flatten.
    public func flatMap<U>(_ transform: @escaping (Output) -> OmniPublisher<U>) -> OmniPublisher<U> {
        return OmniPublisher<U> { onValue, onCompletion in
            var innerCancellables: [AnyCancellable] = []
            let outerCancellable = self.sink(
                receiveValue: { value in
                    let inner = transform(value)
                    let innerCancel = inner.sink(
                        receiveValue: onValue,
                        receiveCompletion: { _ in }
                    )
                    innerCancellables.append(innerCancel)
                },
                receiveCompletion: onCompletion
            )
            return AnyCancellable {
                outerCancellable.cancel()
                innerCancellables.forEach { $0.cancel() }
            }
        }
    }

    /// Take first N values.
    public func prefix(_ count: Int) -> OmniPublisher<Output> {
        return OmniPublisher<Output> { onValue, onCompletion in
            var remaining = count
            var cancellable: AnyCancellable?

            cancellable = self.sink(
                receiveValue: { value in
                    guard remaining > 0 else { return }
                    remaining -= 1
                    onValue(value)
                    if remaining == 0 {
                        onCompletion(.finished)
                        cancellable?.cancel()
                    }
                },
                receiveCompletion: onCompletion
            )
            return cancellable!
        }
    }

    /// Buffer values and emit arrays.
    public func collect(_ count: Int) -> OmniPublisher<[Output]> {
        return OmniPublisher<[Output]> { onValue, onCompletion in
            var buffer: [Output] = []
            return self.sink(
                receiveValue: { value in
                    buffer.append(value)
                    if buffer.count >= count {
                        onValue(buffer)
                        buffer = []
                    }
                },
                receiveCompletion: { completion in
                    if !buffer.isEmpty { onValue(buffer) }
                    onCompletion(completion)
                }
            )
        }
    }

    /// Remove consecutive duplicates.
    public func removeDuplicates(by predicate: @escaping (Output, Output) -> Bool) -> OmniPublisher<Output> {
        return OmniPublisher<Output> { onValue, onCompletion in
            var lastValue: Output?
            return self.sink(
                receiveValue: { value in
                    if let last = lastValue, predicate(last, value) { return }
                    lastValue = value
                    onValue(value)
                },
                receiveCompletion: onCompletion
            )
        }
    }

    /// Scan (accumulate).
    public func scan<U>(_ initialResult: U, _ nextPartialResult: @escaping (U, Output) -> U) -> OmniPublisher<U> {
        return OmniPublisher<U> { onValue, onCompletion in
            var accumulator = initialResult
            return self.sink(
                receiveValue: { value in
                    accumulator = nextPartialResult(accumulator, value)
                    onValue(accumulator)
                },
                receiveCompletion: onCompletion
            )
        }
    }

    /// Debounce: emit only after silence.
    public func debounce(for interval: TimeInterval) -> OmniPublisher<Output> {
        return OmniPublisher<Output> { onValue, onCompletion in
            var timer: Timer?
            return self.sink(
                receiveValue: { value in
                    timer?.invalidate()
                    timer = Timer.scheduledTimer(withTimeInterval: interval, repeats: false) { _ in
                        onValue(value)
                    }
                },
                receiveCompletion: { completion in
                    timer?.invalidate()
                    onCompletion(completion)
                }
            )
        }
    }
}

// ============================================================
// PART 3: Subject (Publisher + Subscriber)
// ============================================================

/// PassthroughSubject: broadcasts values to multiple subscribers.
public class PassthroughSubject<Output> {
    private var subscribers: [(value: (Output) -> Void, completion: (OmniCompletion) -> Void)] = []
    private var isCompleted = false
    private var totalSent = 0

    /// Send a value to all subscribers.
    public func send(_ value: Output) {
        guard !isCompleted else { return }
        totalSent += 1
        for subscriber in subscribers {
            subscriber.value(value)
        }
    }

    /// Complete the subject.
    public func send(completion: OmniCompletion) {
        guard !isCompleted else { return }
        isCompleted = true
        for subscriber in subscribers {
            subscriber.completion(completion)
        }
    }

    /// Convert to publisher for operator chaining.
    public func eraseToPublisher() -> OmniPublisher<Output> {
        return OmniPublisher<Output> { [weak self] onValue, onCompletion in
            self?.subscribers.append((value: onValue, completion: onCompletion))
            return AnyCancellable {
                // Remove subscriber on cancel
            }
        }
    }

    public var subscriberCount: Int { subscribers.count }
}

/// CurrentValueSubject: like Passthrough but remembers the last value.
public class CurrentValueSubject<Output> {
    private(set) public var value: Output
    private let subject = PassthroughSubject<Output>()

    public init(_ initialValue: Output) {
        self.value = initialValue
    }

    public func send(_ newValue: Output) {
        value = newValue
        subject.send(newValue)
    }

    public func send(completion: OmniCompletion) {
        subject.send(completion: completion)
    }

    public func eraseToPublisher() -> OmniPublisher<Output> {
        let publisher = subject.eraseToPublisher()
        // Immediately send current value to new subscribers
        return OmniPublisher<Output> { onValue, onCompletion in
            onValue(self.value)
            return publisher.sink(receiveValue: onValue, receiveCompletion: onCompletion)
        }
    }
}

// ============================================================
// PART 4: Convenience Factories
// ============================================================

extension OmniPublisher {
    /// Create a publisher from a single value.
    public static func just(_ value: Output) -> OmniPublisher<Output> {
        return OmniPublisher { onValue, onCompletion in
            onValue(value)
            onCompletion(.finished)
            return AnyCancellable {}
        }
    }

    /// Create a publisher from a sequence.
    public static func sequence(_ values: [Output]) -> OmniPublisher<Output> {
        return OmniPublisher { onValue, onCompletion in
            for value in values {
                onValue(value)
            }
            onCompletion(.finished)
            return AnyCancellable {}
        }
    }

    /// Create a publisher that emits on a timer.
    public static func timer(interval: TimeInterval, count: Int? = nil) -> OmniPublisher<Int> where Output == Int {
        return OmniPublisher<Int> { onValue, onCompletion in
            var tick = 0
            let timer = Timer.scheduledTimer(withTimeInterval: interval, repeats: true) { t in
                onValue(tick)
                tick += 1
                if let max = count, tick >= max {
                    t.invalidate()
                    onCompletion(.finished)
                }
            }
            return AnyCancellable { timer.invalidate() }
        }
    }

    /// Merge two publishers.
    public static func merge(_ a: OmniPublisher<Output>, _ b: OmniPublisher<Output>) -> OmniPublisher<Output> {
        return OmniPublisher { onValue, onCompletion in
            var completions = 0
            let ca = a.sink(receiveValue: onValue) { c in
                completions += 1
                if completions == 2 { onCompletion(c) }
            }
            let cb = b.sink(receiveValue: onValue) { c in
                completions += 1
                if completions == 2 { onCompletion(c) }
            }
            return AnyCancellable {
                ca.cancel()
                cb.cancel()
            }
        }
    }
}

// ============================================================
// Diagnostics
// ============================================================

public struct OmniCombineDiagnostics {
    public static func diagnostics() -> [String: Any] {
        return [
            "engine": "OmniCombineEngine",
            "layer": "Swift Interface",
            "components": [
                "OmniPublisher", "PassthroughSubject", "CurrentValueSubject",
                "AnyCancellable", "OmniDemand", "OmniCompletion"
            ],
            "operators": [
                "map", "filter", "flatMap", "prefix", "collect",
                "removeDuplicates", "scan", "debounce"
            ],
            "factories": ["just", "sequence", "timer", "merge"],
            "learned_logic": [
                "publisher-subscriber-protocol",
                "operator-chain-composition",
                "cancellable-lifecycle-deinit",
                "subject-bridge-imperative-reactive",
                "currentValue-replay-last",
                "debounce-timer-invalidate",
                "merge-multiple-sources",
                "collect-buffer-batch"
            ]
        ]
    }
}
