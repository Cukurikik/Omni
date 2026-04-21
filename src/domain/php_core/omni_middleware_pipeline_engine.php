<?php
// ===========================================================================
// OMNI MIDDLEWARE PIPELINE ENGINE (SEMESTER 3 REMEDIATION — BATCH 38.1)
// ===========================================================================
// Absorbed From  : Laravel Pipeline + PSR-15 + Slim Framework middleware
// Logic Inherited: PHP / Domain Layer (PSR-15 Middleware Pipeline)
// Domain Layer   : Domain (PHP Core)
// ===========================================================================
//
// By studying Laravel's Pipeline and PSR-15 middleware spec, Mother
// learned that PHP's middleware pattern composes request handlers:
//   1. Each middleware wraps the next, forming an onion-layer stack
//   2. PSR-7 Request/Response interfaces define immutable HTTP messages
//   3. `array_reduce` in reverse builds the handler chain
//   4. Error middleware catches exceptions and transforms to responses
//
// PHP IS the language for web request lifecycle management in OMNI.

declare(strict_types=1);

namespace Omni\Domain\Middleware;

/**
 * Immutable HTTP Request object (PSR-7 inspired).
 */
final class Request
{
    /** @var string */
    private string $method;
    /** @var string */
    private string $path;
    /** @var array<string, string> */
    private array $headers;
    /** @var string */
    private string $body;
    /** @var array<string, mixed> */
    private array $attributes;
    /** @var float */
    private float $startTime;

    public function __construct(
        string $method,
        string $path,
        array $headers = [],
        string $body = '',
        array $attributes = []
    ) {
        $this->method = strtoupper($method);
        $this->path = $path;
        $this->headers = $headers;
        $this->body = $body;
        $this->attributes = $attributes;
        $this->startTime = microtime(true);
    }

    public function getMethod(): string { return $this->method; }
    public function getPath(): string { return $this->path; }
    public function getHeaders(): array { return $this->headers; }
    public function getHeader(string $name): ?string { return $this->headers[$name] ?? null; }
    public function getBody(): string { return $this->body; }
    public function getAttributes(): array { return $this->attributes; }
    public function getAttribute(string $key, $default = null) { return $this->attributes[$key] ?? $default; }
    public function getElapsedMs(): float { return (microtime(true) - $this->startTime) * 1000; }

    /**
     * Return a new Request with an additional attribute (immutable).
     */
    public function withAttribute(string $key, $value): self
    {
        $clone = clone $this;
        $clone->attributes[$key] = $value;
        return $clone;
    }

    /**
     * Return a new Request with an additional header.
     */
    public function withHeader(string $name, string $value): self
    {
        $clone = clone $this;
        $clone->headers[$name] = $value;
        return $clone;
    }
}

/**
 * HTTP Response object (PSR-7 inspired).
 */
final class Response
{
    private int $status;
    /** @var array<string, string> */
    private array $headers;
    private string $body;

    public function __construct(int $status = 200, array $headers = [], string $body = '')
    {
        $this->status = $status;
        $this->headers = array_merge(['Content-Type' => 'application/json'], $headers);
        $this->body = $body;
    }

    public function getStatus(): int { return $this->status; }
    public function getHeaders(): array { return $this->headers; }
    public function getBody(): string { return $this->body; }

    public function withStatus(int $status): self
    {
        $clone = clone $this;
        $clone->status = $status;
        return $clone;
    }

    public function withBody(string $body): self
    {
        $clone = clone $this;
        $clone->body = $body;
        return $clone;
    }

    public function withHeader(string $name, string $value): self
    {
        $clone = clone $this;
        $clone->headers[$name] = $value;
        return $clone;
    }

    public function json(array $data): self
    {
        return $this->withBody(json_encode($data, JSON_THROW_ON_ERROR))
                    ->withHeader('Content-Type', 'application/json');
    }

    public function toArray(): array
    {
        return [
            'status' => $this->status,
            'headers' => $this->headers,
            'body' => $this->body,
        ];
    }
}

/**
 * Middleware interface (PSR-15 inspired).
 * Each middleware receives a Request and a callable $next,
 * and must return a Response.
 */
interface MiddlewareInterface
{
    public function handle(Request $request, callable $next): Response;
}

/**
 * Logging middleware — logs request method, path, and duration.
 */
final class LoggingMiddleware implements MiddlewareInterface
{
    /** @var array<string> */
    public array $logs = [];

    public function handle(Request $request, callable $next): Response
    {
        $start = microtime(true);
        $response = $next($request);
        $duration = round((microtime(true) - $start) * 1000, 2);

        $this->logs[] = sprintf(
            "[%s] %s %s -> %d (%sms)",
            date('Y-m-d H:i:s'),
            $request->getMethod(),
            $request->getPath(),
            $response->getStatus(),
            $duration
        );

        return $response;
    }
}

/**
 * Authentication middleware — checks for Authorization header.
 */
final class AuthMiddleware implements MiddlewareInterface
{
    private string $expectedToken;

    public function __construct(string $expectedToken = 'omni-secret-token')
    {
        $this->expectedToken = $expectedToken;
    }

    public function handle(Request $request, callable $next): Response
    {
        $auth = $request->getHeader('Authorization');

        if ($auth === null || $auth !== "Bearer {$this->expectedToken}") {
            return (new Response(401))->json([
                'error' => 'Unauthorized',
                'message' => 'Invalid or missing Authorization header',
            ]);
        }

        // Enrich request with authenticated user info
        $enriched = $request->withAttribute('authenticated', true)
                           ->withAttribute('user_id', 'omni-user-001');

        return $next($enriched);
    }
}

/**
 * Rate limit middleware — simple in-memory counter.
 */
final class RateLimitMiddleware implements MiddlewareInterface
{
    private int $maxRequests;
    private int $windowSeconds;
    /** @var array<string, array{count: int, window_start: float}> */
    private array $counters = [];

    public function __construct(int $maxRequests = 100, int $windowSeconds = 60)
    {
        $this->maxRequests = $maxRequests;
        $this->windowSeconds = $windowSeconds;
    }

    public function handle(Request $request, callable $next): Response
    {
        $key = $request->getHeader('X-Client-IP') ?? 'unknown';
        $now = microtime(true);

        if (!isset($this->counters[$key]) ||
            ($now - $this->counters[$key]['window_start']) > $this->windowSeconds) {
            $this->counters[$key] = ['count' => 0, 'window_start' => $now];
        }

        $this->counters[$key]['count']++;

        if ($this->counters[$key]['count'] > $this->maxRequests) {
            return (new Response(429))->json([
                'error' => 'Too Many Requests',
                'retry_after' => $this->windowSeconds,
            ]);
        }

        return $next($request)->withHeader(
            'X-RateLimit-Remaining',
            (string)($this->maxRequests - $this->counters[$key]['count'])
        );
    }
}

/**
 * OMNI Middleware Pipeline Engine.
 *
 * Composes middleware layers into an onion-stack pipeline.
 * The handler is wrapped by each middleware from inside-out,
 * so the first middleware added is the outermost layer.
 */
final class OmniMiddlewarePipelineEngine
{
    /** @var MiddlewareInterface[] */
    private array $middlewares = [];
    /** @var callable|null */
    private $handler = null;

    // Metrics
    private int $totalRequests = 0;
    private int $totalSuccesses = 0;
    private int $totalErrors = 0;

    /**
     * Add a middleware to the pipeline.
     */
    public function pipe(MiddlewareInterface $middleware): self
    {
        $this->middlewares[] = $middleware;
        return $this;
    }

    /**
     * Set the core request handler (innermost layer).
     */
    public function setHandler(callable $handler): self
    {
        $this->handler = $handler;
        return $this;
    }

    /**
     * Dispatch a request through the middleware pipeline.
     *
     * Uses array_reduce in reverse to build the handler chain:
     * middleware[0] wraps middleware[1] wraps ... wraps handler.
     */
    public function dispatch(Request $request): Response
    {
        $this->totalRequests++;

        $coreHandler = $this->handler ?? static function (Request $req): Response {
            return (new Response(404))->json(['error' => 'No handler configured']);
        };

        // Build the onion: reduce right-to-left
        $pipeline = array_reduce(
            array_reverse($this->middlewares),
            static function (callable $next, MiddlewareInterface $middleware): callable {
                return static function (Request $request) use ($middleware, $next): Response {
                    return $middleware->handle($request, $next);
                };
            },
            $coreHandler
        );

        try {
            $response = $pipeline($request);
            if ($response->getStatus() < 400) {
                $this->totalSuccesses++;
            } else {
                $this->totalErrors++;
            }
            return $response;
        } catch (\Throwable $e) {
            $this->totalErrors++;
            return (new Response(500))->json([
                'error' => 'Internal Server Error',
                'message' => $e->getMessage(),
            ]);
        }
    }

    /**
     * OMNI Engine Registry diagnostics.
     */
    public function diagnostics(): array
    {
        return [
            'engine' => 'OmniMiddlewarePipelineEngine',
            'layer' => 'PHP Domain',
            'middleware_count' => count($this->middlewares),
            'middleware_stack' => array_map(
                static fn(MiddlewareInterface $m) => get_class($m),
                $this->middlewares
            ),
            'has_handler' => $this->handler !== null,
            'total_requests' => $this->totalRequests,
            'total_successes' => $this->totalSuccesses,
            'total_errors' => $this->totalErrors,
            'success_rate' => $this->totalRequests > 0
                ? round(($this->totalSuccesses / $this->totalRequests) * 100, 1) . '%'
                : 'N/A',
            'learned_logic' => [
                'psr15-middleware-interface',
                'onion-layer-stack-composition',
                'array-reduce-reverse-pipeline',
                'immutable-request-response',
                'clone-based-with-methods',
                'rate-limit-sliding-window',
                'auth-bearer-token-guard',
                'error-middleware-catch-transform',
            ],
        ];
    }
}
