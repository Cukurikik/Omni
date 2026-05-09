<?php

namespace Omni\Domain\MoE;

/**
 * OMNI MOTHER Production Zero-Mock Model Registry
 * Central PHP Authority managing versioning, paths, and metadata
 * for dynamically loading Safetensors models.
 */
class ModelRegistry {
    private \PDO $db;

    public function __construct(\PDO $db) {
        $this->db = $db;
    }

    public function registerModel(string $modelId, string $version, string $fsPath, int $paramCount): bool {
        if (!file_exists($fsPath)) {
            error_log("OMNI CRITICAL: Registration failed. File not found at $fsPath");
            return false;
        }

        try {
            $stmt = $this->db->prepare("
                INSERT INTO model_registry (model_id, version, file_path, parameter_count, is_active, created_at)
                VALUES (:id, :ver, :path, :params, 1, NOW())
                ON DUPLICATE KEY UPDATE file_path = :path, parameter_count = :params, is_active = 1
            ");
            
            return $stmt->execute([
                ':id' => $modelId,
                ':ver' => $version,
                ':path' => $fsPath,
                ':params' => $paramCount
            ]);
        } catch (\PDOException $e) {
            error_log("OMNI CRITICAL: DB Error in Model Registry: " . $e->getMessage());
            return false;
        }
    }

    public function getActiveModelPath(string $modelId): ?string {
        $stmt = $this->db->prepare("SELECT file_path FROM model_registry WHERE model_id = :id AND is_active = 1 ORDER BY version DESC LIMIT 1");
        $stmt->execute([':id' => $modelId]);
        
        $result = $stmt->fetchColumn();
        return $result !== false ? (string)$result : null;
    }
}
