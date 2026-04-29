<?php
// OMNI Divine Memory Integration: Inspired by awesome-pretrained-chinese-nlp-models
// Business Layer - PHP Routing for Metadata on Chinese NLP Models

namespace Omni\Semester14\Batch5;

class OmniError extends \Exception {
    public int $statusCode;
    public function __construct(string $message, int $code) {
        parent::__construct($message, 0, null);
        $this->statusCode = $code;
    }
}

class OmniResult {
    public bool $isOk;
    public mixed $value;
    public ?OmniError $error;

    private function __construct(bool $ok, mixed $val, ?OmniError $err) {
        $this->isOk = $ok;
        $this->value = $val;
        $this->error = $err;
    }

    public static function Ok(mixed $val): self {
        return new self(true, $val, null);
    }

    public static function Err(OmniError $err): self {
        return new self(false, null, $err);
    }
}

class ChineseNLPRouter {
    const MAX_MODEL_REGISTRY_SIZE = 1000;

    private array $models = [];

    public function registerModel(string $modelId, string $metadataJson): OmniResult {
        if (count($this->models) >= self::MAX_MODEL_REGISTRY_SIZE) {
            return OmniResult::Err(new OmniError("Registry bound of 1000 models exceeded.", 413));
        }

        $decoded = json_decode($metadataJson, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            return OmniResult::Err(new OmniError("Invalid JSON metadata mapping.", 400));
        }

        // Zero-mock registration
        $this->models[$modelId] = $decoded;

        return OmniResult::Ok(true);
    }

    public function getModel(string $modelId): OmniResult {
        if (!isset($this->models[$modelId])) {
            return OmniResult::Err(new OmniError("Model not found in registry.", 404));
        }
        return OmniResult::Ok($this->models[$modelId]);
    }
}
