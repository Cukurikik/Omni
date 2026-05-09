/*
 * omni_eventfd.c — Linux eventfd Wrapper
 * Layer: System / C
 *
 * Implements a fast, lightweight inter-process/inter-thread communication
 * mechanism utilizing the Linux `eventfd` syscall. Ideal for notifying epoll loops.
 * Zero mock.
 */

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/eventfd.h>

typedef struct {
    int fd;
} OmniEventFD;

/**
 * Creates a new eventfd object.
 * Returns NULL if creation fails.
 */
OmniEventFD* omni_eventfd_create(unsigned int initval) {
    // EFD_NONBLOCK prevents reads/writes from blocking
    // EFD_CLOEXEC prevents fd leaking to child processes
    int fd = eventfd(initval, EFD_NONBLOCK | EFD_CLOEXEC);
    
    if (fd == -1) {
        perror("OMNI eventfd: Failed to create eventfd");
        return NULL;
    }

    OmniEventFD* efd = (OmniEventFD*)__builtin_malloc(sizeof(OmniEventFD));
    if (!efd) {
        close(fd);
        return NULL;
    }
    
    efd->fd = fd;
    return efd;
}

/**
 * Signals the eventfd by adding a value (usually 1) to its internal counter.
 */
int omni_eventfd_notify(OmniEventFD* efd, uint64_t val) {
    if (!efd || efd->fd < 0) return -1;
    
    ssize_t bytes_written = write(efd->fd, &val, sizeof(uint64_t));
    if (bytes_written != sizeof(uint64_t)) {
        return -1;
    }
    return 0;
}

/**
 * Reads the eventfd counter, resetting it to 0.
 * Returns the read value, or 0 if no events are pending (EAGAIN due to NONBLOCK).
 */
uint64_t omni_eventfd_read(OmniEventFD* efd) {
    if (!efd || efd->fd < 0) return 0;
    
    uint64_t val = 0;
    ssize_t bytes_read = read(efd->fd, &val, sizeof(uint64_t));
    
    if (bytes_read != sizeof(uint64_t)) {
        return 0; // EAGAIN
    }
    
    return val;
}

/**
 * Closes and frees the eventfd object.
 */
void omni_eventfd_destroy(OmniEventFD* efd) {
    if (efd) {
        if (efd->fd >= 0) {
            close(efd->fd);
        }
        __builtin_free(efd);
    }
}

/**
 * Exposes the raw file descriptor for inclusion in epoll/poll loops.
 */
int omni_eventfd_get_fd(OmniEventFD* efd) {
    if (!efd) return -1;
    return efd->fd;
}
