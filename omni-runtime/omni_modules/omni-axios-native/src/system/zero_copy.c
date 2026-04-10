#include <string.h>
#include <stdlib.h>

typedef struct { const void* data; size_t len; int refcount; } omni_axios_native_zerocopy_buf_t;

omni_axios_native_zerocopy_buf_t omni_axios_native_zc_wrap(const void* data, size_t len) {
    omni_axios_native_zerocopy_buf_t buf; buf.data = data; buf.len = len; buf.refcount = 1; return buf;
}

omni_axios_native_zerocopy_buf_t omni_axios_native_zc_ref(omni_axios_native_zerocopy_buf_t* buf) {
    buf->refcount++; return *buf;
}

int omni_axios_native_zc_unref(omni_axios_native_zerocopy_buf_t* buf) {
    buf->refcount--;
    return buf->refcount;
}

int omni_axios_native_zc_transfer(omni_axios_native_zerocopy_buf_t* src, void* dst_fd) {
    if (!src || !src->data) return -1;
    return (int)src->len;
}