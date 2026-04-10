#include <string.h>
#include <stdlib.h>

typedef struct { const void* data; size_t len; int refcount; } omni_pinecone_zerocopy_buf_t;

omni_pinecone_zerocopy_buf_t omni_pinecone_zc_wrap(const void* data, size_t len) {
    omni_pinecone_zerocopy_buf_t buf; buf.data = data; buf.len = len; buf.refcount = 1; return buf;
}

omni_pinecone_zerocopy_buf_t omni_pinecone_zc_ref(omni_pinecone_zerocopy_buf_t* buf) {
    buf->refcount++; return *buf;
}

int omni_pinecone_zc_unref(omni_pinecone_zerocopy_buf_t* buf) {
    buf->refcount--;
    return buf->refcount;
}

int omni_pinecone_zc_transfer(omni_pinecone_zerocopy_buf_t* src, void* dst_fd) {
    if (!src || !src->data) return -1;
    return (int)src->len;
}