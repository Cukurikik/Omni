// moe_power_manager.c — System / Energy
// Layer: System / OS — MoE Dynamic Voltage and Frequency Scaling (DVFS)
//
// Manages power states of CPU/GPU cores based on expert activation.
// MoE naturally leaves many experts (and their hosting nodes) idle during
// specific inference passes. This controller lowers frequency of idle cores
// to save power and thermal budget, boosting active experts.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

#define CPUFREQ_PATH "/sys/devices/system/cpu/cpu%d/cpufreq/scaling_setspeed"
#define GOVERNOR_PATH "/sys/devices/system/cpu/cpu%d/cpufreq/scaling_governor"

typedef enum {
    PM_OK = 0,
    PM_ERR_FILE = -1,
    PM_ERR_WRITE = -2
} PowerManagerResult;

/**
 * Sets the CPU governor to 'userspace' to allow manual frequency control.
 */
PowerManagerResult omni_pm_set_governor_userspace(int cpu_id) {
    char path[256];
    snprintf(path, sizeof(path), GOVERNOR_PATH, cpu_id);
    
    int fd = open(path, O_WRONLY);
    if (fd < 0) return PM_ERR_FILE;
    
    const char* gov = "userspace\n";
    if (write(fd, gov, strlen(gov)) < 0) {
        close(fd);
        return PM_ERR_WRITE;
    }
    
    close(fd);
    return PM_OK;
}

/**
 * Throttles an idle core to base/minimum frequency to save power.
 * Called for CPU cores hosting experts that were NOT selected by the router.
 */
PowerManagerResult omni_pm_throttle_idle_expert(int cpu_id, unsigned long min_freq_khz) {
    char path[256];
    snprintf(path, sizeof(path), CPUFREQ_PATH, cpu_id);
    
    int fd = open(path, O_WRONLY);
    if (fd < 0) return PM_ERR_FILE;
    
    char freq_str[32];
    snprintf(freq_str, sizeof(freq_str), "%lu\n", min_freq_khz);
    
    if (write(fd, freq_str, strlen(freq_str)) < 0) {
        close(fd);
        return PM_ERR_WRITE;
    }
    
    close(fd);
    return PM_OK;
}

/**
 * Boosts an active core to maximum frequency.
 * Called immediately for CPU cores hosting experts that WERE selected by the router.
 */
PowerManagerResult omni_pm_boost_active_expert(int cpu_id, unsigned long max_freq_khz) {
    char path[256];
    snprintf(path, sizeof(path), CPUFREQ_PATH, cpu_id);
    
    int fd = open(path, O_WRONLY);
    if (fd < 0) return PM_ERR_FILE;
    
    char freq_str[32];
    snprintf(freq_str, sizeof(freq_str), "%lu\n", max_freq_khz);
    
    if (write(fd, freq_str, strlen(freq_str)) < 0) {
        close(fd);
        return PM_ERR_WRITE;
    }
    
    close(fd);
    return PM_OK;
}
