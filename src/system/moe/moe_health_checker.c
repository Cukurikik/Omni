// moe_health_checker.c — Low-Level MoE Expert Health Monitor
// Layer: System / Health — MoE Runtime Diagnostics
//
// C-native health checker for MoE expert processes:
// - Watchdog timers for hung experts
// - Memory leak detection
// - NaN/Inf detection in expert outputs
// - Expert liveness probing

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define MOE_MAX_EXPERTS 256
#define MOE_HEALTH_OK 0
#define MOE_HEALTH_TIMEOUT 1
#define MOE_HEALTH_NAN_DETECTED 2
#define MOE_HEALTH_MEM_LEAK 3
#define MOE_HEALTH_DEAD 4

typedef struct {
    int expert_id;
    int status;
    int64_t last_heartbeat_us;
    int64_t timeout_us;
    int64_t tokens_processed;
    int64_t nan_count;
    int64_t inf_count;
    size_t memory_baseline;
    size_t memory_current;
    size_t memory_peak;
    int consecutive_failures;
    int max_consecutive_failures;
} ExpertHealthState;

typedef struct {
    ExpertHealthState experts[MOE_MAX_EXPERTS];
    int num_experts;
    int64_t check_interval_us;
    int64_t global_start_us;
    int total_checks;
    int total_alerts;
} MoEHealthChecker;

static int64_t current_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000000LL + ts.tv_nsec / 1000;
}

/**
 * Initialize the health checker.
 */
int moe_health_init(
    MoEHealthChecker* checker,
    int num_experts,
    int64_t timeout_us,
    int64_t check_interval_us,
    int max_failures
) {
    if (!checker || num_experts <= 0 || num_experts > MOE_MAX_EXPERTS) {
        return -1;
    }

    memset(checker, 0, sizeof(*checker));
    checker->num_experts = num_experts;
    checker->check_interval_us = check_interval_us;
    checker->global_start_us = current_time_us();

    for (int i = 0; i < num_experts; i++) {
        ExpertHealthState* e = &checker->experts[i];
        e->expert_id = i;
        e->status = MOE_HEALTH_OK;
        e->last_heartbeat_us = current_time_us();
        e->timeout_us = timeout_us;
        e->tokens_processed = 0;
        e->nan_count = 0;
        e->inf_count = 0;
        e->memory_baseline = 0;
        e->memory_current = 0;
        e->memory_peak = 0;
        e->consecutive_failures = 0;
        e->max_consecutive_failures = max_failures;
    }

    return 0;
}

/**
 * Record a heartbeat from an expert.
 */
void moe_health_heartbeat(MoEHealthChecker* checker, int expert_id) {
    if (!checker || expert_id < 0 || expert_id >= checker->num_experts) return;
    ExpertHealthState* e = &checker->experts[expert_id];
    e->last_heartbeat_us = current_time_us();
    e->consecutive_failures = 0;
    if (e->status == MOE_HEALTH_TIMEOUT || e->status == MOE_HEALTH_DEAD) {
        e->status = MOE_HEALTH_OK;
    }
}

/**
 * Check expert output for NaN/Inf values.
 * Returns number of invalid values detected.
 */
int moe_health_check_output(
    MoEHealthChecker* checker,
    int expert_id,
    const float* output,
    int output_len
) {
    if (!checker || !output || expert_id < 0 || expert_id >= checker->num_experts) {
        return -1;
    }

    ExpertHealthState* e = &checker->experts[expert_id];
    int invalid = 0;

    for (int i = 0; i < output_len; i++) {
        if (isnan(output[i])) {
            e->nan_count++;
            invalid++;
        } else if (isinf(output[i])) {
            e->inf_count++;
            invalid++;
        }
    }

    if (invalid > 0) {
        e->status = MOE_HEALTH_NAN_DETECTED;
        e->consecutive_failures++;
    } else {
        e->tokens_processed++;
    }

    return invalid;
}

/**
 * Update memory tracking for an expert.
 */
void moe_health_update_memory(
    MoEHealthChecker* checker,
    int expert_id,
    size_t current_bytes
) {
    if (!checker || expert_id < 0 || expert_id >= checker->num_experts) return;
    ExpertHealthState* e = &checker->experts[expert_id];

    if (e->memory_baseline == 0) {
        e->memory_baseline = current_bytes;
    }
    e->memory_current = current_bytes;
    if (current_bytes > e->memory_peak) {
        e->memory_peak = current_bytes;
    }

    /* Detect memory leak: >50% growth over baseline */
    if (e->memory_baseline > 0 &&
        current_bytes > e->memory_baseline * 3 / 2) {
        e->status = MOE_HEALTH_MEM_LEAK;
    }
}

/**
 * Run health check on all experts.
 * Returns number of unhealthy experts.
 */
int moe_health_check_all(MoEHealthChecker* checker) {
    if (!checker) return -1;

    int64_t now = current_time_us();
    int unhealthy = 0;

    for (int i = 0; i < checker->num_experts; i++) {
        ExpertHealthState* e = &checker->experts[i];

        /* Check timeout */
        if (now - e->last_heartbeat_us > e->timeout_us) {
            if (e->status != MOE_HEALTH_DEAD) {
                e->status = MOE_HEALTH_TIMEOUT;
                e->consecutive_failures++;
            }
        }

        /* Check if expert should be marked dead */
        if (e->consecutive_failures >= e->max_consecutive_failures) {
            e->status = MOE_HEALTH_DEAD;
        }

        if (e->status != MOE_HEALTH_OK) {
            unhealthy++;
        }
    }

    checker->total_checks++;
    checker->total_alerts += unhealthy;

    return unhealthy;
}

/**
 * Get health status for a specific expert.
 */
int moe_health_get_status(const MoEHealthChecker* checker, int expert_id) {
    if (!checker || expert_id < 0 || expert_id >= checker->num_experts) {
        return MOE_HEALTH_DEAD;
    }
    return checker->experts[expert_id].status;
}

/**
 * Get list of healthy expert IDs.
 */
int moe_health_get_healthy(
    const MoEHealthChecker* checker,
    int* out_ids,
    int max_out
) {
    if (!checker || !out_ids) return 0;
    int count = 0;
    for (int i = 0; i < checker->num_experts && count < max_out; i++) {
        if (checker->experts[i].status == MOE_HEALTH_OK) {
            out_ids[count++] = i;
        }
    }
    return count;
}

/**
 * Generate a health report string.
 */
int moe_health_report(
    const MoEHealthChecker* checker,
    char* buf,
    int buf_size
) {
    if (!checker || !buf || buf_size <= 0) return -1;

    int ok = 0, timeout = 0, nan = 0, mem = 0, dead = 0;
    for (int i = 0; i < checker->num_experts; i++) {
        switch (checker->experts[i].status) {
            case MOE_HEALTH_OK: ok++; break;
            case MOE_HEALTH_TIMEOUT: timeout++; break;
            case MOE_HEALTH_NAN_DETECTED: nan++; break;
            case MOE_HEALTH_MEM_LEAK: mem++; break;
            case MOE_HEALTH_DEAD: dead++; break;
        }
    }

    return snprintf(buf, buf_size,
        "MoE Health: %d OK, %d timeout, %d NaN, %d memLeak, %d dead "
        "| checks=%d alerts=%d",
        ok, timeout, nan, mem, dead,
        checker->total_checks, checker->total_alerts);
}

/**
 * Reset an expert's health state (e.g., after restart).
 */
void moe_health_reset_expert(MoEHealthChecker* checker, int expert_id) {
    if (!checker || expert_id < 0 || expert_id >= checker->num_experts) return;
    ExpertHealthState* e = &checker->experts[expert_id];
    e->status = MOE_HEALTH_OK;
    e->last_heartbeat_us = current_time_us();
    e->consecutive_failures = 0;
    e->nan_count = 0;
    e->inf_count = 0;
}
