<?php
namespace OmniFramework\Business\Legacy;

use PDO;
use Exception;

class OmniDBError extends Exception {}

class CMSBridge {
    private PDO $pdo;

    public function __construct(string $dsn, string $user, string $pass) {
        try {
            $this->pdo = new PDO($dsn, $user, $pass, [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
            ]);
        } catch (\PDOException $e) {
            throw new OmniDBError("Failed to connect to legacy CMS: " . $e->getMessage());
        }
    }

    public function fetchActiveUsers(): array {
        try {
            $stmt = $this->pdo->prepare("SELECT id, email FROM users WHERE status = 'active'");
            $stmt->execute();
            return $stmt->fetchAll();
        } catch (\PDOException $e) {
            throw new OmniDBError("Query failed: " . $e->getMessage());
        }
    }
}
