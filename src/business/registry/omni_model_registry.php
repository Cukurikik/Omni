<?php
namespace Omni\Registry;

use Exception;
use PDO;

/**
 * Omni Model Registry (PHP)
 * Business Layer
 * Exposes a robust web API to manage the lifecycle of Omni Transformer models.
 * Integrates with standard enterprise relational databases.
 */
class ModelRegistry {
    private PDO $db;

    public function __construct(PDO $db_connection) {
        $this->db = $db_connection;
    }

    public function registerModel(string $name, string $architecture, string $s3Path, string $checksum): int {
        $stmt = $this->db->prepare(
            "INSERT INTO omni_models (name, architecture, path, checksum, created_at) 
             VALUES (:name, :arch, :path, :checksum, NOW())"
        );
        
        $stmt->execute([
            ':name' => $name,
            ':arch' => $architecture,
            ':path' => $s3Path,
            ':checksum' => $checksum
        ]);

        return (int)$this->db->lastInsertId();
    }

    public function getModelMetadata(int $id): ?array {
        $stmt = $this->db->prepare("SELECT * FROM omni_models WHERE id = :id AND is_active = 1");
        $stmt->execute([':id' => $id]);
        $result = $stmt->fetch(PDO::FETCH_ASSOC);
        
        return $result ? $result : null;
    }

    public function deprecateModel(int $id): bool {
        $stmt = $this->db->prepare("UPDATE omni_models SET is_active = 0 WHERE id = :id");
        return $stmt->execute([':id' => $id]);
    }

    /**
     * Retrieves all models matching an architecture for distributed load balancing.
     */
    public function getModelsByArchitecture(string $architecture): array {
        $stmt = $this->db->prepare("SELECT id, name, path FROM omni_models WHERE architecture = :arch AND is_active = 1");
        $stmt->execute([':arch' => $architecture]);
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
}
?>
