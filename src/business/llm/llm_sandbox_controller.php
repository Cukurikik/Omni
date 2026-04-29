<?php
namespace OmniBatch9\Business;

class LLMSandboxController {
    const MAX_CODE_SIZE = 1000000; // 1MB
    const ALLOWED_LANGS = ['python', 'javascript', 'bash'];
    const MAX_TIMEOUT = 300; // 5min

    public function executeCode(string $code, string $language, int $timeoutSec = 30): OmniResult {
        if (empty($code)) return new OmniResult(false, null, "Empty code");
        if (strlen($code) > self::MAX_CODE_SIZE) return new OmniResult(false, null, "Code exceeds 1MB");
        if (!in_array($language, self::ALLOWED_LANGS)) return new OmniResult(false, null, "Unsupported language: $language");
        if ($timeoutSec < 1 || $timeoutSec > self::MAX_TIMEOUT) return new OmniResult(false, null, "Timeout out of range");
        return new OmniResult(true, ['language' => $language, 'size' => strlen($code), 'timeout' => $timeoutSec]);
    }
}
