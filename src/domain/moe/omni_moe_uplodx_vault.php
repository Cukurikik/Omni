<?php

namespace Omni\Domain\MoE;

/**
 * OMNI MOTHER Production Zero-Mock Secure Upload Vault
 * Handles massive payload uploads (e.g. custom LoRA weights or RAG docs)
 * validating MIME types, chunking, and moving to secure storage.
 */
class UplodxVault {
    private string $storagePath;
    private array $allowedMimes = [
        'application/octet-stream', // Safetensors/Bin
        'application/json',
        'text/plain'
    ];

    public function __construct(string $storagePath = '/opt/omni/vault/') {
        $this->storagePath = $storagePath;
        if (!is_dir($this->storagePath)) {
            mkdir($this->storagePath, 0755, true);
        }
    }

    public function receiveChunk(string $tempFilePath, string $originalName, string $uploadId, int $chunkIndex, int $totalChunks): bool {
        // Basic Security Validation
        $finfo = finfo_open(FILEINFO_MIME_TYPE);
        $mime = finfo_file($finfo, $tempFilePath);
        finfo_close($finfo);

        if (!in_array($mime, $this->allowedMimes)) {
            error_log("OMNI SECURE: Invalid MIME type detected: $mime");
            return false;
        }

        // Prevent path traversal
        $safeName = basename($uploadId . "_" . $originalName);
        $targetFile = $this->storagePath . $safeName . ".part";

        // Append chunk
        $chunkData = file_get_contents($tempFilePath);
        if (file_put_contents($targetFile, $chunkData, FILE_APPEND | LOCK_EX) === false) {
            error_log("OMNI CRITICAL: Failed to write chunk to vault.");
            return false;
        }

        // If last chunk, rename file to complete
        if ($chunkIndex == $totalChunks - 1) {
            $finalFile = $this->storagePath . $safeName;
            rename($targetFile, $finalFile);
            error_log("OMNI SYSTEM: Assembly complete for $finalFile");
        }

        return true;
    }
}
