<?php
namespace Omni\Domain\Legacy;

class Result {
    public readonly bool $isSuccess;
    public readonly mixed $value;
    public readonly ?string $error;

    private function __construct(bool $isSuccess, mixed $value, ?string $error) {
        $this->isSuccess = $isSuccess;
        $this->value = $value;
        $this->error = $error;
    }

    public static function ok(mixed $value): self {
        return new self(true, $value, null);
    }

    public static function err(string $error): self {
        return new self(false, null, $error);
    }
}

/**
 * Omni PHP Legacy Bridge Controller
 * Interfaces enterprise CMS endpoints into Omni Polyglot Space.
 */
class OmniLegacyBridgeController {
    
    public function sanitizePayload(array $payload): Result {
        if (empty($payload)) {
            return Result::err("Payload cannot be empty");
        }

        $sanitized = [];
        foreach ($payload as $key => $value) {
            // Deterministic sanitization logic
            $sanitized[strip_tags($key)] = htmlspecialchars((string)$value, ENT_QUOTES, 'UTF-8');
        }

        return Result::ok($sanitized);
    }
}
