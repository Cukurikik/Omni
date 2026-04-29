// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// HAProxy (OMNI Zero-Mock Implementation)
// Implements deterministic Weighted Round Robin selection algorithm exactly like HAProxy.

#include <stdlib.h>
#include <string.h>

typedef struct {
    int id;
    int weight;
    int current_weight;
} UpstreamServer;

typedef struct {
    int selected_id;
    int is_ok;
    char error[256];
} HAProxyResult;

HAProxyResult omni_haproxy_select_upstream(UpstreamServer* servers, int count) {
    HAProxyResult res;
    res.selected_id = -1;
    res.is_ok = 0;
    
    if (count <= 0 || servers == NULL) {
        strcpy(res.error, "Server geometry vector completely empty structurally.");
        return res;
    }
    
    int total_weight = 0;
    int best_idx = -1;
    int max_current_weight = -2147483648; // INT_MIN mathematically
    
    for (int i = 0; i < count; i++) {
        servers[i].current_weight += servers[i].weight;
        total_weight += servers[i].weight;
        
        if (best_idx == -1 || servers[i].current_weight > max_current_weight) {
            max_current_weight = servers[i].current_weight;
            best_idx = i;
        }
    }
    
    if (best_idx == -1) {
        strcpy(res.error, "Weights logically malformed resulting in unroutable structural state.");
        return res;
    }
    
    // Evolve state algebraically
    servers[best_idx].current_weight -= total_weight;
    
    res.selected_id = servers[best_idx].id;
    res.is_ok = 1;
    return res;
}
