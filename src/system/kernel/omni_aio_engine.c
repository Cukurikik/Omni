/*
 * omni_aio_engine.c — Linux Asynchronous I/O (AIO) Engine
 * Layer: System / C
 *
 * Implements high-throughput non-blocking disk reads/writes using the native
 * Linux AIO syscalls. Avoids blocking the epoll network threads during heavy
 * storage operations (e.g. database flushes). Zero mock.
 */

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/syscall.h>
#include <linux/aio_abi.h>

// Direct syscall wrappers for AIO since glibc doesn't expose them directly
static inline int io_setup(unsigned nr, aio_context_t *ctxp) {
    return syscall(__NR_io_setup, nr, ctxp);
}

static inline int io_destroy(aio_context_t ctx) {
    return syscall(__NR_io_destroy, ctx);
}

static inline int io_submit(aio_context_t ctx, long nr, struct iocb **iocbpp) {
    return syscall(__NR_io_submit, ctx, nr, iocbpp);
}

static inline int io_getevents(aio_context_t ctx, long min_nr, long nr, struct io_event *events, struct timespec *timeout) {
    return syscall(__NR_io_getevents, ctx, min_nr, nr, events, timeout);
}

typedef struct {
    aio_context_t ctx;
    int max_events;
} OmniAIOEngine;

/**
 * Initializes the AIO context.
 */
OmniAIOEngine* omni_aio_init(int max_events) {
    OmniAIOEngine* engine = (OmniAIOEngine*)malloc(sizeof(OmniAIOEngine));
    if (!engine) return NULL;

    engine->ctx = 0;
    engine->max_events = max_events;

    if (io_setup(max_events, &engine->ctx) < 0) {
        perror("OMNI AIO: io_setup failed");
        free(engine);
        return NULL;
    }

    return engine;
}

/**
 * Submits an asynchronous read request.
 */
int omni_aio_read(OmniAIOEngine* engine, int fd, void* buf, size_t count, off_t offset, uint64_t data) {
    if (!engine || fd < 0 || !buf) return -1;

    struct iocb cb;
    memset(&cb, 0, sizeof(cb));
    
    cb.aio_fildes = fd;
    cb.aio_lio_opcode = IOCB_CMD_PREAD;
    cb.aio_buf = (uint64_t)buf;
    cb.aio_nbytes = count;
    cb.aio_offset = offset;
    cb.aio_data = data; // User data passed to completion event

    struct iocb *cbs[1];
    cbs[0] = &cb;

    if (io_submit(engine->ctx, 1, cbs) < 0) {
        perror("OMNI AIO: io_submit read failed");
        return -1;
    }

    return 0;
}

/**
 * Submits an asynchronous write request.
 */
int omni_aio_write(OmniAIOEngine* engine, int fd, void* buf, size_t count, off_t offset, uint64_t data) {
    if (!engine || fd < 0 || !buf) return -1;

    struct iocb cb;
    memset(&cb, 0, sizeof(cb));
    
    cb.aio_fildes = fd;
    cb.aio_lio_opcode = IOCB_CMD_PWRITE;
    cb.aio_buf = (uint64_t)buf;
    cb.aio_nbytes = count;
    cb.aio_offset = offset;
    cb.aio_data = data;

    struct iocb *cbs[1];
    cbs[0] = &cb;

    if (io_submit(engine->ctx, 1, cbs) < 0) {
        perror("OMNI AIO: io_submit write failed");
        return -1;
    }

    return 0;
}

/**
 * Polls for completed I/O events.
 */
int omni_aio_poll(OmniAIOEngine* engine, struct io_event* events, int max_events) {
    if (!engine || !events) return -1;

    // Non-blocking poll (timeout = 0)
    struct timespec ts;
    ts.tv_sec = 0;
    ts.tv_nsec = 0;

    int ret = io_getevents(engine->ctx, 0, max_events, events, &ts);
    if (ret < 0 && errno != EAGAIN) {
        perror("OMNI AIO: io_getevents failed");
        return -1;
    }

    return ret; // Returns number of completed events
}

/**
 * Destroys the AIO context.
 */
void omni_aio_destroy(OmniAIOEngine* engine) {
    if (engine) {
        io_destroy(engine->ctx);
        free(engine);
    }
}
