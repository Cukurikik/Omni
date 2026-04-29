#include <cstdint>

extern "C" {
    int omni_sys_fastchat_heartbeat_sync(long long timestamp_ms, int active_connections) {
        // Return load factor
        if (active_connections <= 0) return 0;
        int load = active_connections * 10;
        return (load > 100) ? 100 : load;
    }
}
