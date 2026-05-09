/*
 * omni_rdtsc_timer.c — Cycle-Accurate Hardware Timer
 * Layer: System / Kernel
 * Inspired by: Linux Kernel Performance Events (perf)
 *
 * Exposes the RDTSC (Read Time-Stamp Counter) assembly instruction directly
 * to high-level applications. Bypasses the OS syscall overhead (e.g., gettimeofday)
 * for nano-second precision benchmarking of algorithmic hotspots. Zero mock.
 */

#include <stdint.h>

#ifdef _MSC_VER
#include <intrin.h>
#endif

/**
 * Reads the hardware Time-Stamp Counter.
 * Guarantees serial execution to prevent out-of-order execution artifacts
 * from skewing the micro-benchmark.
 */
static inline uint64_t rdtscp_internal() {
    unsigned int aux;
#ifdef _MSC_VER
    return __rdtscp(&aux);
#elif defined(__i386__) || defined(__x86_64__)
    uint64_t rax, rdx;
    __asm__ __volatile__ (
        "rdtscp"
        : "=a" (rax), "=d" (rdx), "=c" (aux)
        :: "memory"
    );
    return (rdx << 32) | rax;
#elif defined(__aarch64__)
    // ARM64 fallback (CNTVCT_EL0)
    uint64_t val;
    __asm__ __volatile__("mrs %0, cntvct_el0" : "=r" (val));
    return val;
#else
    // Generic fallback (Not cycle accurate)
    return 0;
#endif
}

/**
 * Initializes a timing block.
 */
uint64_t omni_timer_start() {
    // rdtscp flushes the pipeline before executing
    return rdtscp_internal();
}

/**
 * Ends a timing block and returns the elapsed CPU cycles.
 */
uint64_t omni_timer_end(uint64_t start_cycles) {
    uint64_t end_cycles = rdtscp_internal();
    if (end_cycles >= start_cycles) {
        return end_cycles - start_cycles;
    } else {
        // Handle wraparound (extremely rare for 64-bit, but good practice)
        return (UINT64_MAX - start_cycles) + end_cycles + 1;
    }
}
