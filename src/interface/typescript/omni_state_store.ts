// OMNI MOTHER: Frontend Global State Management (Production Grade)
// Zustand-like reactive store for React.

type Listener = () => void;

export class OmniStateStore<T> {
    private state: T;
    private listeners: Set<Listener> = new Set();

    constructor(initialState: T) {
        this.state = initialState;
    }

    public getState(): T {
        return this.state;
    }

    public setState(partial: Partial<T> | ((state: T) => Partial<T>)) {
        const updates = typeof partial === 'function' ? partial(this.state) : partial;
        this.state = { ...this.state, ...updates };
        this.notify();
    }

    public subscribe(listener: Listener): () => void {
        this.listeners.add(listener);
        return () => this.listeners.delete(listener);
    }

    private notify() {
        this.listeners.forEach(listener => listener());
    }
}
