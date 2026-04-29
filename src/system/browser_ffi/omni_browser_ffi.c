#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* OMNI Browser FFI Engine — System Layer
 * Absorbing psyb0t/uzdabrawza browser automation concepts at the FFI boundary.
 * Provides zero-copy DOM action serialization for cross-language browser control.
 */

typedef enum {
    BFFI_OK = 0,
    BFFI_ERR_NULL = -1,
    BFFI_ERR_OVERFLOW = -2,
    BFFI_ERR_INVALID_ACTION = -3
} BffiResult;

typedef enum {
    ACTION_CLICK = 1,
    ACTION_TYPE = 2,
    ACTION_NAVIGATE = 3,
    ACTION_SCREENSHOT = 4,
    ACTION_SCROLL = 5,
    ACTION_WAIT = 6
} BrowserAction;

typedef struct {
    BrowserAction action;
    uint16_t selector_len;
    char selector[512];
    char payload[1024];
    uint16_t payload_len;
    uint32_t timeout_ms;
} BrowserCommand;

typedef struct {
    BrowserCommand* commands;
    size_t count;
    size_t capacity;
} CommandBatch;

BffiResult bffi_create_batch(size_t capacity, CommandBatch* out) {
    if (!out) return BFFI_ERR_NULL;
    if (capacity == 0 || capacity > 10000) return BFFI_ERR_OVERFLOW;

    out->commands = (BrowserCommand*)calloc(capacity, sizeof(BrowserCommand));
    if (!out->commands) return BFFI_ERR_OVERFLOW;

    out->count = 0;
    out->capacity = capacity;
    return BFFI_OK;
}

BffiResult bffi_add_command(CommandBatch* batch, BrowserAction action,
                            const char* selector, size_t sel_len,
                            const char* payload, size_t pay_len,
                            uint32_t timeout_ms) {
    if (!batch || !batch->commands) return BFFI_ERR_NULL;
    if (batch->count >= batch->capacity) return BFFI_ERR_OVERFLOW;
    if (sel_len > 511 || pay_len > 1023) return BFFI_ERR_OVERFLOW;
    if (action < ACTION_CLICK || action > ACTION_WAIT) return BFFI_ERR_INVALID_ACTION;

    BrowserCommand* cmd = &batch->commands[batch->count];
    cmd->action = action;
    cmd->timeout_ms = timeout_ms;

    if (selector && sel_len > 0) {
        memcpy(cmd->selector, selector, sel_len);
        cmd->selector[sel_len] = '\0';
        cmd->selector_len = (uint16_t)sel_len;
    }

    if (payload && pay_len > 0) {
        memcpy(cmd->payload, payload, pay_len);
        cmd->payload[pay_len] = '\0';
        cmd->payload_len = (uint16_t)pay_len;
    }

    batch->count++;
    return BFFI_OK;
}

void bffi_free_batch(CommandBatch* batch) {
    if (batch && batch->commands) {
        free(batch->commands);
        batch->commands = NULL;
        batch->count = 0;
        batch->capacity = 0;
    }
}

const char* bffi_diagnostics(void) {
    return "{\"engine\":\"OmniBrowserFfi\",\"status\":\"Active\",\"version\":\"1.0.0\"}";
}
