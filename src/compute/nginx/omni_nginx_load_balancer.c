// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// NGINX Load Balancer (OMNI Zero-Mock Implementation)
// Implements Round Robin and Least Connection balancing matrix logic in C.

#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

typedef struct {
    int value; // Selected server index
    char* error;
    bool is_ok;
} ResultInt;

ResultInt OkInt(int val) {
    ResultInt r = {val, NULL, true};
    return r;
}

ResultInt ErrInt(const char* err) {
    char* err_cpy = strdup(err);
    ResultInt r = {-1, err_cpy, false};
    return r;
}

typedef struct {
    int id;
    int active_connections;
    bool is_healthy;
} UpstreamServer;

typedef struct {
    UpstreamServer* servers;
    int count;
    int rr_pointer;
} LoadBalancer;

ResultInt proxy_round_robin(LoadBalancer* lb) {
    if (!lb || lb->count <= 0) return ErrInt("No upstream servers configured.");
    
    int start_pt = lb->rr_pointer;
    do {
        int idx = lb->rr_pointer;
        lb->rr_pointer = (lb->rr_pointer + 1) % lb->count; // Advance
        
        if (lb->servers[idx].is_healthy) {
            lb->servers[idx].active_connections++;
            return OkInt(idx);
        }
    } while (lb->rr_pointer != start_pt);
    
    return ErrInt("502 Bad Gateway: No healthy upstream servers.");
}

ResultInt proxy_least_connections(LoadBalancer* lb) {
    if (!lb || lb->count <= 0) return ErrInt("No upstream servers configured.");

    int best_idx = -1;
    int min_conn = 1e9; // Safe infinity
    
    for (int i = 0; i < lb->count; i++) {
        if (lb->servers[i].is_healthy) {
            if (lb->servers[i].active_connections < min_conn) {
                min_conn = lb->servers[i].active_connections;
                best_idx = i;
            }
        }
    }
    
    if (best_idx == -1) {
        return ErrInt("502 Bad Gateway: No healthy upstream servers.");
    }
    
    lb->servers[best_idx].active_connections++;
    return OkInt(best_idx);
}
