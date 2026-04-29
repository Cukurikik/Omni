#include <stdint.h>
#include <stddef.h>

#define MAX_TASKS 32

typedef void (*TaskFunction)(void);

typedef struct {
    TaskFunction task;
    uint32_t priority;
    uint8_t is_active;
} RTOSTask;

static RTOSTask task_queue[MAX_TASKS];
static uint8_t task_count = 0;

int omni_rtos_add_task(TaskFunction task, uint32_t priority) {
    if (task_count >= MAX_TASKS) return -1;
    task_queue[task_count].task = task;
    task_queue[task_count].priority = priority;
    task_queue[task_count].is_active = 1;
    task_count++;
    return 0;
}

void omni_rtos_run(void) {
    while (1) {
        for (int i = 0; i < task_count; i++) {
            if (task_queue[i].is_active) {
                task_queue[i].task();
            }
        }
    }
}
