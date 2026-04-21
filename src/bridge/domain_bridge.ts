/**
 * ===========================================================================
 * OMNI BRIDGE — DOMAIN ↔ ALL LAYERS INTERFACE
 * ===========================================================================
 * TypeScript interface contracts for Domain-layer engines. Any domain engine
 * (C#, Java, Ruby, PHP, GraphQL) must satisfy these interfaces to be
 * invocable from UI/Network/Compute layers via the OMNI bridge.
 * ===========================================================================
 */

/** Canonical domain command envelope. */
export interface DomainCommand {
    readonly commandType: string;
    readonly aggregateId: string;
    readonly payload: Record<string, unknown>;
    readonly timestamp: Date;
}

/** Canonical domain query envelope. */
export interface DomainQuery {
    readonly queryType: string;
    readonly filters: Record<string, unknown>;
    readonly limit?: number;
    readonly offset?: number;
}

/** Canonical domain event emitted after a command succeeds. */
export interface DomainEvent {
    readonly eventType: string;
    readonly aggregateId: string;
    readonly data: Record<string, unknown>;
    readonly occurredAt: Date;
}

/** Result wrapper with monadic error handling (no try/catch). */
export type DomainResult<T> =
    | { success: true; value: T }
    | { success: false; error: string; code: number };

/** All domain engines must implement this interface. */
export interface DomainBridge {
    /** Execute a command (write operation). */
    execute(command: DomainCommand): Promise<DomainResult<DomainEvent>>;

    /** Execute a query (read operation). */
    query<T>(query: DomainQuery): Promise<DomainResult<T[]>>;

    /** Return the engine name. */
    name(): string;

    /** Health check. */
    healthcheck(): boolean;
}

/** Factory to create domain results without try/catch. */
export function ok<T>(value: T): DomainResult<T> {
    return { success: true, value };
}

export function fail<T>(error: string, code: number = 500): DomainResult<T> {
    return { success: false, error, code };
}
