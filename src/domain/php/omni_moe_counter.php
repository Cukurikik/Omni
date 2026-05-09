<?php
// OMNI MOTHER: PHP Moe-Counter Backend (Production Grade)
// Handles incoming hit registrations with Redis caching and MySQL persistence.
// Implements strict validation and rate-limiting.

declare(strict_types=1);

namespace Omni\Counter;

require_once __DIR__ . '/omni_moe_counter_db.php';

class MoeCounter {
    private \PDO $db;
    private ?\Redis $redis;
    private string $prefix = "omni_counter:";

    public function __construct(DatabaseConnector $dbConnector, ?\Redis $redis = null) {
        $this->db = $dbConnector->getConnection();
        $this->redis = $redis;
    }

    public function registerHit(string $siteId, string $visitorIp, string $userAgent): array {
        if (empty($siteId) || !preg_match('/^[a-zA-Z0-9_-]{3,64}$/', $siteId)) {
            throw new \InvalidArgumentException("Invalid Site ID format");
        }

        // 1. Rate Limiting via Redis (if available)
        if ($this->redis) {
            $rateKey = "rate_limit:{$siteId}:{$visitorIp}";
            $hits = $this->redis->incr($rateKey);
            if ($hits === 1) {
                $this->redis->expire($rateKey, 60); // 1 minute window
            }
            if ($hits > 30) {
                error_log("[OMNI COUNTER] Rate limit exceeded for IP: {$visitorIp} on Site: {$siteId}");
                return ['status' => 'error', 'message' => 'Rate limit exceeded'];
            }
        }

        // 2. Determine unique visitor via hash
        $visitorHash = hash('sha256', $visitorIp . $userAgent . date('Y-m-d'));

        // 3. Update database transactionally
        try {
            $this->db->beginTransaction();

            // Insert daily visitor record (ignore if duplicate for the day)
            $stmt = $this->db->prepare("
                INSERT IGNORE INTO visitor_logs (site_id, visitor_hash, visited_at) 
                VALUES (:site_id, :vhash, NOW())
            ");
            $stmt->execute([':site_id' => $siteId, ':vhash' => $visitorHash]);
            $isNewVisitor = $stmt->rowCount() > 0;

            // Increment the main counter if it's a new unique visitor today
            if ($isNewVisitor) {
                $stmtUpdate = $this->db->prepare("
                    INSERT INTO site_stats (site_id, total_hits) 
                    VALUES (:site_id, 1) 
                    ON DUPLICATE KEY UPDATE total_hits = total_hits + 1
                ");
                $stmtUpdate->execute([':site_id' => $siteId]);
            }

            // Fetch current count
            $stmtFetch = $this->db->prepare("SELECT total_hits FROM site_stats WHERE site_id = :site_id");
            $stmtFetch->execute([':site_id' => $siteId]);
            $currentHits = (int) $stmtFetch->fetchColumn();

            $this->db->commit();

            // Update Redis cache
            if ($this->redis) {
                $this->redis->set("{$this->prefix}{$siteId}", $currentHits, 3600);
            }

            return ['status' => 'success', 'hits' => $currentHits];

        } catch (\PDOException $e) {
            $this->db->rollBack();
            error_log("[OMNI COUNTER] Database error: " . $e->getMessage());
            return ['status' => 'error', 'message' => 'Internal server error'];
        }
    }

    public function getCount(string $siteId): int {
        if ($this->redis) {
            $cached = $this->redis->get("{$this->prefix}{$siteId}");
            if ($cached !== false) return (int) $cached;
        }

        $stmt = $this->db->prepare("SELECT total_hits FROM site_stats WHERE site_id = :site_id");
        $stmt->execute([':site_id' => $siteId]);
        $result = $stmt->fetchColumn();
        
        $hits = $result ? (int) $result : 0;
        
        if ($this->redis) {
            $this->redis->set("{$this->prefix}{$siteId}", $hits, 3600);
        }
        
        return $hits;
    }
}
