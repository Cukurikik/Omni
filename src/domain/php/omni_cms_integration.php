<?php
declare(strict_types=1);

namespace Omni\Domain\CMS;

/**
 * OMNI MOTHER: Legacy PHP CMS Integration (Production Grade)
 * Synchronizes users between Omni and legacy WordPress/Drupal installations.
 */
class CmsSyncService {
    private \PDO $db;

    public function __construct(\PDO $db) {
        $this->db = $db;
    }

    public function syncUser(string $omniUserId, string $email, string $name): bool {
        try {
            $stmt = $this->db->prepare("
                INSERT INTO wp_users (user_login, user_email, display_name, user_registered) 
                VALUES (:login, :email, :name, NOW())
                ON DUPLICATE KEY UPDATE display_name = :name_update
            ");
            
            return $stmt->execute([
                ':login' => 'omni_' . $omniUserId,
                ':email' => $email,
                ':name' => $name,
                ':name_update' => $name
            ]);
        } catch (\PDOException $e) {
            error_log("[OMNI PHP] CMS Sync Failed: " . $e->getMessage());
            return false;
        }
    }
}
