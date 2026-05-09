<?php

namespace Omni\Business;

/**
 * 🪐 OMNI MOTHER - PHP Laravel-style IoC Container
 * A simple but powerful Dependency Injection container.
 */
class IoCContainer {
    protected array $bindings = [];
    protected array $instances = [];

    /**
     * Register a binding with the container.
     */
    public function bind(string $abstract, $concrete = null, bool $shared = false): void {
        if (is_null($concrete)) {
            $concrete = $abstract;
        }

        $this->bindings[$abstract] = compact('concrete', 'shared');
    }

    /**
     * Resolve the given type from the container.
     */
    public function make(string $abstract) {
        if (isset($this->instances[$abstract])) {
            return $this->instances[$abstract];
        }

        $concrete = $this->bindings[$abstract]['concrete'] ?? $abstract;

        if ($concrete instanceof \Closure) {
            $object = $concrete($this);
        } else {
            $object = new $concrete();
        }

        if ($this->bindings[$abstract]['shared'] ?? false) {
            $this->instances[$abstract] = $object;
        }

        return $object;
    }
}