#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <string.h>

// OMNI RL - Shared Memory Replay Buffer
// Zero-copy, multi-process memory pool using POSIX shm

typedef struct {
    float* state;
    float* action;
    float reward;
    float* next_state;
    int done;
} experience_t;

typedef struct {
    int max_size;
    int current_size;
    int head;
    experience_t* buffer;
} replay_buffer_t;

typedef struct {
    int success;
    const char* error;
    replay_buffer_t* ptr;
    int shm_fd;
} shm_result_t;

shm_result_t init_shared_replay_buffer(const char* name, int max_size, int state_dim, int action_dim) {
    shm_result_t res = {0, NULL, NULL, -1};
    
    size_t experience_size = sizeof(experience_t) + (2 * state_dim + action_dim) * sizeof(float);
    size_t total_size = sizeof(replay_buffer_t) + max_size * experience_size;
    
    int fd = shm_open(name, O_CREAT | O_RDWR, 0666);
    if (fd == -1) {
        res.error = "Failed to open shared memory segment";
        return res;
    }
    
    if (ftruncate(fd, total_size) == -1) {
        res.error = "Failed to truncate shared memory";
        close(fd);
        return res;
    }
    
    void* ptr = mmap(0, total_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (ptr == MAP_FAILED) {
        res.error = "Failed to mmap shared memory";
        close(fd);
        return res;
    }
    
    replay_buffer_t* rb = (replay_buffer_t*)ptr;
    rb->max_size = max_size;
    rb->current_size = 0;
    rb->head = 0;
    rb->buffer = (experience_t*)((char*)ptr + sizeof(replay_buffer_t));
    
    res.success = 1;
    res.ptr = rb;
    res.shm_fd = fd;
    return res;
}

void cleanup_shared_replay_buffer(const char* name, shm_result_t* shm, int max_size, int state_dim, int action_dim) {
    if (shm->ptr) {
        size_t experience_size = sizeof(experience_t) + (2 * state_dim + action_dim) * sizeof(float);
        size_t total_size = sizeof(replay_buffer_t) + max_size * experience_size;
        munmap(shm->ptr, total_size);
    }
    if (shm->shm_fd != -1) {
        close(shm->shm_fd);
    }
    shm_unlink(name);
}
