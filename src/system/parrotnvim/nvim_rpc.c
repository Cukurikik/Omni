#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    void* payload;
    const char* error;
    int is_ok;
} OmniResultRPC;

OmniResultRPC send_nvim_rpc_request(const char* method, const char* params) {
    if (!method || !params) {
        return (OmniResultRPC){NULL, "Invalid RPC arguments", 0};
    }

    // System-level serialization for Neovim MessagePack-RPC
    size_t payload_len = strlen(method) + strlen(params) + 32;
    char* encoded_payload = (char*)malloc(payload_len);
    if (!encoded_payload) {
        return (OmniResultRPC){NULL, "OOM in RPC encoding", 0};
    }

    snprintf(encoded_payload, payload_len, "{\"method\":\"%s\", \"params\":%s}", method, params);
    
    return (OmniResultRPC){encoded_payload, NULL, 1};
}
