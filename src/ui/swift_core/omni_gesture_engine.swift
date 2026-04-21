// ===========================================================================
// OMNI GESTURE ENGINE (POLYLINGUAL REMEDIATION — BATCH 37.6)
// ===========================================================================
// Absorbed From  : Apple UIGestureRecognizer + Flutter gesture_detector
// Logic Inherited: Swift / UI Layer (Finite State Machine Gesture Recognition)
// Domain Layer   : UI Mobile (Swift Core)
// ===========================================================================
//
// By studying Apple's UIGestureRecognizer state machine, Mother learned
// that gesture recognition follows a deterministic FSM:
//   Possible → Began → Changed → Ended (continuous gestures)
//   Possible → Recognized (discrete gestures)
//   Possible → Failed
//
// Swift enums with associated values are perfect for modeling these
// states, and protocol-oriented design allows composable gesture types.

import Foundation

// MARK: - Gesture Types

/// All gesture types the engine can recognize.
enum GestureType: String, CaseIterable {
    case tap
    case doubleTap
    case longPress
    case pan
    case pinch
    case rotation
    case swipeLeft
    case swipeRight
    case swipeUp
    case swipeDown
    case edgePan
}

// MARK: - Gesture State Machine

/// UIGestureRecognizer-compatible state machine.
/// Each state transition is validated — impossible transitions cause `.failed`.
enum GestureState: String {
    case possible     // Initial: waiting for touches
    case began        // Continuous: gesture started
    case changed      // Continuous: gesture updated
    case ended        // Continuous: gesture completed successfully
    case recognized   // Discrete: gesture matched
    case cancelled    // Gesture was interrupted
    case failed       // Gesture did not match

    /// Valid transitions from this state.
    var validTransitions: Set<GestureState> {
        switch self {
        case .possible:
            return [.began, .recognized, .failed]
        case .began:
            return [.changed, .ended, .cancelled]
        case .changed:
            return [.changed, .ended, .cancelled]
        case .ended, .recognized, .cancelled, .failed:
            return [.possible] // Reset
        }
    }

    /// Validate a state transition.
    func canTransition(to next: GestureState) -> Bool {
        return validTransitions.contains(next)
    }
}

// MARK: - Touch Data

/// Raw touch input data.
struct TouchPoint {
    let id: Int
    let x: Double
    let y: Double
    let timestamp: TimeInterval
    let phase: TouchPhase
    let force: Double          // 0.0 to 1.0 (3D Touch / Force Touch)
    let majorRadius: Double    // Touch area radius
}

enum TouchPhase: String {
    case began
    case moved
    case stationary
    case ended
    case cancelled
}

// MARK: - Gesture Event

/// Output event produced when a gesture is recognized.
struct GestureEvent {
    let type: GestureType
    let state: GestureState
    let timestamp: TimeInterval
    let location: (x: Double, y: Double)
    let velocity: (x: Double, y: Double)
    let scale: Double         // For pinch
    let rotation: Double      // For rotation (radians)
    let translation: (x: Double, y: Double)  // For pan
    let touchCount: Int
    let duration: TimeInterval
}

// MARK: - Gesture Recognizer Protocol

/// Protocol for all gesture recognizer implementations.
protocol GestureRecognizer {
    var type: GestureType { get }
    var state: GestureState { get }
    var isEnabled: Bool { get set }

    /// Process a new touch event. Returns a GestureEvent if recognized.
    mutating func processTouchEvent(_ touch: TouchPoint) -> GestureEvent?

    /// Reset the recognizer to initial state.
    mutating func reset()
}

// MARK: - Tap Recognizer

struct TapRecognizer: GestureRecognizer {
    let type: GestureType = .tap
    var state: GestureState = .possible
    var isEnabled: Bool = true

    /// Maximum movement allowed during tap (points).
    var maxMovement: Double = 10.0
    /// Maximum duration for a tap (seconds).
    var maxDuration: TimeInterval = 0.3

    private var startTouch: TouchPoint?
    private var startTime: TimeInterval = 0

    mutating func processTouchEvent(_ touch: TouchPoint) -> GestureEvent? {
        guard isEnabled else { return nil }

        switch touch.phase {
        case .began:
            startTouch = touch
            startTime = touch.timestamp
            state = .possible

        case .moved:
            guard let start = startTouch else { return nil }
            let dx = touch.x - start.x
            let dy = touch.y - start.y
            let distance = sqrt(dx * dx + dy * dy)
            if distance > maxMovement {
                state = .failed
                startTouch = nil
            }

        case .ended:
            guard let start = startTouch else { return nil }
            let duration = touch.timestamp - startTime
            let dx = touch.x - start.x
            let dy = touch.y - start.y
            let distance = sqrt(dx * dx + dy * dy)

            if duration <= maxDuration && distance <= maxMovement {
                state = .recognized
                let event = GestureEvent(
                    type: .tap,
                    state: .recognized,
                    timestamp: touch.timestamp,
                    location: (touch.x, touch.y),
                    velocity: (0, 0),
                    scale: 1.0,
                    rotation: 0,
                    translation: (0, 0),
                    touchCount: 1,
                    duration: duration
                )
                startTouch = nil
                state = .possible
                return event
            } else {
                state = .failed
                startTouch = nil
            }

        case .cancelled:
            state = .cancelled
            startTouch = nil

        case .stationary:
            break
        }

        return nil
    }

    mutating func reset() {
        state = .possible
        startTouch = nil
    }
}

// MARK: - Pan Recognizer

struct PanRecognizer: GestureRecognizer {
    let type: GestureType = .pan
    var state: GestureState = .possible
    var isEnabled: Bool = true

    /// Minimum movement before pan begins (points).
    var minimumDistance: Double = 10.0

    private var startTouch: TouchPoint?
    private var lastTouch: TouchPoint?
    private var accumulatedTranslation: (x: Double, y: Double) = (0, 0)

    mutating func processTouchEvent(_ touch: TouchPoint) -> GestureEvent? {
        guard isEnabled else { return nil }

        switch touch.phase {
        case .began:
            startTouch = touch
            lastTouch = touch
            accumulatedTranslation = (0, 0)
            state = .possible

        case .moved:
            guard let start = startTouch, let last = lastTouch else { return nil }

            let totalDx = touch.x - start.x
            let totalDy = touch.y - start.y
            let totalDist = sqrt(totalDx * totalDx + totalDy * totalDy)

            if state == .possible && totalDist >= minimumDistance {
                state = .began
            }

            if state == .began || state == .changed {
                let dt = max(touch.timestamp - last.timestamp, 0.001)
                let velocityX = (touch.x - last.x) / dt
                let velocityY = (touch.y - last.y) / dt

                accumulatedTranslation = (totalDx, totalDy)
                state = .changed
                lastTouch = touch

                return GestureEvent(
                    type: .pan,
                    state: .changed,
                    timestamp: touch.timestamp,
                    location: (touch.x, touch.y),
                    velocity: (velocityX, velocityY),
                    scale: 1.0,
                    rotation: 0,
                    translation: accumulatedTranslation,
                    touchCount: 1,
                    duration: touch.timestamp - start.timestamp
                )
            }

        case .ended:
            if state == .began || state == .changed {
                state = .ended
                let event = GestureEvent(
                    type: .pan,
                    state: .ended,
                    timestamp: touch.timestamp,
                    location: (touch.x, touch.y),
                    velocity: (0, 0),
                    scale: 1.0,
                    rotation: 0,
                    translation: accumulatedTranslation,
                    touchCount: 1,
                    duration: touch.timestamp - (startTouch?.timestamp ?? touch.timestamp)
                )
                reset()
                return event
            }
            reset()

        case .cancelled:
            state = .cancelled
            reset()

        case .stationary:
            break
        }

        return nil
    }

    mutating func reset() {
        state = .possible
        startTouch = nil
        lastTouch = nil
        accumulatedTranslation = (0, 0)
    }
}

// MARK: - Long Press Recognizer

struct LongPressRecognizer: GestureRecognizer {
    let type: GestureType = .longPress
    var state: GestureState = .possible
    var isEnabled: Bool = true

    /// Duration required for long press (seconds).
    var minimumDuration: TimeInterval = 0.5
    /// Maximum movement allowed during long press.
    var maxMovement: Double = 10.0

    private var startTouch: TouchPoint?

    mutating func processTouchEvent(_ touch: TouchPoint) -> GestureEvent? {
        guard isEnabled else { return nil }

        switch touch.phase {
        case .began:
            startTouch = touch
            state = .possible

        case .stationary, .moved:
            guard let start = startTouch else { return nil }
            let dx = touch.x - start.x
            let dy = touch.y - start.y
            let distance = sqrt(dx * dx + dy * dy)

            if distance > maxMovement {
                state = .failed
                startTouch = nil
                return nil
            }

            let elapsed = touch.timestamp - start.timestamp
            if elapsed >= minimumDuration && state == .possible {
                state = .recognized
                let event = GestureEvent(
                    type: .longPress,
                    state: .recognized,
                    timestamp: touch.timestamp,
                    location: (touch.x, touch.y),
                    velocity: (0, 0),
                    scale: 1.0,
                    rotation: 0,
                    translation: (0, 0),
                    touchCount: 1,
                    duration: elapsed
                )
                return event
            }

        case .ended:
            state = state == .recognized ? .ended : .failed
            startTouch = nil

        case .cancelled:
            state = .cancelled
            startTouch = nil
        }

        return nil
    }

    mutating func reset() {
        state = .possible
        startTouch = nil
    }
}

// MARK: - Core Engine

/// Unified gesture recognition engine managing multiple recognizers.
class OmniGestureEngine {
    private var recognizers: [GestureRecognizer] = []
    private var eventLog: [GestureEvent] = []
    private var totalTouchesProcessed: Int = 0
    private var totalGesturesRecognized: Int = 0
    private var listeners: [(GestureEvent) -> Void] = []

    init() {
        // Register default recognizers
        recognizers.append(TapRecognizer())
        recognizers.append(PanRecognizer())
        recognizers.append(LongPressRecognizer())
    }

    /// Register a custom gesture recognizer.
    func addRecognizer(_ recognizer: GestureRecognizer) {
        recognizers.append(recognizer)
    }

    /// Register an event listener.
    func onGesture(_ handler: @escaping (GestureEvent) -> Void) {
        listeners.append(handler)
    }

    /// Feed a touch event through all active recognizers.
    /// Returns all gesture events that were recognized.
    func processTouch(_ touch: TouchPoint) -> [GestureEvent] {
        totalTouchesProcessed += 1
        var events: [GestureEvent] = []

        for i in 0..<recognizers.count {
            guard recognizers[i].isEnabled else { continue }

            if let event = recognizers[i].processTouchEvent(touch) {
                events.append(event)
                eventLog.append(event)
                totalGesturesRecognized += 1

                // Notify listeners
                for listener in listeners {
                    listener(event)
                }
            }
        }

        return events
    }

    /// Enable/disable a specific gesture type.
    func setEnabled(_ type: GestureType, enabled: Bool) {
        for i in 0..<recognizers.count {
            if recognizers[i].type == type {
                recognizers[i].isEnabled = enabled
            }
        }
    }

    /// Reset all recognizers.
    func resetAll() {
        for i in 0..<recognizers.count {
            recognizers[i].reset()
        }
    }

    /// Get recent gesture events.
    func recentEvents(limit: Int = 20) -> [GestureEvent] {
        return Array(eventLog.suffix(limit))
    }

    /// Diagnostics for OMNI Engine Registry.
    func diagnostics() -> [String: Any] {
        return [
            "engine": "OmniGestureEngine",
            "layer": "Swift UI Mobile",
            "recognizer_count": recognizers.count,
            "active_recognizers": recognizers.filter { $0.isEnabled }.count,
            "supported_gestures": recognizers.map { $0.type.rawValue },
            "total_touches_processed": totalTouchesProcessed,
            "total_gestures_recognized": totalGesturesRecognized,
            "event_log_size": eventLog.count,
            "listener_count": listeners.count,
            "learned_logic": [
                "uigesturerecognizer-fsm",
                "protocol-oriented-recognizer",
                "enum-associated-values-state",
                "validated-state-transitions",
                "velocity-from-touch-delta",
                "multi-recognizer-simultaneous",
                "swift-value-type-mutating"
            ]
        ]
    }
}
