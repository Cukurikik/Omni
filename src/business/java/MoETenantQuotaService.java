package dev.omniframework.tenant;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.web.bind.annotation.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;

import java.util.concurrent.TimeUnit;

/**
 * OMNI Framework - Tenant Quota Service (Java/Spring Boot)
 * Handles fast validation and decrementing of tenant token quotas using Redis.
 * This is queried by the Go API Gateway before routing to the C++ inference engine.
 */
@SpringBootApplication
@RestController
@RequestMapping("/api/v1/tenant")
public class MoETenantQuotaService {

    @Autowired
    private StringRedisTemplate redisTemplate;

    public static void main(String[] args) {
        SpringApplication.run(MoETenantQuotaService.class, args);
        System.out.println("OMNI Java: MoE Tenant Quota Service running.");
    }

    @PostMapping("/{tenantId}/consume")
    public ResponseEntity<QuotaResponse> consumeQuota(
            @PathVariable String tenantId,
            @RequestParam long tokens) {
        
        String key = "tenant:quota:" + tenantId;
        
        // Use Redis decrement operation for atomicity
        Long remaining = redisTemplate.opsForValue().decrement(key, tokens);
        
        if (remaining == null) {
            // Tenant key doesn't exist, initialize with default free tier (e.g., 10k tokens)
            redisTemplate.opsForValue().set(key, String.valueOf(10000 - tokens), 30, TimeUnit.DAYS);
            remaining = 10000L - tokens;
        }

        if (remaining < 0) {
            // Revert the deduction if they didn't have enough
            redisTemplate.opsForValue().increment(key, tokens);
            return ResponseEntity.status(429).body(new QuotaResponse(false, 0, "Insufficient quota."));
        }

        return ResponseEntity.ok(new QuotaResponse(true, remaining, "Quota consumed successfully."));
    }

    static class QuotaResponse {
        public boolean allowed;
        public long remainingTokens;
        public String message;

        public QuotaResponse(boolean allowed, long remainingTokens, String message) {
            this.allowed = allowed;
            this.remainingTokens = remainingTokens;
            this.message = message;
        }
    }
}
