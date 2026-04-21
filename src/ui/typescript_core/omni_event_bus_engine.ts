/// <reference lib="dom" />
/// <reference types="node" />
// ===========================================================================
// OMNI EVENT BUS ENGINE (SEMESTER 3 — BATCH 38.7)
// ===========================================================================
// Absorbed From  : EventEmitter3 + mitt + RxJS Subject + tRPC subscriptions
// Logic Inherited: TypeScript / Interface Layer (Typed Event Bus / Pub-Sub)
// ===========================================================================
//
// By studying EventEmitter3 and mitt, Mother learned:
//   1. Type-safe event maps prevent runtime string key errors
//   2. Once listeners auto-remove after first invocation
//   3. Wildcard listeners catch all events for logging/debugging
//   4. Async event emission enables non-blocking handler execution
//   5. Priority-based listener ordering controls execution sequence

// ============================================================
// Core Types
// ============================================================

type EventMap = Record<string, any>;
type Handler<T = any> = (payload: T) => void | Promise<void>;
type WildcardHandler<Events extends EventMap> = <K extends keyof Events>(
  type: K,
  payload: Events[K]
) => void;

interface ListenerEntry<T = any> {
  handler: Handler<T>;
  once: boolean;
  priority: number;
  id: number;
}

interface EventStats {
  totalEmits: number;
  totalListenersAdded: number;
  totalListenersRemoved: number;
  totalErrors: number;
  eventCounts: Record<string, number>;
}

// ============================================================
// Typed Event Bus
// ============================================================

class OmniEventBus<Events extends EventMap> {
  private _handlers: Map<keyof Events, ListenerEntry[]> = new Map();
  private _wildcardHandlers: Set<WildcardHandler<Events>> = new Set();
  private _nextId: number = 0;
  private _stats: EventStats = {
    totalEmits: 0,
    totalListenersAdded: 0,
    totalListenersRemoved: 0,
    totalErrors: 0,
    eventCounts: {},
  };
  private _interceptors: Array<(event: keyof Events, payload: any) => any> = [];
  private _deadLetterHandler?: (event: string, payload: any) => void;
  private _maxListenersPerEvent: number = 100;

  /**
   * Register an event handler.
   */
  on<K extends keyof Events>(
    event: K,
    handler: Handler<Events[K]>,
    options: { priority?: number; once?: boolean } = {}
  ): () => void {
    const { priority = 0, once = false } = options;
    const id = this._nextId++;
    const entry: ListenerEntry<Events[K]> = { handler, once, priority, id };

    if (!this._handlers.has(event)) {
      this._handlers.set(event, []);
    }

    const list = this._handlers.get(event)!;

    if (list.length >= this._maxListenersPerEvent) {
      console.warn(
        `[OmniEventBus] Max listeners (${this._maxListenersPerEvent}) reached for event "${String(event)}"`
      );
    }

    list.push(entry);
    // Sort by priority (higher priority first)
    list.sort((a, b) => b.priority - a.priority);

    this._stats.totalListenersAdded++;

    // Return unsubscribe function
    return () => this.off(event, id);
  }

  /**
   * Register a one-time event handler.
   */
  once<K extends keyof Events>(
    event: K,
    handler: Handler<Events[K]>,
    priority: number = 0
  ): () => void {
    return this.on(event, handler, { priority, once: true });
  }

  /**
   * Register a wildcard handler that receives ALL events.
   */
  onAny(handler: WildcardHandler<Events>): () => void {
    this._wildcardHandlers.add(handler);
    return () => this._wildcardHandlers.delete(handler);
  }

  /**
   * Remove a specific handler by ID.
   */
  off<K extends keyof Events>(event: K, handlerId: number): void {
    const list = this._handlers.get(event);
    if (!list) return;

    const idx = list.findIndex((e) => e.id === handlerId);
    if (idx !== -1) {
      list.splice(idx, 1);
      this._stats.totalListenersRemoved++;
    }
  }

  /**
   * Remove all handlers for an event, or all handlers if no event specified.
   */
  removeAllListeners<K extends keyof Events>(event?: K): void {
    if (event) {
      const count = this._handlers.get(event)?.length ?? 0;
      this._handlers.delete(event);
      this._stats.totalListenersRemoved += count;
    } else {
      for (const [, list] of this._handlers) {
        this._stats.totalListenersRemoved += list.length;
      }
      this._handlers.clear();
      this._wildcardHandlers.clear();
    }
  }

  /**
   * Emit an event synchronously.
   */
  emit<K extends keyof Events>(event: K, payload: Events[K]): void {
    this._stats.totalEmits++;
    this._stats.eventCounts[event as string] =
      (this._stats.eventCounts[event as string] || 0) + 1;

    // Run interceptors
    let processedPayload = payload;
    for (const interceptor of this._interceptors) {
      processedPayload = interceptor(event, processedPayload);
    }

    const list = this._handlers.get(event);

    if (!list || list.length === 0) {
      // Dead letter
      this._deadLetterHandler?.(event as string, processedPayload);

      // Still notify wildcards
      for (const wc of this._wildcardHandlers) {
        try { wc(event, processedPayload); } catch (e) { this._stats.totalErrors++; }
      }
      return;
    }

    // Execute handlers
    const toRemove: number[] = [];
    for (const entry of list) {
      try {
        entry.handler(processedPayload);
      } catch (e) {
        this._stats.totalErrors++;
      }
      if (entry.once) {
        toRemove.push(entry.id);
      }
    }

    // Remove once-handlers
    for (const id of toRemove) {
      this.off(event, id);
    }

    // Notify wildcards
    for (const wc of this._wildcardHandlers) {
      try { wc(event, processedPayload); } catch (e) { this._stats.totalErrors++; }
    }
  }

  /**
   * Emit an event asynchronously (all handlers run in parallel).
   */
  async emitAsync<K extends keyof Events>(event: K, payload: Events[K]): Promise<void> {
    this._stats.totalEmits++;
    this._stats.eventCounts[event as string] =
      (this._stats.eventCounts[event as string] || 0) + 1;

    let processedPayload = payload;
    for (const interceptor of this._interceptors) {
      processedPayload = interceptor(event, processedPayload);
    }

    const list = this._handlers.get(event);
    if (!list || list.length === 0) {
      this._deadLetterHandler?.(event as string, processedPayload);
      return;
    }

    const toRemove: number[] = [];
    const promises: Promise<void>[] = [];

    for (const entry of list) {
      promises.push(
        Promise.resolve()
          .then(() => entry.handler(processedPayload))
          .catch(() => { this._stats.totalErrors++; })
      );
      if (entry.once) toRemove.push(entry.id);
    }

    await Promise.all(promises);
    for (const id of toRemove) this.off(event, id);
  }

  /**
   * Wait for the next occurrence of an event (Promise-based).
   */
  waitFor<K extends keyof Events>(event: K, timeout?: number): Promise<Events[K]> {
    return new Promise((resolve, reject) => {
      let timer: ReturnType<typeof setTimeout> | undefined;

      const unsub = this.once(event, (payload) => {
        if (timer) clearTimeout(timer);
        resolve(payload);
      });

      if (timeout) {
        timer = setTimeout(() => {
          unsub();
          reject(new Error(`waitFor "${String(event)}" timed out after ${timeout}ms`));
        }, timeout);
      }
    });
  }

  /**
   * Add an interceptor that transforms payloads before handlers run.
   */
  addInterceptor(fn: (event: keyof Events, payload: any) => any): () => void {
    this._interceptors.push(fn);
    return () => {
      const idx = this._interceptors.indexOf(fn);
      if (idx !== -1) this._interceptors.splice(idx, 1);
    };
  }

  /**
   * Set a dead-letter handler for events with no listeners.
   */
  onDeadLetter(handler: (event: string, payload: any) => void): void {
    this._deadLetterHandler = handler;
  }

  /**
   * Get the number of listeners for an event.
   */
  listenerCount<K extends keyof Events>(event: K): number {
    return this._handlers.get(event)?.length ?? 0;
  }

  /**
   * List all registered event names.
   */
  eventNames(): (keyof Events)[] {
    return Array.from(this._handlers.keys());
  }

  get stats(): EventStats {
    return { ...this._stats };
  }

  diagnostics() {
    return {
      engine: "OmniEventBusEngine",
      layer: "TypeScript Interface",
      totalEvents: this._handlers.size,
      totalWildcards: this._wildcardHandlers.size,
      totalInterceptors: this._interceptors.length,
      stats: this._stats,
      learned_logic: [
        "typed-event-map-safety",
        "priority-ordered-listeners",
        "once-auto-remove-handler",
        "wildcard-catch-all-events",
        "async-emit-parallel-handlers",
        "waitFor-promise-event",
        "interceptor-payload-transform",
        "dead-letter-unhandled-events",
      ],
    };
  }
}

// ============================================================
// Channel (Typed Pub/Sub Topics)
// ============================================================

class EventChannel<T> {
  private _bus = new OmniEventBus<{ message: T }>();
  private _name: string;
  private _buffer: T[] = [];
  private _bufferSize: number;
  private _totalPublished: number = 0;

  constructor(name: string, bufferSize: number = 0) {
    this._name = name;
    this._bufferSize = bufferSize;
  }

  publish(message: T): void {
    this._totalPublished++;
    if (this._bufferSize > 0) {
      this._buffer.push(message);
      if (this._buffer.length > this._bufferSize) {
        this._buffer.shift();
      }
    }
    this._bus.emit("message", message);
  }

  subscribe(handler: Handler<T>): () => void {
    // Replay buffer to new subscriber
    for (const buffered of this._buffer) {
      handler(buffered);
    }
    return this._bus.on("message", handler);
  }

  async waitForNext(timeout?: number): Promise<T> {
    return this._bus.waitFor("message", timeout);
  }

  get stats() {
    return {
      channel: this._name,
      bufferSize: this._buffer.length,
      totalPublished: this._totalPublished,
      ...this._bus.stats,
    };
  }
}

function diagnostics() {
  return {
    engine: "OmniEventBusEngine",
    layer: "TypeScript Interface",
    components: ["OmniEventBus", "EventChannel"],
    learned_logic: [
      "typed-event-map-safety",
      "priority-ordered-listeners",
      "once-auto-remove-handler",
      "wildcard-catch-all-events",
      "async-emit-parallel-handlers",
      "waitFor-promise-event",
      "interceptor-payload-transform",
      "dead-letter-unhandled-events",
      "channel-replay-buffer",
    ],
  };
}

export { OmniEventBus, EventChannel, diagnostics };
export type { Handler, EventMap };
