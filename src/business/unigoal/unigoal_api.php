<?php
declare(strict_types=1);

namespace Omni\Semester14\Batch8\UniGoal;

// OMNI PHP routing bridge
// No frameworks, pure PHP 8+ strict types

class OmniResult {
    public readonly mixed $payload;
    public readonly ?string $error;
    public readonly bool $isOk;

    private function __construct(mixed $payload, ?string $error, bool $isOk) {
        $this->payload = $payload;
        $this->error = $error;
        $this->isOk = $isOk;
    }

    public static function ok(mixed $payload): self {
        return new self($payload, null, true);
    }

    public static function err(string $error): self {
        return new self(null, $error, false);
    }
}

class UniGoalRouter {
    private const ALLOWED_ENDPOINTS = ['/api/rl/status', '/api/rl/trigger'];

    public function handleRequest(string $uri, string $method): OmniResult {
        if (!in_array($uri, self::ALLOWED_ENDPOINTS)) {
            return OmniResult::err("OMNI_HTTP_404: Endpoint not found in UniGoal Router");
        }

        if ($method !== 'GET' && $method !== 'POST') {
             return OmniResult::err("OMNI_HTTP_405: Method not allowed");
        }

        // Simulate routing to Mojo Compute Layer via FFI bridge
        return OmniResult::ok([
            'routed_to' => $uri,
            'status' => 'delegated_to_omni_bridge'
        ]);
    }
}
