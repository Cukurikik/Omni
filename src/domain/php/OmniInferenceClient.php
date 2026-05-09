<?php
/**
 * OMNI Business Layer — PHP Inference API Client
 * PSR-compatible HTTP client for OMNI inference services.
 */

declare(strict_types=1);

namespace Omni\Client;

class InferenceConfig
{
    public string $baseUrl;
    public int $timeoutSeconds;
    public int $maxRetries;
    public string $apiKey;

    public function __construct(
        string $baseUrl = 'http://localhost:8080/api/v1',
        int $timeoutSeconds = 30,
        int $maxRetries = 3,
        string $apiKey = ''
    ) {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->timeoutSeconds = $timeoutSeconds;
        $this->maxRetries = $maxRetries;
        $this->apiKey = $apiKey;
    }
}

class InferenceResult
{
    public string $text;
    public int $tokens;
    public float $latencyMs;
    public string $requestId;
    public string $model;

    public function __construct(array $data)
    {
        $this->text = $data['generated_text'] ?? '';
        $this->tokens = $data['tokens_generated'] ?? 0;
        $this->latencyMs = $data['latency_ms'] ?? 0.0;
        $this->requestId = $data['request_id'] ?? '';
        $this->model = $data['model'] ?? '';
    }
}

class OmniInferenceClient
{
    private InferenceConfig $config;
    private array $stats = ['requests' => 0, 'errors' => 0, 'totalLatency' => 0.0];

    public function __construct(InferenceConfig $config)
    {
        $this->config = $config;
    }

    public function infer(string $prompt, array $options = []): InferenceResult
    {
        $payload = [
            'prompt' => $prompt,
            'max_tokens' => $options['max_tokens'] ?? 256,
            'temperature' => $options['temperature'] ?? 0.7,
            'top_p' => $options['top_p'] ?? 0.9,
        ];

        $start = microtime(true);
        $response = $this->request('POST', '/infer', $payload);
        $latency = (microtime(true) - $start) * 1000;

        $this->stats['requests']++;
        $this->stats['totalLatency'] += $latency;

        $response['latency_ms'] = $latency;
        return new InferenceResult($response);
    }

    public function embed(array $texts): array
    {
        return $this->request('POST', '/embed', ['texts' => $texts]);
    }

    public function health(): array
    {
        return $this->request('GET', '/health');
    }

    public function getStats(): array
    {
        $avg = $this->stats['requests'] > 0
            ? $this->stats['totalLatency'] / $this->stats['requests'] : 0;
        return array_merge($this->stats, ['avgLatencyMs' => round($avg, 2)]);
    }

    private function request(string $method, string $path, array $body = []): array
    {
        $url = $this->config->baseUrl . $path;
        $attempt = 0;

        while ($attempt < $this->config->maxRetries) {
            $attempt++;
            $ch = curl_init();
            curl_setopt_array($ch, [
                CURLOPT_URL => $url,
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_TIMEOUT => $this->config->timeoutSeconds,
                CURLOPT_HTTPHEADER => array_filter([
                    'Content-Type: application/json',
                    $this->config->apiKey ? "Authorization: Bearer {$this->config->apiKey}" : null,
                ]),
            ]);

            if ($method === 'POST') {
                curl_setopt($ch, CURLOPT_POST, true);
                curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($body));
            }

            $response = curl_exec($ch);
            $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            $error = curl_error($ch);
            curl_close($ch);

            if ($response !== false && $httpCode >= 200 && $httpCode < 300) {
                return json_decode($response, true) ?? [];
            }

            if ($httpCode >= 500 && $attempt < $this->config->maxRetries) {
                usleep(min(1000000, 100000 * (2 ** $attempt))); // Exponential backoff
                continue;
            }

            $this->stats['errors']++;
            throw new \RuntimeException("API error ($httpCode): $error - $response");
        }

        throw new \RuntimeException("Max retries exceeded for $url");
    }
}
