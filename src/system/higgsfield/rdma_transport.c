#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <infiniband/verbs.h>

// OMNI Higgsfield - RDMA Transport Layer
// Zero-copy tensor transfer via RoCEv2 / InfiniBand

typedef struct {
    struct ibv_context *ctx;
    struct ibv_pd *pd;
    struct ibv_mr *mr;
    struct ibv_cq *cq;
    struct ibv_qp *qp;
    void *buffer;
    size_t size;
} rdma_context_t;

typedef struct {
    int success;
    const char* error;
} rdma_result_t;

rdma_result_t init_rdma(rdma_context_t *ctx, size_t buffer_size) {
    rdma_result_t res = {0, NULL};
    int num_devices;
    struct ibv_device **dev_list = ibv_get_device_list(&num_devices);
    
    if (!dev_list || num_devices == 0) {
        res.error = "No RDMA devices found.";
        return res;
    }

    ctx->ctx = ibv_open_device(dev_list[0]);
    ibv_free_device_list(dev_list);
    
    if (!ctx->ctx) {
        res.error = "Failed to open RDMA device.";
        return res;
    }

    ctx->pd = ibv_alloc_pd(ctx->ctx);
    if (!ctx->pd) {
        res.error = "Failed to allocate Protection Domain.";
        return res;
    }

    ctx->size = buffer_size;
    ctx->buffer = malloc(buffer_size);
    if (!ctx->buffer) {
        res.error = "Failed to allocate memory buffer.";
        return res;
    }

    ctx->mr = ibv_reg_mr(ctx->pd, ctx->buffer, buffer_size, IBV_ACCESS_LOCAL_WRITE | IBV_ACCESS_REMOTE_WRITE | IBV_ACCESS_REMOTE_READ);
    if (!ctx->mr) {
        res.error = "Failed to register Memory Region.";
        return res;
    }

    ctx->cq = ibv_create_cq(ctx->ctx, 10, NULL, NULL, 0);
    if (!ctx->cq) {
        res.error = "Failed to create Completion Queue.";
        return res;
    }

    struct ibv_qp_init_attr qp_attr = {0};
    qp_attr.send_cq = ctx->cq;
    qp_attr.recv_cq = ctx->cq;
    qp_attr.qp_type = IBV_QPT_RC; // Reliable Connection
    qp_attr.cap.max_send_wr = 10;
    qp_attr.cap.max_recv_wr = 10;
    qp_attr.cap.max_send_sge = 1;
    qp_attr.cap.max_recv_sge = 1;

    ctx->qp = ibv_create_qp(ctx->pd, &qp_attr);
    if (!ctx->qp) {
        res.error = "Failed to create Queue Pair.";
        return res;
    }

    res.success = 1;
    return res;
}

void cleanup_rdma(rdma_context_t *ctx) {
    if (ctx->qp) ibv_destroy_qp(ctx->qp);
    if (ctx->cq) ibv_destroy_cq(ctx->cq);
    if (ctx->mr) ibv_dereg_mr(ctx->mr);
    if (ctx->buffer) free(ctx->buffer);
    if (ctx->pd) ibv_dealloc_pd(ctx->pd);
    if (ctx->ctx) ibv_close_device(ctx->ctx);
}
