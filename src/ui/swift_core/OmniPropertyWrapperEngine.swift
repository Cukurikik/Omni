// ===========================================================================
// OMNI PROPERTY WRAPPER ENGINE (SEMESTER 3 — BATCH 38.7)
// ===========================================================================
// Absorbed From  : SwiftUI property wrappers + @Binding + @State + @Environment
// Logic Inherited: Swift / Interface Layer (Projected Values & Wrapped Access)
// ===========================================================================
//
// By studying SwiftUI, Mother learned property wrapper patterns:
//   1. @propertyWrapper encapsulates storage + access + projection
//   2. wrappedValue provides the main value access
//   3. projectedValue ($prefix) provides secondary access (e.g., Binding)
//   4. @State triggers UI re-render on change
//   5. @Environment provides dependency injection via key paths

import Foundation

// ============================================================
// PART 1: Validated Property Wrapper
// ============================================================

/// Property wrapper that validates value on every set.
@propertyWrapper
public struct Validated<Value> {
    private var value: Value
    private let validator: (Value) -> Bool
    private let errorMessage: String
    private var totalSets = 0
    private var totalValidationFailures = 0

    public init(wrappedValue: Value, validator: @escaping (Value) -> Bool, message: String = "Validation failed") {
        self.validator = validator
        self.errorMessage = message
        guard validator(wrappedValue) else {
            fatalError("Initial value failed validation: \(message)")
        }
        self.value = wrappedValue
    }

    public var wrappedValue: Value {
        get { value }
        set {
            totalSets += 1
            guard validator(newValue) else {
                totalValidationFailures += 1
                print("⚠️ Validation failed: \(errorMessage)")
                return
            }
            value = newValue
        }
    }

    public var projectedValue: (isValid: Bool, totalSets: Int, totalFailures: Int) {
        (validator(value), totalSets, totalValidationFailures)
    }
}

// ============================================================
// PART 2: Clamped Property Wrapper
// ============================================================

/// Property wrapper that clamps values to a range.
@propertyWrapper
public struct Clamped<Value: Comparable> {
    private var value: Value
    private let range: ClosedRange<Value>

    public init(wrappedValue: Value, _ range: ClosedRange<Value>) {
        self.range = range
        self.value = min(max(wrappedValue, range.lowerBound), range.upperBound)
    }

    public var wrappedValue: Value {
        get { value }
        set { value = min(max(newValue, range.lowerBound), range.upperBound) }
    }
}

// ============================================================
// PART 3: UserDefault Property Wrapper
// ============================================================

/// Property wrapper that persists values in UserDefaults.
@propertyWrapper
public struct UserDefault<Value> {
    private let key: String
    private let defaultValue: Value
    private let storage: UserDefaults

    public init(wrappedValue: Value, key: String, storage: UserDefaults = .standard) {
        self.key = key
        self.defaultValue = wrappedValue
        self.storage = storage
    }

    public var wrappedValue: Value {
        get {
            storage.object(forKey: key) as? Value ?? defaultValue
        }
        set {
            storage.set(newValue, forKey: key)
        }
    }

    public var projectedValue: String { key }
}

// ============================================================
// PART 4: Atomic Property Wrapper (Thread-Safe)
// ============================================================

/// Thread-safe property wrapper using NSLock.
@propertyWrapper
public class Atomic<Value> {
    private var value: Value
    private let lock = NSLock()
    private var totalReads = 0
    private var totalWrites = 0

    public init(wrappedValue: Value) {
        self.value = wrappedValue
    }

    public var wrappedValue: Value {
        get {
            lock.lock()
            defer { lock.unlock() }
            totalReads += 1
            return value
        }
        set {
            lock.lock()
            defer { lock.unlock() }
            totalWrites += 1
            value = newValue
        }
    }

    /// Perform atomic mutation.
    public func mutate(_ mutation: (inout Value) -> Void) {
        lock.lock()
        defer { lock.unlock() }
        totalWrites += 1
        mutation(&value)
    }

    public var projectedValue: (reads: Int, writes: Int) {
        (totalReads, totalWrites)
    }
}

// ============================================================
// PART 5: Observable Property Wrapper
// ============================================================

/// Property wrapper that notifies observers on change.
@propertyWrapper
public class Observable<Value> {
    private var value: Value
    private var observers: [(Value, Value) -> Void] = []
    private var totalChanges = 0

    public init(wrappedValue: Value) {
        self.value = wrappedValue
    }

    public var wrappedValue: Value {
        get { value }
        set {
            let oldValue = value
            value = newValue
            totalChanges += 1
            for observer in observers {
                observer(oldValue, newValue)
            }
        }
    }

    public var projectedValue: Observable<Value> { self }

    /// Add an observer function.
    public func observe(_ handler: @escaping (Value, Value) -> Void) {
        observers.append(handler)
    }

    /// Current observer count.
    public var observerCount: Int { observers.count }
    public var changeCount: Int { totalChanges }
}

// ============================================================
// PART 6: Lazy Injectable Property Wrapper
// ============================================================

/// Property wrapper for lazy dependency injection.
@propertyWrapper
public struct Injected<Value> {
    private var factory: (() -> Value)?
    private var cached: Value?
    private let lazy: Bool

    public init(factory: @escaping () -> Value, lazy: Bool = true) {
        self.factory = factory
        self.lazy = lazy
        if !lazy {
            self.cached = factory()
        }
    }

    public var wrappedValue: Value {
        mutating get {
            if let cached = cached {
                return cached
            }
            let value = factory!()
            cached = value
            return value
        }
    }
}

// ============================================================
// PART 7: Expirable Property Wrapper (TTL Cache)
// ============================================================

/// Property wrapper with time-to-live (TTL) expiration.
@propertyWrapper
public class Expirable<Value> {
    private var value: Value?
    private var expiresAt: Date?
    private let ttl: TimeInterval
    private let defaultValue: Value
    private var totalExpiredReads = 0

    public init(wrappedValue: Value, ttl: TimeInterval) {
        self.defaultValue = wrappedValue
        self.ttl = ttl
        self.value = wrappedValue
        self.expiresAt = Date().addingTimeInterval(ttl)
    }

    public var wrappedValue: Value {
        get {
            if let expires = expiresAt, Date() > expires {
                totalExpiredReads += 1
                value = nil
                expiresAt = nil
                return defaultValue
            }
            return value ?? defaultValue
        }
        set {
            value = newValue
            expiresAt = Date().addingTimeInterval(ttl)
        }
    }

    public var isExpired: Bool {
        guard let expires = expiresAt else { return true }
        return Date() > expires
    }

    public var projectedValue: (isExpired: Bool, expiredReads: Int) {
        (isExpired, totalExpiredReads)
    }
}

// ============================================================
// Diagnostics
// ============================================================

public struct OmniPropertyWrapperDiagnostics {
    public static func diagnostics() -> [String: Any] {
        return [
            "engine": "OmniPropertyWrapperEngine",
            "layer": "Swift Interface",
            "wrappers": [
                "Validated", "Clamped", "UserDefault", "Atomic",
                "Observable", "Injected", "Expirable"
            ],
            "features": [
                "wrappedValue-main-access",
                "projectedValue-dollar-prefix",
                "init-wrappedValue-sugar"
            ],
            "learned_logic": [
                "property-wrapper-encapsulation",
                "projected-value-secondary-api",
                "validated-set-guard-reject",
                "clamped-range-min-max",
                "userdefault-persistence",
                "nslock-thread-safe-atomic",
                "observer-old-new-notification",
                "ttl-expirable-cache-invalidation"
            ]
        ]
    }
}
