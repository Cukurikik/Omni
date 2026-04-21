// ===========================================================================
// OMNI PROTOCOL ENGINE (SEMESTER 3 — BATCH 38.7)
// ===========================================================================
// Absorbed From  : Swift stdlib protocols + SwiftUI + Vapor Middleware
// Logic Inherited: Swift / Interface Layer (Protocol-Oriented Programming)
// ===========================================================================
//
// By studying Swift's POP paradigm, Mother learned:
//   1. Protocols define capabilities, not inheritance hierarchies
//   2. Protocol extensions provide default implementations
//   3. Associated types enable generic protocols (PATs)
//   4. Protocol composition with & operator
//   5. Existential types (any Protocol) vs opaque types (some Protocol)

import Foundation

// ============================================================
// PART 1: Core Protocols with Associated Types
// ============================================================

/// Repository pattern with associated types.
public protocol OmniRepository {
    associatedtype Entity: OmniIdentifiable
    associatedtype ID: Hashable

    func findById(_ id: ID) async throws -> Entity?
    func findAll() async throws -> [Entity]
    func save(_ entity: Entity) async throws -> Entity
    func delete(_ id: ID) async throws -> Bool
    func count() async throws -> Int
}

/// Identifiable protocol (like Swift.Identifiable but explicit).
public protocol OmniIdentifiable {
    associatedtype ID: Hashable
    var id: ID { get }
}

/// Validatable protocol.
public protocol OmniValidatable {
    func validate() -> [ValidationError]
    var isValid: Bool { get }
}

/// Default implementation via protocol extension.
extension OmniValidatable {
    public var isValid: Bool {
        validate().isEmpty
    }

    public func validateOrThrow() throws {
        let errors = validate()
        if !errors.isEmpty {
            throw OmniValidationException(errors: errors)
        }
    }
}

public struct ValidationError: Error, CustomStringConvertible {
    public let field: String
    public let message: String
    public let code: String

    public var description: String { "[\(code)] \(field): \(message)" }
}

public struct OmniValidationException: Error {
    public let errors: [ValidationError]
    public var localizedDescription: String {
        errors.map(\.description).joined(separator: "; ")
    }
}

// ============================================================
// PART 2: Middleware Chain (Vapor-Inspired)
// ============================================================

/// Request context for middleware chain.
public struct RequestContext {
    public var path: String
    public var method: String
    public var headers: [String: String]
    public var body: Data?
    public var metadata: [String: Any]

    public init(path: String, method: String = "GET",
                headers: [String: String] = [:],
                body: Data? = nil) {
        self.path = path
        self.method = method
        self.headers = headers
        self.body = body
        self.metadata = [:]
    }
}

public struct ResponseContext {
    public var status: Int
    public var headers: [String: String]
    public var body: Data?

    public init(status: Int = 200, headers: [String: String] = [:], body: Data? = nil) {
        self.status = status
        self.headers = headers
        self.body = body
    }
}

/// Middleware protocol (Vapor-style).
public protocol OmniMiddleware {
    func handle(
        request: RequestContext,
        next: (RequestContext) async throws -> ResponseContext
    ) async throws -> ResponseContext
}

/// Middleware pipeline that chains middleware in order.
public class MiddlewarePipeline {
    private var middlewares: [OmniMiddleware] = []
    private var totalRequests = 0

    public func use(_ middleware: OmniMiddleware) {
        middlewares.append(middleware)
    }

    public func handle(
        request: RequestContext,
        finalHandler: @escaping (RequestContext) async throws -> ResponseContext
    ) async throws -> ResponseContext {
        totalRequests += 1

        // Build chain from inside out
        var handler: (RequestContext) async throws -> ResponseContext = finalHandler

        for middleware in middlewares.reversed() {
            let nextHandler = handler
            handler = { req in
                try await middleware.handle(request: req, next: nextHandler)
            }
        }

        return try await handler(request)
    }

    public var stats: [String: Any] {
        [
            "middlewareCount": middlewares.count,
            "totalRequests": totalRequests,
        ]
    }
}

// ============================================================
// PART 3: Type-Erased Wrappers
// ============================================================

/// Type-erased Repository wrapper.
public class AnyRepository<Entity: OmniIdentifiable>: OmniRepository where Entity.ID: Hashable {
    public typealias ID = Entity.ID

    private let _findById: (ID) async throws -> Entity?
    private let _findAll: () async throws -> [Entity]
    private let _save: (Entity) async throws -> Entity
    private let _delete: (ID) async throws -> Bool
    private let _count: () async throws -> Int

    public init<R: OmniRepository>(_ repository: R) where R.Entity == Entity, R.ID == Entity.ID {
        _findById = repository.findById
        _findAll = repository.findAll
        _save = repository.save
        _delete = repository.delete
        _count = repository.count
    }

    public func findById(_ id: Entity.ID) async throws -> Entity? {
        try await _findById(id)
    }

    public func findAll() async throws -> [Entity] {
        try await _findAll()
    }

    public func save(_ entity: Entity) async throws -> Entity {
        try await _save(entity)
    }

    public func delete(_ id: Entity.ID) async throws -> Bool {
        try await _delete(id)
    }

    public func count() async throws -> Int {
        try await _count()
    }
}

// ============================================================
// PART 4: In-Memory Repository Implementation
// ============================================================

public class InMemoryRepository<Entity: OmniIdentifiable>: OmniRepository where Entity.ID: Hashable {
    public typealias ID = Entity.ID

    private var storage: [Entity.ID: Entity] = [:]
    private var totalOps = 0

    public init() {}

    public func findById(_ id: Entity.ID) async throws -> Entity? {
        totalOps += 1
        return storage[id]
    }

    public func findAll() async throws -> [Entity] {
        totalOps += 1
        return Array(storage.values)
    }

    public func save(_ entity: Entity) async throws -> Entity {
        totalOps += 1
        storage[entity.id] = entity
        return entity
    }

    public func delete(_ id: Entity.ID) async throws -> Bool {
        totalOps += 1
        return storage.removeValue(forKey: id) != nil
    }

    public func count() async throws -> Int {
        totalOps += 1
        return storage.count
    }

    public var stats: [String: Any] {
        [
            "count": storage.count,
            "totalOps": totalOps,
        ]
    }
}

// ============================================================
// PART 5: Built-in Middleware Implementations
// ============================================================

/// Logging middleware.
public class LoggingMiddleware: OmniMiddleware {
    private var requestCount = 0

    public init() {}

    public func handle(
        request: RequestContext,
        next: (RequestContext) async throws -> ResponseContext
    ) async throws -> ResponseContext {
        requestCount += 1
        let start = Date()
        let response = try await next(request)
        let duration = Date().timeIntervalSince(start) * 1000
        print("[\(request.method)] \(request.path) -> \(response.status) (\(String(format: "%.1f", duration))ms)")
        return response
    }
}

/// Auth middleware.
public class AuthMiddleware: OmniMiddleware {
    private let validTokens: Set<String>

    public init(validTokens: Set<String>) {
        self.validTokens = validTokens
    }

    public func handle(
        request: RequestContext,
        next: (RequestContext) async throws -> ResponseContext
    ) async throws -> ResponseContext {
        guard let auth = request.headers["Authorization"],
              validTokens.contains(auth.replacingOccurrences(of: "Bearer ", with: "")) else {
            return ResponseContext(status: 401, body: "Unauthorized".data(using: .utf8))
        }
        return try await next(request)
    }
}

/// Rate-limiting middleware.
public class RateLimitMiddleware: OmniMiddleware {
    private var requestTimes: [Date] = []
    private let maxRequests: Int
    private let window: TimeInterval

    public init(maxRequests: Int, windowSeconds: TimeInterval) {
        self.maxRequests = maxRequests
        self.window = windowSeconds
    }

    public func handle(
        request: RequestContext,
        next: (RequestContext) async throws -> ResponseContext
    ) async throws -> ResponseContext {
        let now = Date()
        requestTimes = requestTimes.filter { now.timeIntervalSince($0) < window }

        if requestTimes.count >= maxRequests {
            return ResponseContext(status: 429, body: "Too Many Requests".data(using: .utf8))
        }

        requestTimes.append(now)
        return try await next(request)
    }
}

// ============================================================
// Diagnostics
// ============================================================

public struct OmniProtocolDiagnostics {
    public static func diagnostics() -> [String: Any] {
        return [
            "engine": "OmniProtocolEngine",
            "layer": "Swift Interface",
            "protocols": [
                "OmniRepository", "OmniIdentifiable", "OmniValidatable", "OmniMiddleware"
            ],
            "implementations": [
                "InMemoryRepository", "AnyRepository",
                "LoggingMiddleware", "AuthMiddleware", "RateLimitMiddleware",
                "MiddlewarePipeline"
            ],
            "learned_logic": [
                "protocol-oriented-programming",
                "associated-type-generic-protocol",
                "protocol-extension-default-impl",
                "type-erasure-any-wrapper",
                "middleware-chain-inside-out",
                "async-await-concurrency",
                "repository-pattern-generics",
                "rate-limit-sliding-window"
            ]
        ]
    }
}
