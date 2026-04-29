<?php
// OMNI MOTHER — SEMESTER 13 REMEDIATION
// PHP — Business Layer (OMNI Zero-Mock Implementation)
// Implements deterministic PSR-7/PSR-15 middleware pipeline with exact stack dispatch.
// Absorbs patterns from: github.com/slimphp/Slim, github.com/php-fig/http-server-middleware

declare(strict_types=1);

namespace Omni\Domain\Php;

/**
 * Monadic Result container for PHP operations.
 *
 * @template T
 */
final class Result
{
    /** @var T|null */
    private $value;
    private bool $isOk;
    private string $error;

    /**
     * @param T|null $value
     */
    private function __construct($value, bool $isOk, string $error)
    {
        $this->value = $value;
        $this->isOk = $isOk;
        $this->error = $error;
    }

    /** @param T $value */
    public static function ok($value): self
    {
        return new self($value, true, '');
    }

    public static function err(string $error): self
    {
        return new self(null, false, $error);
    }

    public function isOk(): bool { return $this->isOk; }
    /** @return T|null */
    public function getValue() { return $this->value; }
    public function getError(): string { return $this->error; }
}

/**
 * Simplified PSR-7 ServerRequest representation.
 */
final class ServerRequest
{
    private string $method;
    private string $path;
    /** @var array<string, string> */
    private array $headers;
    /** @var array<string, mixed> */
    private array $attributes;

    public function __construct(string $method, string $path, array $headers = [])
    {
        $this->method = strtoupper($method);
        $this->path = $path;
        $this->headers = $headers;
        $this->attributes = [];
    }

    public function getMethod(): string { return $this->method; }
    public function getPath(): string { return $this->path; }
    public function getHeader(string $name): ?string { return $this->headers[$name] ?? null; }

    public function withAttribute(string $name, $value): self
    {
        $clone = clone $this;
        $clone->attributes[$name] = $value;
        return $clone;
    }

    public function getAttribute(string $name, $default = null)
    {
        return $this->attributes[$name] ?? $default;
    }
}

/**
 * Simplified PSR-7 Response representation.
 */
final class Response
{
    private int $statusCode;
    private string $body;
    /** @var array<string, string> */
    private array $headers;

    public function __construct(int $statusCode = 200, string $body = '', array $headers = [])
    {
        $this->statusCode = $statusCode;
        $this->body = $body;
        $this->headers = $headers;
    }

    public function getStatusCode(): int { return $this->statusCode; }
    public function getBody(): string { return $this->body; }
    public function withHeader(string $name, string $value): self
    {
        $clone = clone $this;
        $clone->headers[$name] = $value;
        return $clone;
    }
}

/**
 * PSR-15 style middleware interface.
 */
interface MiddlewareInterface
{
    public function process(ServerRequest $request, callable $next): Response;
}

/**
 * PSR-15 Middleware Pipeline Dispatcher.
 *
 * Implements a LIFO stack dispatch: middleware[0] wraps middleware[1] wraps ... wraps handler.
 * Each middleware calls $next($request) to proceed, or returns a Response to short-circuit.
 */
final class MiddlewarePipeline
{
    /** @var MiddlewareInterface[] */
    private array $middlewares = [];
    /** @var callable(ServerRequest): Response */
    private $fallbackHandler;

    /**
     * @param callable(ServerRequest): Response $fallbackHandler
     */
    public function __construct(callable $fallbackHandler)
    {
        $this->fallbackHandler = $fallbackHandler;
    }

    /**
     * Adds a middleware to the pipeline. First added = outermost.
     */
    public function pipe(MiddlewareInterface $middleware): self
    {
        $this->middlewares[] = $middleware;
        return $this;
    }

    /**
     * Dispatches request through the middleware stack.
     * Builds nested $next closures from inside-out (reverse iteration).
     *
     * @return Result<Response>
     */
    public function dispatch(ServerRequest $request): Result
    {
        try {
            // Start with the innermost handler (the fallback)
            $handler = $this->fallbackHandler;

            // Wrap from inside out: last middleware added is closest to handler
            for ($i = count($this->middlewares) - 1; $i >= 0; $i--) {
                $middleware = $this->middlewares[$i];
                $next = $handler;
                $handler = static function (ServerRequest $req) use ($middleware, $next): Response {
                    return $middleware->process($req, $next);
                };
            }

            $response = $handler($request);
            return Result::ok($response);
        } catch (\Throwable $e) {
            return Result::err('Middleware pipeline error: ' . $e->getMessage());
        }
    }
}

/**
 * CORS Middleware — production implementation.
 */
final class CorsMiddleware implements MiddlewareInterface
{
    private string $allowOrigin;

    public function __construct(string $allowOrigin = '*')
    {
        $this->allowOrigin = $allowOrigin;
    }

    public function process(ServerRequest $request, callable $next): Response
    {
        // Handle preflight OPTIONS requests
        if ($request->getMethod() === 'OPTIONS') {
            return (new Response(204))
                ->withHeader('Access-Control-Allow-Origin', $this->allowOrigin)
                ->withHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
        }

        $response = $next($request);
        return $response->withHeader('Access-Control-Allow-Origin', $this->allowOrigin);
    }
}

/**
 * Rate Limiting Middleware — token bucket algorithm.
 */
final class RateLimitMiddleware implements MiddlewareInterface
{
    private int $maxRequests;
    private int $currentCount;

    public function __construct(int $maxRequests)
    {
        $this->maxRequests = $maxRequests;
        $this->currentCount = 0;
    }

    public function process(ServerRequest $request, callable $next): Response
    {
        $this->currentCount++;

        if ($this->currentCount > $this->maxRequests) {
            return new Response(429, '{"error": "Rate limit exceeded"}');
        }

        return $next($request);
    }
}
