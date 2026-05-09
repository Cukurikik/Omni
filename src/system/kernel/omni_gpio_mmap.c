/*
 * omni_gpio_mmap.c — Raw Memory-Mapped GPIO Access
 * Layer: System / Embedded / Kernel
 *
 * Provides microsecond-latency hardware pin toggling by bypassing the Linux
 * sysfs filesystem and writing directly to physical memory mapped registers.
 * Essential for bare-metal IoT, Robotics, and Raspberry Pi integrations. Zero mock.
 */

#ifdef __linux__

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdint.h>

// BCM2835 (Raspberry Pi 1/Zero) Base
// BCM2836/7 (Raspberry Pi 2/3) Base is 0x3F000000
// BCM2711 (Raspberry Pi 4) Base is 0xFE000000
#define BCM2835_PERI_BASE   0x20000000
#define GPIO_BASE           (BCM2835_PERI_BASE + 0x200000)
#define BLOCK_SIZE          (4*1024)

// GPIO Setup macros
#define INP_GPIO(g) *(gpio_map+((g)/10)) &= ~(7<<(((g)%10)*3))
#define OUT_GPIO(g) *(gpio_map+((g)/10)) |=  (1<<(((g)%10)*3))

// Pin Output macros
#define GPIO_SET *(gpio_map+7)  // sets bits which are 1 ignores bits which are 0
#define GPIO_CLR *(gpio_map+10) // clears bits which are 1 ignores bits which are 0

// Pin Input macros
#define GPIO_GET *(gpio_map+13)

volatile uint32_t *gpio_map = NULL;

/**
 * Initializes the memory map to physical hardware registers.
 * Must be run as root.
 */
int omni_gpio_init() {
    int mem_fd = open("/dev/mem", O_RDWR | O_SYNC);
    if (mem_fd < 0) {
        perror("Failed to open /dev/mem. Are you root?");
        return -1;
    }

    // Map physical memory into user space
    void *map = mmap(
        NULL,
        BLOCK_SIZE,
        PROT_READ | PROT_WRITE,
        MAP_SHARED,
        mem_fd,
        GPIO_BASE
    );

    close(mem_fd); // safe to close after mmap

    if (map == MAP_FAILED) {
        perror("mmap error");
        return -1;
    }

    // Cast mapped pointer to volatile uint32_t to prevent compiler optimizations
    gpio_map = (volatile uint32_t *)map;
    
    return 0;
}

/**
 * Sets a GPIO pin as an Output
 */
void omni_gpio_set_output(int pin) {
    if (!gpio_map) return;
    INP_GPIO(pin); // Must always clear before setting
    OUT_GPIO(pin);
}

/**
 * Sets a GPIO pin as an Input
 */
void omni_gpio_set_input(int pin) {
    if (!gpio_map) return;
    INP_GPIO(pin);
}

/**
 * Writes a HIGH (1) or LOW (0) to an output pin
 */
void omni_gpio_write(int pin, int value) {
    if (!gpio_map) return;
    if (value) {
        GPIO_SET = 1 << pin;
    } else {
        GPIO_CLR = 1 << pin;
    }
}

/**
 * Reads the current state of an input pin
 */
int omni_gpio_read(int pin) {
    if (!gpio_map) return 0;
    if ((GPIO_GET & (1 << pin)) != 0) {
        return 1;
    }
    return 0;
}

#endif
