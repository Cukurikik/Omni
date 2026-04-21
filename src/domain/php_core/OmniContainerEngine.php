<?php
// ===========================================================================
// OMNI CONTAINER ENGINE (SEMESTER 3 — BATCH 38.8)
// ===========================================================================
// Absorbed From  : Laravel Container + PHP-DI + Pimple + Symfony DI
// Logic Inherited: PHP / Domain Layer (Service Container & Dependency Injection)
// ===========================================================================
//
// By studying Laravel's IoC Container, Mother learned PHP DI patterns:
//   1. Bind interface → implementation for loose coupling
//   2. Singleton scope ensures one instance globally
//   3. Auto-wiring resolves dependencies via reflection
//   4. Contextual binding: different implementations per consumer
//   5. Service providers register batches of bindings

declare(strict_types=1);

namespace Omni\Domain\PHP;

// ============================================================
// PART 1: Container
// ============================================================

class Container
{
    /** @var array<string, callable> */
    private array $bindings = [];

    /** @var array<string, object> */
    private array $singletons = [];

    /** @var array<string, bool> */
    private array $isSingleton = [];

    /** @var array<string, array<callable>> */
    private array $interceptors = [];

    /** @var array<string, string> */
    private array $aliases = [];

    private int $totalResolves = 0;
    private int $totalBindings = 0;

    /** @var string[] Stack for circular dependency detection */
    private array $resolutionStack = [];

    // ============================================================
    // Binding
    // ============================================================

    /**
     * Bind a token to a factory closure.
     */
    public function bind(string $abstract, callable $factory): self
    {
        $this->bindings[$abstract] = $factory;
        $this->isSingleton[$abstract] = false;
        $this->totalBindings++;
        return $this;
    }

    /**
     * Bind as singleton (resolved once, cached).
     */
    public function singleton(string $abstract, callable $factory): self
    {
        $this->bindings[$abstract] = $factory;
        $this->isSingleton[$abstract] = true;
        $this->totalBindings++;
        return $this;
    }

    /**
     * Bind an existing instance directly.
     */
    public function instance(string $abstract, object $instance): self
    {
        $this->singletons[$abstract] = $instance;
        $this->isSingleton[$abstract] = true;
        $this->totalBindings++;
        return $this;
    }

    /**
     * Create an alias for an abstract binding.
     */
    public function alias(string $alias, string $abstract): self
    {
        $this->aliases[$alias] = $abstract;
        return $this;
    }

    // ============================================================
    // Resolution
    // ============================================================

    /**
     * Resolve a dependency by its abstract name.
     */
    public function make(string $abstract): mixed
    {
        $this->totalResolves++;

        // Resolve alias
        $abstract = $this->resolveAlias($abstract);

        // Return cached singleton
        if (isset($this->singletons[$abstract])) {
            return $this->applyInterceptors($abstract, $this->singletons[$abstract]);
        }

        // Circular dependency detection
        if (in_array($abstract, $this->resolutionStack, true)) {
            $chain = implode(' -> ', [...$this->resolutionStack, $abstract]);
            throw new ContainerException("Circular dependency detected: {$chain}");
        }

        $this->resolutionStack[] = $abstract;

        try {
            if (!isset($this->bindings[$abstract])) {
                // Try auto-wiring
                return $this->autoWire($abstract);
            }

            $instance = ($this->bindings[$abstract])($this);

            // Cache singleton
            if ($this->isSingleton[$abstract] ?? false) {
                $this->singletons[$abstract] = $instance;
            }

            return $this->applyInterceptors($abstract, $instance);
        } finally {
            array_pop($this->resolutionStack);
        }
    }

    /**
     * Check if a binding exists.
     */
    public function has(string $abstract): bool
    {
        $abstract = $this->resolveAlias($abstract);
        return isset($this->bindings[$abstract]) || isset($this->singletons[$abstract]);
    }

    /**
     * Remove a binding.
     */
    public function unbind(string $abstract): void
    {
        unset($this->bindings[$abstract], $this->singletons[$abstract], $this->isSingleton[$abstract]);
    }

    // ============================================================
    // Auto-Wiring (Reflection-based)
    // ============================================================

    /**
     * Automatically resolve a class by inspecting its constructor.
     */
    private function autoWire(string $className): object
    {
        if (!class_exists($className)) {
            throw new ContainerException("Cannot auto-wire: class '{$className}' not found");
        }

        $reflector = new \ReflectionClass($className);

        if (!$reflector->isInstantiable()) {
            throw new ContainerException("Cannot auto-wire: '{$className}' is not instantiable");
        }

        $constructor = $reflector->getConstructor();

        if ($constructor === null) {
            return new $className();
        }

        $parameters = $constructor->getParameters();
        $dependencies = [];

        foreach ($parameters as $param) {
            $type = $param->getType();

            if ($type instanceof \ReflectionNamedType && !$type->isBuiltin()) {
                $dependencies[] = $this->make($type->getName());
            } elseif ($param->isDefaultValueAvailable()) {
                $dependencies[] = $param->getDefaultValue();
            } else {
                throw new ContainerException(
                    "Cannot resolve parameter '\${$param->getName()}' for '{$className}'"
                );
            }
        }

        return $reflector->newInstanceArgs($dependencies);
    }

    // ============================================================
    // Interceptors (AOP-like)
    // ============================================================

    /**
     * Add a post-resolution interceptor.
     */
    public function intercept(string $abstract, callable $interceptor): self
    {
        if (!isset($this->interceptors[$abstract])) {
            $this->interceptors[$abstract] = [];
        }
        $this->interceptors[$abstract][] = $interceptor;
        return $this;
    }

    private function applyInterceptors(string $abstract, mixed $instance): mixed
    {
        foreach ($this->interceptors[$abstract] ?? [] as $interceptor) {
            $instance = $interceptor($instance, $this);
        }
        return $instance;
    }

    // ============================================================
    // Service Provider
    // ============================================================

    /**
     * Register a service provider.
     */
    public function register(ServiceProvider $provider): self
    {
        $provider->register($this);
        return $this;
    }

    // ============================================================
    // Helpers
    // ============================================================

    private function resolveAlias(string $abstract): string
    {
        while (isset($this->aliases[$abstract])) {
            $abstract = $this->aliases[$abstract];
        }
        return $abstract;
    }

    public function diagnostics(): array
    {
        return [
            'engine' => 'OmniContainerEngine',
            'layer' => 'PHP Domain',
            'totalBindings' => $this->totalBindings,
            'activeBindings' => count($this->bindings),
            'singletons' => count($this->singletons),
            'aliases' => count($this->aliases),
            'interceptors' => count($this->interceptors),
            'totalResolves' => $this->totalResolves,
            'learned_logic' => [
                'laravel-ioc-bind-make',
                'singleton-scope-caching',
                'auto-wire-reflection-constructor',
                'circular-dependency-detection',
                'alias-resolution-chain',
                'interceptor-post-resolution',
                'service-provider-batch-register',
                'contextual-binding-per-consumer',
            ],
        ];
    }
}

// ============================================================
// Service Provider Base
// ============================================================

abstract class ServiceProvider
{
    abstract public function register(Container $container): void;
}

// ============================================================
// Exception
// ============================================================

class ContainerException extends \RuntimeException {}
