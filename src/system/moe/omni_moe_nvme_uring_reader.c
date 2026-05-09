#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <liburing.h>
#include <string.h>

#define QUEUE_DEPTH 128
#define BLOCK_SIZE 4096

// OMNI MOTHER Production: Zero-Mock NVMe io_uring reader
// Bypasses Linux VFS cache via O_DIRECT for max MoE weight streaming bandwidth

typedef struct {
    struct io_uring ring;
    int fd;
    size_t file_size;
} OmniNvmeStreamer;

int omni_nvme_init(OmniNvmeStreamer* streamer, const char* filepath) {
    if (!streamer || !filepath) return -1;

    streamer->fd = open(filepath, O_RDONLY | O_DIRECT);
    if (streamer->fd < 0) {
        perror("OMNI CRITICAL: Failed to open NVMe target");
        return -1;
    }

    off_t size = lseek(streamer->fd, 0, SEEK_END);
    if (size < 0) {
        close(streamer->fd);
        return -1;
    }
    streamer->file_size = (size_t)size;

    int ret = io_uring_queue_init(QUEUE_DEPTH, &streamer->ring, 0);
    if (ret < 0) {
        fprintf(stderr, "OMNI CRITICAL: io_uring_queue_init failed: %s\n", strerror(-ret));
        close(streamer->fd);
        return -1;
    }

    return 0;
}

int omni_nvme_read_async(OmniNvmeStreamer* streamer, void* buffer, size_t size, off_t offset) {
    if (!streamer || !buffer) return -1;
    if ((size % BLOCK_SIZE) != 0 || (offset % BLOCK_SIZE) != 0) {
        fprintf(stderr, "OMNI CRITICAL: O_DIRECT requires block-aligned I/O\n");
        return -1;
    }

    struct io_uring_sqe *sqe = io_uring_get_sqe(&streamer->ring);
    if (!sqe) {
        fprintf(stderr, "OMNI CRITICAL: io_uring SQE ring full\n");
        return -1;
    }

    io_uring_prep_read(sqe, streamer->fd, buffer, size, offset);
    io_uring_sqe_set_data(sqe, buffer); // Use buffer ptr as user data

    int ret = io_uring_submit(&streamer->ring);
    if (ret < 0) {
        fprintf(stderr, "OMNI CRITICAL: io_uring_submit failed: %s\n", strerror(-ret));
        return -1;
    }

    return 0;
}

int omni_nvme_wait_completion(OmniNvmeStreamer* streamer) {
    struct io_uring_cqe *cqe;
    int ret = io_uring_wait_cqe(&streamer->ring, &cqe);
    if (ret < 0) {
        fprintf(stderr, "OMNI CRITICAL: io_uring_wait_cqe failed: %s\n", strerror(-ret));
        return -1;
    }
    
    if (cqe->res < 0) {
        fprintf(stderr, "OMNI CRITICAL: Async read failed: %s\n", strerror(-cqe->res));
        io_uring_cqe_seen(&streamer->ring, cqe);
        return -1;
    }

    io_uring_cqe_seen(&streamer->ring, cqe);
    return 0;
}

void omni_nvme_cleanup(OmniNvmeStreamer* streamer) {
    if (streamer) {
        io_uring_queue_exit(&streamer->ring);
        if (streamer->fd >= 0) {
            close(streamer->fd);
        }
    }
}
