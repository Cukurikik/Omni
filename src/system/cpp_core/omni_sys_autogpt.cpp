#include <cstdint>

extern "C" {
    int omni_sys_autogpt_dependencies(int* dep_matrix, int num_tasks, int task_idx) {
        if (!dep_matrix || num_tasks <= 0 || task_idx < 0 || task_idx >= num_tasks) return -1;
        
        int unresolved = 0;
        for (int i = 0; i < num_tasks; ++i) {
            // if task_idx depends on i
            if (dep_matrix[task_idx * num_tasks + i] == 1) {
                unresolved++;
            }
        }
        return unresolved; // 0 means task is ready
    }
}
