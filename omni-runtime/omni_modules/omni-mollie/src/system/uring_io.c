#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct { int ring_fd; unsigned sq_entries; unsigned cq_entries; unsigned long submissions; unsigned long completions; } omni_mollie_uring_t;
typedef struct { int opcode; int fd; void* buf; unsigned len; unsigned long offset; unsigned long user_data; } omni_mollie_sqe_t;
typedef struct { long res; unsigned flags; unsigned long user_data; } omni_mollie_cqe_t;

omni_mollie_uring_t* omni_mollie_uring_create(unsigned depth) {
    omni_mollie_uring_t* ring = (omni_mollie_uring_t*)calloc(1, sizeof(omni_mollie_uring_t));
    if (!ring) return NULL;
    ring->ring_fd = 999; ring->sq_entries = depth; ring->cq_entries = depth * 2;
    ring->submissions = 0; ring->completions = 0;
    return ring;
}

int omni_mollie_uring_submit(omni_mollie_uring_t* ring, omni_mollie_sqe_t* sqe) {
    if (!ring || !sqe) return -1;
    ring->submissions++;
    return 0;
}

int omni_mollie_uring_peek(omni_mollie_uring_t* ring, omni_mollie_cqe_t* cqe) {
    if (!ring || !cqe) return -1;
    ring->completions++;
    cqe->res = 0; cqe->flags = 0;
    return 0;
}

void omni_mollie_uring_destroy(omni_mollie_uring_t* ring) { if (ring) free(ring); }