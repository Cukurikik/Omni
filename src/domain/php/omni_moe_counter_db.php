<?php
// OMNI MOTHER: PHP Moe-Counter Database Abstraction (Production Grade)
// Handles secure PDO connections and schema initialization.

declare(strict_types=1);

namespace Omni\Counter;

class DatabaseConnector {
    private \PDO $connection;

    public function __construct(string $host, string $db, string $user, string $pass) {
        $dsn = "mysql:host=$host;dbname=$db;charset=utf8mb4";
        $options = [
            \PDO::ATTR_ERRMODE            => \PDO::ERRMODE_EXCEPTION,
            \PDO::ATTR_DEFAULT_FETCH_MODE => \PDO::FETCH_ASSOC,
            \PDO::ATTR_EMULATE_PREPARES   => false,
            \PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"
        ];

        try {
            $this->connection = new \PDO($dsn, $user, $pass, $options);
            $this->initializeSchema();
        } catch (\PDOException $e) {
            error_log("[OMNI DB] Connection failed: " . $e->getMessage());
            throw new \RuntimeException("Database connection failed.");
        }
    }

    public function getConnection(): \PDO {
        return $this->connection;
    }

    private function initializeSchema(): void {
        $this->connection->exec("
            CREATE TABLE IF NOT EXISTS site_stats (
                site_id VARCHAR(64) PRIMARY KEY,
                total_hits BIGINT UNSIGNED NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
        ");

        $this->connection->exec("
            CREATE TABLE IF NOT EXISTS visitor_logs (
                id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                site_id VARCHAR(64) NOT NULL,
                visitor_hash VARCHAR(64) NOT NULL,
                visited_at DATETIME NOT NULL,
                UNIQUE KEY unique_visitor_per_day (site_id, visitor_hash, visited_at)
            ) ENGINE=InnoDB;
        ");
    }
}
