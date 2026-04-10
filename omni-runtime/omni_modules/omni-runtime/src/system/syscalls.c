// ============================================================
// ⚡ omni-runtime/system/syscalls.c — Process Context & Context Switching
// ============================================================

#include <stdint.h>
#include <time.h>
#include <stdlib.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif

extern "C" {

struct OmniError {
    uint32_t code;
    const char* message;
};

struct OmniUptimeResult {
    uint8_t is_error;
    OmniError error;
    double uptime;
};

static uint64_t start_time_ns = 0;

uint64_t current_time_ns() {
#ifdef _WIN32
    LARGE_INTEGER frequency;
    LARGE_INTEGER time;
    QueryPerformanceFrequency(&frequency);
    QueryPerformanceCounter(&time);
    return (uint64_t)(time.QuadPart * 1000000000LL / frequency.QuadPart);
#else
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
#endif
}

void omni_runtime_init() {
    start_time_ns = current_time_ns();
}

OmniUptimeResult omni_sys_uptime() {
    if (start_time_ns == 0) {
        omni_runtime_init();
    }
    double diff_secs = (double)(current_time_ns() - start_time_ns) / 1000000000.0;
    return OmniUptimeResult { 0, {0, nullptr}, diff_secs };
}

void omni_sys_sleep(uint32_t milliseconds) {
#ifdef _WIN32
    Sleep(milliseconds);
#else
    usleep(milliseconds * 1000);
#endif
}

void omni_sys_exit(int32_t exit_code) {
    exit(exit_code);
}

}
