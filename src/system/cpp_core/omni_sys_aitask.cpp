#include <cstring>

extern "C" {
    int omni_sys_aitask_hash_priority(const char* task_desc) {
        if (!task_desc) return 0;
        
        // Simple deterministic priority heuristic based on length and keywords
        int priority = 0;
        int len = std::strlen(task_desc);
        priority += (len % 10);
        
        if (std::strstr(task_desc, "URGENT") || std::strstr(task_desc, "CRITICAL")) {
            priority += 50;
        }
        
        return priority;
    }
}
