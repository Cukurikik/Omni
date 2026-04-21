/// <reference lib="dom" />
/// <reference types="node" />
// ===========================================================================
// OMNI DI CONTAINER ENGINE (SEMESTER 3 — BATCH 38.7)
// ===========================================================================
// Absorbed From  : InversifyJS + tsyringe + typed-inject + Awilix
// Logic Inherited: TypeScript / Interface Layer (Inversion of Control)
// ===========================================================================
//
// By studying InversifyJS and tsyringe, Mother learned DI patterns:
//   1. Token-based registration decouples interface from implementation
//   2. Lifecycle scopes: transient (new each time), singleton, scoped
//   3. Automatic dependency resolution via decoration metadata
//   4. Factory providers enable lazy/conditional instantiation
//   5. Child containers inherit + override parent bindings

// ============================================================
// Core Types
// ============================================================

type Token<T = any> = symbol | string;
type Factory<T> = (container: Container) => T;

enum Lifecycle {
  TRANSIENT = "transient",   // New instance every resolve
  SINGLETON = "singleton",   // One instance forever
  SCOPED    = "scoped",      // One instance per scope
}

interface Binding<T> {
  token: Token<T>;
  lifecycle: Lifecycle;
  factory: Factory<T>;
  instance?: T;  // Cached instance for singletons
  tags: Set<string>;
}

interface ResolveOptions {
  optional?: boolean;
}

// ============================================================
// Container Implementation
// ============================================================

class Container {
  private _bindings: Map<Token, Binding<any>> = new Map();
  private _scopedInstances: Map<Token, any> = new Map();
  private _parent: Container | null = null;
  private _children: Set<Container> = new Set();
  private _interceptors: Map<Token, Array<(instance: any) => any>> = new Map();
  private _resolutionStack: Set<Token> = new Set(); // Circular dep detection
  private _totalResolves: number = 0;
  private _totalBindings: number = 0;
  private _disposed: boolean = false;

  constructor(parent?: Container) {
    if (parent) {
      this._parent = parent;
      parent._children.add(this);
    }
  }

  // ============================================================
  // Registration (Fluent API)
  // ============================================================

  /**
   * Bind a token to a factory function.
   */
  bind<T>(token: Token<T>): BindingBuilder<T> {
    return new BindingBuilder(this, token);
  }

  /**
   * Internal: register a completed binding.
   */
  _registerBinding<T>(binding: Binding<T>): void {
    this._bindings.set(binding.token, binding);
    this._totalBindings++;
  }

  /**
   * Register a value directly (singleton shorthand).
   */
  bindValue<T>(token: Token<T>, value: T): this {
    this._bindings.set(token, {
      token,
      lifecycle: Lifecycle.SINGLETON,
      factory: () => value,
      instance: value,
      tags: new Set(),
    });
    this._totalBindings++;
    return this;
  }

  /**
   * Register a class (auto-constructs with `new`).
   */
  bindClass<T>(token: Token<T>, ctor: new (...args: any[]) => T, lifecycle: Lifecycle = Lifecycle.TRANSIENT): this {
    this._bindings.set(token, {
      token,
      lifecycle,
      factory: () => new ctor(),
      tags: new Set(),
    });
    this._totalBindings++;
    return this;
  }

  // ============================================================
  // Resolution
  // ============================================================

  /**
   * Resolve a dependency by its token.
   */
  resolve<T>(token: Token<T>, options: ResolveOptions = {}): T {
    this._totalResolves++;

    if (this._disposed) {
      throw new Error(`Container is disposed, cannot resolve "${String(token)}"`);
    }

    // Circular dependency detection
    if (this._resolutionStack.has(token)) {
      throw new Error(
        `Circular dependency detected: ${[...this._resolutionStack, token].map(String).join(" -> ")}`
      );
    }

    const binding = this._getBinding(token);

    if (!binding) {
      if (options.optional) return undefined as any;
      throw new Error(`No binding found for token "${String(token)}"`);
    }

    let instance: T;

    switch (binding.lifecycle) {
      case Lifecycle.SINGLETON:
        if (binding.instance === undefined) {
          this._resolutionStack.add(token);
          try {
            binding.instance = binding.factory(this);
          } finally {
            this._resolutionStack.delete(token);
          }
        }
        instance = binding.instance;
        break;

      case Lifecycle.SCOPED:
        if (this._scopedInstances.has(token)) {
          instance = this._scopedInstances.get(token);
        } else {
          this._resolutionStack.add(token);
          try {
            instance = binding.factory(this);
          } finally {
            this._resolutionStack.delete(token);
          }
          this._scopedInstances.set(token, instance);
        }
        break;

      case Lifecycle.TRANSIENT:
      default:
        this._resolutionStack.add(token);
        try {
          instance = binding.factory(this);
        } finally {
          this._resolutionStack.delete(token);
        }
        break;
    }

    // Apply interceptors
    const interceptors = this._interceptors.get(token);
    if (interceptors) {
      for (const interceptor of interceptors) {
        instance = interceptor(instance);
      }
    }

    return instance;
  }

  /**
   * Resolve all bindings tagged with a specific tag.
   */
  resolveTagged<T>(tag: string): T[] {
    const results: T[] = [];
    for (const [token, binding] of this._bindings) {
      if (binding.tags.has(tag)) {
        results.push(this.resolve(token));
      }
    }
    return results;
  }

  /**
   * Check if a binding exists.
   */
  has(token: Token): boolean {
    return this._getBinding(token) !== undefined;
  }

  // ============================================================
  // Scoping
  // ============================================================

  /**
   * Create a child container (inherits parent bindings).
   */
  createChild(): Container {
    return new Container(this);
  }

  /**
   * Create a new scope (fresh scoped instances).
   */
  createScope(): Container {
    const scope = new Container(this);
    return scope;
  }

  // ============================================================
  // Interceptors
  // ============================================================

  /**
   * Add a post-resolution interceptor (decorator pattern).
   */
  intercept<T>(token: Token<T>, interceptor: (instance: T) => T): this {
    if (!this._interceptors.has(token)) {
      this._interceptors.set(token, []);
    }
    this._interceptors.get(token)!.push(interceptor);
    return this;
  }

  // ============================================================
  // Lifecycle
  // ============================================================

  /**
   * Dispose container and all children. Calls dispose() on singleton instances.
   */
  dispose(): void {
    this._disposed = true;

    // Dispose children first
    for (const child of this._children) {
      child.dispose();
    }

    // Dispose singleton instances
    for (const [, binding] of this._bindings) {
      if (binding.instance && typeof binding.instance.dispose === 'function') {
        binding.instance.dispose();
      }
    }

    // Clear scoped instances
    for (const [, instance] of this._scopedInstances) {
      if (instance && typeof instance.dispose === 'function') {
        instance.dispose();
      }
    }

    this._bindings.clear();
    this._scopedInstances.clear();
    this._interceptors.clear();
    this._children.clear();

    // Remove from parent
    if (this._parent) {
      this._parent._children.delete(this);
    }
  }

  /**
   * Unbind a specific token.
   */
  unbind(token: Token): void {
    const binding = this._bindings.get(token);
    if (binding?.instance && typeof binding.instance.dispose === 'function') {
      binding.instance.dispose();
    }
    this._bindings.delete(token);
    this._scopedInstances.delete(token);
  }

  // ============================================================
  // Internal
  // ============================================================

  private _getBinding(token: Token): Binding<any> | undefined {
    let binding = this._bindings.get(token);
    if (!binding && this._parent) {
      binding = this._parent._getBinding(token);
    }
    return binding;
  }

  // ============================================================
  // Diagnostics
  // ============================================================

  diagnostics() {
    const bindingInfo = Array.from(this._bindings.entries()).map(([token, binding]) => ({
      token: String(token),
      lifecycle: binding.lifecycle,
      hasInstance: binding.instance !== undefined,
      tags: Array.from(binding.tags),
    }));

    return {
      engine: "OmniDIContainerEngine",
      layer: "TypeScript Interface",
      totalBindings: this._totalBindings,
      activeBindings: this._bindings.size,
      totalResolves: this._totalResolves,
      childContainers: this._children.size,
      scopedInstances: this._scopedInstances.size,
      interceptors: this._interceptors.size,
      disposed: this._disposed,
      bindings: bindingInfo,
      learned_logic: [
        "inversify-token-based-binding",
        "lifecycle-transient-singleton-scoped",
        "circular-dependency-detection",
        "child-container-inheritance",
        "factory-provider-lazy-init",
        "interceptor-post-resolution",
        "tagged-binding-multi-resolve",
        "dispose-cascade-children-first",
      ],
    };
  }
}

// ============================================================
// Binding Builder (Fluent API)
// ============================================================

class BindingBuilder<T> {
  private _token: Token<T>;
  private _container: Container;
  private _lifecycle: Lifecycle = Lifecycle.TRANSIENT;
  private _tags: Set<string> = new Set();
  private _factory?: Factory<T>;

  constructor(container: Container, token: Token<T>) {
    this._container = container;
    this._token = token;
  }

  toFactory(factory: Factory<T>): this {
    this._factory = factory;
    return this;
  }

  toValue(value: T): this {
    this._factory = () => value;
    this._lifecycle = Lifecycle.SINGLETON;
    return this;
  }

  toClass(ctor: new (...args: any[]) => T): this {
    this._factory = () => new ctor();
    return this;
  }

  inSingletonScope(): this {
    this._lifecycle = Lifecycle.SINGLETON;
    return this;
  }

  inTransientScope(): this {
    this._lifecycle = Lifecycle.TRANSIENT;
    return this;
  }

  inScopedScope(): this {
    this._lifecycle = Lifecycle.SCOPED;
    return this;
  }

  withTag(tag: string): this {
    this._tags.add(tag);
    return this;
  }

  done(): Container {
    if (!this._factory) {
      throw new Error(`No factory provided for token "${String(this._token)}"`);
    }
    this._container._registerBinding({
      token: this._token,
      lifecycle: this._lifecycle,
      factory: this._factory,
      tags: this._tags,
    });
    return this._container;
  }
}

// ============================================================
// Token Factory
// ============================================================

function createToken<T>(description: string): Token<T> {
  return Symbol(description);
}

function diagnostics() {
  return {
    engine: "OmniDIContainerEngine",
    layer: "TypeScript Interface",
    components: ["Container", "BindingBuilder", "createToken"],
    lifecycles: Object.values(Lifecycle),
    learned_logic: [
      "inversify-token-based-binding",
      "lifecycle-transient-singleton-scoped",
      "circular-dependency-detection",
      "child-container-inheritance",
      "factory-provider-lazy-init",
      "interceptor-post-resolution",
      "tagged-binding-multi-resolve",
      "dispose-cascade-children-first",
    ],
  };
}

export { Container, BindingBuilder, Lifecycle, createToken, diagnostics };
export type { Token };
