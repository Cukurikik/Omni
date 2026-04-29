<?php
declare(strict_types=1);

namespace Omni\Semester14\Batch8\Petals;

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

class PetalsAuthDomain {
    private const MAX_TOKEN_LENGTH = 1024;
    
    public function validateShardToken(string $token, string $nodeId): OmniResult {
        if (empty($token) || empty($nodeId)) {
            return OmniResult::err("OMNI_AUTH_001: Token and Node ID required");
        }
        
        if (strlen($token) > self::MAX_TOKEN_LENGTH) {
            return OmniResult::err("OMNI_LIMIT: Token length exceeds maximum allowed");
        }
        
        // Validate JWT format structure (header.payload.signature)
        $parts = explode('.', $token);
        if (count($parts) !== 3) {
            return OmniResult::err("OMNI_AUTH_002: Malformed authorization token");
        }
        
        // FFI Call down to Zig Crypto Layer would happen here
        // For now, return validated success
        return OmniResult::ok([
            'authorized' => true,
            'node_id' => $nodeId,
            'permissions' => ['read_shard', 'compute_shard']
        ]);
    }
}
