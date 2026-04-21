// ===========================================================================
// OMNI NAVIGATION ENGINE (SEMESTER 3 — BATCH 38.2)
// ===========================================================================
// Absorbed From  : SwiftUI NavigationStack + UIKit Coordinator + TCA Router
// Logic Inherited: Swift / UI Layer (Type-Safe Navigation Stack)
// ===========================================================================

import Foundation

// MARK: - Navigation Destination (Enum-Based Type Safety)

/// Each screen/destination is represented as an enum case.
/// This ensures exhaustive handling and prevents invalid navigation states.
enum NavigationDestination: Hashable, CustomStringConvertible {
    case home
    case engineList(filter: String?)
    case engineDetail(engineId: String)
    case settings
    case profile(userId: String)
    case diagnostics
    case search(query: String)
    
    var description: String {
        switch self {
        case .home: return "home"
        case .engineList(let f): return "engineList(\(f ?? "all"))"
        case .engineDetail(let id): return "engineDetail(\(id))"
        case .settings: return "settings"
        case .profile(let uid): return "profile(\(uid))"
        case .diagnostics: return "diagnostics"
        case .search(let q): return "search(\(q))"
        }
    }
}

// MARK: - Navigation Action

enum NavigationAction {
    case push(NavigationDestination)
    case pop
    case popToRoot
    case replace(NavigationDestination)
    case present(NavigationDestination, style: PresentationStyle)
    case dismiss
    
    enum PresentationStyle {
        case sheet
        case fullScreen
        case popover
    }
}

// MARK: - Navigation Event (for logging/analytics)

struct NavigationEvent {
    let action: String
    let from: NavigationDestination?
    let to: NavigationDestination?
    let timestamp: Date
    let stackDepth: Int
}

// MARK: - Deep Link Parser

struct DeepLinkParser {
    
    /// Parse a URL path into a NavigationDestination.
    /// e.g., "/engine/rust_core" → .engineDetail(engineId: "rust_core")
    static func parse(url: String) -> NavigationDestination? {
        let components = url
            .trimmingCharacters(in: CharacterSet(charactersIn: "/"))
            .components(separatedBy: "/")
        
        guard !components.isEmpty else { return .home }
        
        switch components[0] {
        case "home":
            return .home
        case "engines":
            if components.count > 1 {
                return .engineDetail(engineId: components[1])
            }
            return .engineList(filter: nil)
        case "settings":
            return .settings
        case "profile":
            if components.count > 1 {
                return .profile(userId: components[1])
            }
            return nil
        case "diagnostics":
            return .diagnostics
        case "search":
            if components.count > 1 {
                return .search(query: components[1])
            }
            return nil
        default:
            return nil
        }
    }
}

// MARK: - Navigation Engine

/// Type-safe navigation stack with history, deep linking, and analytics.
final class OmniNavigationEngine {
    
    // Navigation stack (array acts as stack)
    private var stack: [NavigationDestination] = [.home]
    
    // Modal presentation stack
    private var modalStack: [NavigationDestination] = []
    
    // Navigation history (for analytics)
    private var history: [NavigationEvent] = []
    
    // Guards (prevent navigation under certain conditions)
    private var guards: [(NavigationDestination) -> Bool] = []
    
    // Metrics
    private(set) var totalNavigations: Int = 0
    private(set) var totalPops: Int = 0
    private(set) var totalDeepLinks: Int = 0
    private(set) var totalGuardBlocks: Int = 0
    
    /// Current visible destination.
    var current: NavigationDestination {
        modalStack.last ?? stack.last ?? .home
    }
    
    /// Current stack depth.
    var depth: Int { stack.count }
    
    /// Whether we can go back.
    var canGoBack: Bool { stack.count > 1 }
    
    // MARK: - Navigation Actions
    
    /// Push a new destination onto the stack.
    @discardableResult
    func push(_ destination: NavigationDestination) -> Bool {
        // Run navigation guards
        for guard_ in guards {
            if !guard_(destination) {
                totalGuardBlocks += 1
                return false
            }
        }
        
        let from = current
        stack.append(destination)
        recordEvent(action: "push", from: from, to: destination)
        totalNavigations += 1
        return true
    }
    
    /// Pop the top destination.
    @discardableResult
    func pop() -> NavigationDestination? {
        guard stack.count > 1 else { return nil }
        
        let from = current
        let popped = stack.removeLast()
        recordEvent(action: "pop", from: from, to: current)
        totalPops += 1
        return popped
    }
    
    /// Pop to root (home).
    func popToRoot() {
        let from = current
        stack = [.home]
        recordEvent(action: "popToRoot", from: from, to: .home)
        totalPops += 1
    }
    
    /// Replace the current top with a new destination.
    func replace(with destination: NavigationDestination) {
        let from = current
        if !stack.isEmpty {
            stack[stack.count - 1] = destination
        }
        recordEvent(action: "replace", from: from, to: destination)
        totalNavigations += 1
    }
    
    /// Present a modal.
    func present(_ destination: NavigationDestination) {
        let from = current
        modalStack.append(destination)
        recordEvent(action: "present", from: from, to: destination)
        totalNavigations += 1
    }
    
    /// Dismiss the top modal.
    @discardableResult
    func dismiss() -> NavigationDestination? {
        guard !modalStack.isEmpty else { return nil }
        let dismissed = modalStack.removeLast()
        recordEvent(action: "dismiss", from: dismissed, to: current)
        return dismissed
    }
    
    // MARK: - Deep Linking
    
    /// Navigate via deep link URL.
    @discardableResult
    func handleDeepLink(_ url: String) -> Bool {
        guard let destination = DeepLinkParser.parse(url: url) else {
            return false
        }
        
        popToRoot()
        push(destination)
        totalDeepLinks += 1
        return true
    }
    
    // MARK: - Guards
    
    /// Add a navigation guard. Return false to block navigation.
    func addGuard(_ guard_: @escaping (NavigationDestination) -> Bool) {
        guards.append(guard_)
    }
    
    // MARK: - State Query
    
    /// Get the full navigation path as strings.
    var breadcrumbs: [String] {
        stack.map { $0.description }
    }
    
    /// Get recent navigation history.
    func recentHistory(limit: Int = 10) -> [NavigationEvent] {
        Array(history.suffix(limit))
    }
    
    // MARK: - Internal
    
    private func recordEvent(action: String, from: NavigationDestination?, to: NavigationDestination?) {
        let event = NavigationEvent(
            action: action,
            from: from,
            to: to,
            timestamp: Date(),
            stackDepth: stack.count
        )
        history.append(event)
    }
    
    // MARK: - Diagnostics
    
    func diagnostics() -> [String: Any] {
        return [
            "engine": "OmniNavigationEngine",
            "layer": "Swift UI",
            "current_destination": current.description,
            "stack_depth": stack.count,
            "modal_depth": modalStack.count,
            "total_navigations": totalNavigations,
            "total_pops": totalPops,
            "total_deep_links": totalDeepLinks,
            "total_guard_blocks": totalGuardBlocks,
            "history_count": history.count,
            "breadcrumbs": breadcrumbs,
            "learned_logic": [
                "swiftui-navigation-stack",
                "enum-based-type-safe-destinations",
                "coordinator-pattern",
                "deep-link-url-parsing",
                "navigation-guard-middleware",
                "modal-presentation-stack",
                "breadcrumb-trail-tracking",
                "analytics-event-recording"
            ]
        ]
    }
}
