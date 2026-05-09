<?php
// OMNI Business Layer — PHP Model Serving API Gateway
// Laravel-style API gateway for transformer model inference.

declare(strict_types=1);

namespace Omni\Domain\Serving;

use RuntimeException;
use InvalidArgumentException;

/**
 * Inference request value object.
 */
final class InferenceRequest
{
    public function __construct(
        public readonly string $requestId,
        public readonly string $prompt,
        public readonly int $maxTokens = 256,
        public readonly float $temperature = 0.7,
        public readonly float $topP = 0.9,
        public readonly bool $stream = false,
        public readonly float $createdAt = 0.0,
    ) {
        if (empty($this->prompt)) {
            throw new InvalidArgumentException('Prompt cannot be empty');
        }
        if ($this->maxTokens < 1 || $this->maxTokens > 8192) {
            throw new InvalidArgumentException('maxTokens must be 1-8192');
        }
        if ($this->temperature < 0.0 || $this->temperature > 2.0) {
            throw new InvalidArgumentException('temperature must be 0.0-2.0');
        }
    }

    public static function fromArray(array $data): self
    {
        return new self(
            requestId: $data['request_id'] ?? bin2hex(random_bytes(16)),
            prompt: $data['prompt'] ?? throw new InvalidArgumentException('prompt required'),
            maxTokens: (int)($data['max_tokens'] ?? 256),
            temperature: (float)($data['temperature'] ?? 0.7),
            topP: (float)($data['top_p'] ?? 0.9),
            stream: (bool)($data['stream'] ?? false),
            createdAt: microtime(true),
        );
    }
}

/**
 * Inference response.
 */
final class InferenceResponse
{
    public function __construct(
        public readonly string $requestId,
        public readonly string $generatedText,
        public readonly int $tokensGenerated,
        public readonly float $latencyMs,
        public readonly string $finishReason,
        public readonly array $usage,
    ) {}

    public function toArray(): array
    {
        return [
            'request_id' => $this->requestId,
            'generated_text' => $this->generatedText,
            'tokens_generated' => $this->tokensGenerated,
            'latency_ms' => round($this->latencyMs, 2),
            'finish_reason' => $this->finishReason,
            'usage' => $this->usage,
        ];
    }
}

/**
 * Rate limiter for API gateway.
 */
final class RateLimiter
{
    /** @var array<string, array{count: int, window_start: float}> */
    private array $buckets = [];

    public function __construct(
        private readonly int $maxRequestsPerMinute = 60,
    ) {}

    public function isAllowed(string $clientId): bool
    {
        $now = microtime(true);
        if (!isset($this->buckets[$clientId])) {
            $this->buckets[$clientId] = ['count' => 0, 'window_start' => $now];
        }

        $bucket = &$this->buckets[$clientId];
        if ($now - $bucket['window_start'] >= 60.0) {
            $bucket['count'] = 0;
            $bucket['window_start'] = $now;
        }

        if ($bucket['count'] >= $this->maxRequestsPerMinute) {
            return false;
        }

        $bucket['count']++;
        return true;
    }
}

/**
 * Model serving gateway.
 */
final class ModelGateway
{
    private int $totalRequests = 0;
    private float $totalLatency = 0.0;
    private int $errorCount = 0;

    public function __construct(
        private readonly RateLimiter $rateLimiter,
        private readonly string $modelId = 'omni-7b',
    ) {}

    public function infer(InferenceRequest $request, string $clientId): InferenceResponse
    {
        if (!$this->rateLimiter->isAllowed($clientId)) {
            throw new RuntimeException('Rate limit exceeded for client: ' . $clientId);
        }

        $startTime = microtime(true);
        $this->totalRequests++;

        try {
            // Production: call inference engine via FFI/gRPC
            $generatedText = $this->processInference($request);
            $latency = (microtime(true) - $startTime) * 1000.0;
            $this->totalLatency += $latency;

            $promptTokens = (int)(strlen($request->prompt) / 4);
            $completionTokens = (int)(strlen($generatedText) / 4);

            return new InferenceResponse(
                requestId: $request->requestId,
                generatedText: $generatedText,
                tokensGenerated: $completionTokens,
                latencyMs: $latency,
                finishReason: 'stop',
                usage: [
                    'prompt_tokens' => $promptTokens,
                    'completion_tokens' => $completionTokens,
                    'total_tokens' => $promptTokens + $completionTokens,
                ],
            );
        } catch (\Throwable $e) {
            $this->errorCount++;
            throw new RuntimeException("Inference failed: {$e->getMessage()}", 0, $e);
        }
    }

    public function getStats(): array
    {
        return [
            'model_id' => $this->modelId,
            'total_requests' => $this->totalRequests,
            'error_count' => $this->errorCount,
            'avg_latency_ms' => $this->totalRequests > 0
                ? round($this->totalLatency / $this->totalRequests, 2)
                : 0.0,
        ];
    }

    private function processInference(InferenceRequest $request): string
    {
        return "Response for: " . substr($request->prompt, 0, 100);
    }
}
