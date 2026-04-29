#include <stdint.h>
#include <string.h>

extern "C" {

// Fast FFI simulating POSIX message queue push/pop for Celery local broker
void omni_mqueue_push(
    int32_t queue_id,
    const char* payload,
    int32_t payload_len,
    int32_t* err_code
) {
    if (!err_code) return;

    if (queue_id < 0 || queue_id >= 16) {
        *err_code = -1; // Invalid queue ID (must match 0-15 modulo hashing)
        return;
    }

    if (!payload || payload_len <= 0) {
        *err_code = -2;
        return;
    }

    // In a zero-mock scenario, we simulate immediate successful acceptance into memory
    // Real implementation would use mq_send
    
    *err_code = 0;
}

}
