<?php
// @omni-layer Business | @omni-lang PHP | @omni-batch 17
// @omni-description REST API gateway: PHP 8.3 typed service for model inference
// routing, request validation, quota enforcement, and response caching.

declare(strict_types=1);

namespace Omni\Business\Gateway;

enum InferenceStatus: string {
    case Pending = 'pending';
    case Processing = 'processing';
    case Completed = 'completed';
    case Failed = 'failed';
}

readonly class OmniResult {
    public function __construct(
        public readonly mixed $data = null,
        public readonly ?string $error = null,
    ) {}

    public function isOk(): bool {
        return $this->error === null;
    }
}

readonly class InferenceRequest {
    public function __construct(
        public readonly string $id,
        public readonly string $modelId,
        public readonly string $text,
        public readonly string $taskType,
        public readonly float $temperature = 1.0,
        public readonly int $maxTokens = 100,
    ) {}
}

readonly class InferenceResponse {
    public function __construct(
        public readonly string $requestId,
        public readonly string $modelId,
        public readonly array $output,
        public readonly float $confidence,
        public readonly float $latencyMs,
        public readonly InferenceStatus $status,
    ) {}

    public function toArray(): array {
        return [
            'request_id' => $this->requestId,
            'model_id' => $this->modelId,
            'output' => $this->output,
            'confidence' => $this->confidence,
            'latency_ms' => $this->latencyMs,
            'status' => $this->status->value,
        ];
    }
}

class QuotaManager {
    private array $usage = [];
    private int $dailyLimit;

    public function __construct(int $dailyLimit = 10000) {
        $this->dailyLimit = $dailyLimit;
    }

    public function checkQuota(string $userId): OmniResult {
        $used = $this->usage[$userId] ?? 0;
        if ($used >= $this->dailyLimit) {
            return new OmniResult(error: "Quota exceeded for user {$userId}");
        }
        return new OmniResult(data: ['remaining' => $this->dailyLimit - $used]);
    }

    public function recordUsage(string $userId, int $tokens): void {
        $this->usage[$userId] = ($this->usage[$userId] ?? 0) + $tokens;
    }
}

class InferenceGateway {
    private array $responseCache = [];
    private array $requestLog = [];
    private QuotaManager $quotaManager;
    private int $processedCount = 0;

    public function __construct(int $dailyLimit = 10000) {
        $this->quotaManager = new QuotaManager($dailyLimit);
    }

    public function processRequest(InferenceRequest $req, string $userId): OmniResult {
        // Check quota
        $quotaResult = $this->quotaManager->checkQuota($userId);
        if (!$quotaResult->isOk()) {
            return $quotaResult;
        }

        // Check cache
        $cacheKey = md5($req->modelId . $req->text . $req->taskType);
        if (isset($this->responseCache[$cacheKey])) {
            return new OmniResult(data: $this->responseCache[$cacheKey]);
        }

        // Process inference
        $start = hrtime(true);
        $output = $this->computeInference($req);
        $latency = (hrtime(true) - $start) / 1e6;

        $response = new InferenceResponse(
            requestId: $req->id,
            modelId: $req->modelId,
            output: $output,
            confidence: $this->computeConfidence($output),
            latencyMs: $latency,
            status: InferenceStatus::Completed,
        );

        // Cache and log
        $this->responseCache[$cacheKey] = $response->toArray();
        $this->requestLog[] = ['userId' => $userId, 'requestId' => $req->id, 'latency' => $latency];
        $this->quotaManager->recordUsage($userId, $req->maxTokens);
        $this->processedCount++;

        return new OmniResult(data: $response->toArray());
    }

    public function stats(): array {
        $latencies = array_column($this->requestLog, 'latency');
        return [
            'processed' => $this->processedCount,
            'cached' => count($this->responseCache),
            'avg_latency_ms' => count($latencies) > 0 ? array_sum($latencies) / count($latencies) : 0,
        ];
    }

    private function computeInference(InferenceRequest $req): array {
        $hash = crc32($req->text);
        return [abs($hash) % 32000, abs($hash * 7 + 42) % 32000, abs($hash * 13 + 99) % 32000];
    }

    private function computeConfidence(array $output): float {
        $sum = array_sum($output);
        return $sum > 0 ? min(1.0, log1p((float)$sum) / 10.0) : 0.0;
    }
}
