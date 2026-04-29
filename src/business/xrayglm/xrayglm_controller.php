<?php
namespace OmniBatch9\Business;

class OmniResult {
    public bool $isOk;
    public $value;
    public ?string $error;
    public function __construct(bool $ok, $value = null, ?string $error = null) {
        $this->isOk = $ok; $this->value = $value; $this->error = $error;
    }
}

class XrayGLMController {
    const MAX_IMAGE_SIZE = 50 * 1024 * 1024; // 50MB
    const ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/dicom'];

    public function uploadImage(string $imageData, string $mimeType): OmniResult {
        if (empty($imageData)) return new OmniResult(false, null, "Empty image data");
        if (strlen($imageData) > self::MAX_IMAGE_SIZE) return new OmniResult(false, null, "Image exceeds 50MB");
        if (!in_array($mimeType, self::ALLOWED_TYPES)) return new OmniResult(false, null, "Unsupported MIME type");
        return new OmniResult(true, ['size' => strlen($imageData), 'type' => $mimeType]);
    }

    public function getDiagnosis(string $imageId): OmniResult {
        if (empty($imageId)) return new OmniResult(false, null, "Missing image ID");
        if (strlen($imageId) > 128) return new OmniResult(false, null, "Invalid image ID");
        return new OmniResult(true, ['image_id' => $imageId, 'status' => 'processed']);
    }
}
