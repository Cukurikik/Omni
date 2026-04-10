// omni-influxdb â€” Reactive State Management

export type Listener<T> = (value: T) => void;
export type Unsubscribe = () => void;

export class ReactiveStore<T> {
  private state: T;
  private listeners: Set<Listener<T>> = new Set();

  constructor(initial: T) { this.state = initial; }
  get(): T { return this.state; }
  set(value: T): void { this.state = value; this.listeners.forEach(l => l(value)); }
  update(fn: (prev: T) => T): void { this.set(fn(this.state)); }
  subscribe(listener: Listener<T>): Unsubscribe { this.listeners.add(listener); return () => this.listeners.delete(listener); }
  derived<U>(fn: (value: T) => U): ReactiveStore<U> {
    const d = new ReactiveStore<U>(fn(this.state));
    this.subscribe(v => d.set(fn(v)));
    return d;
  }
}

export class EventEmitter<T extends Record<string, unknown>> {
  private handlers: Map<keyof T, Set<Function>> = new Map();
  on<K extends keyof T>(event: K, handler: (data: T[K]) => void): Unsubscribe {
    if (!this.handlers.has(event)) this.handlers.set(event, new Set());
    this.handlers.get(event)!.add(handler);
    return () => this.handlers.get(event)?.delete(handler);
  }
  emit<K extends keyof T>(event: K, data: T[K]): void { this.handlers.get(event)?.forEach(h => h(data)); }
}