#include <string.h>
#include <stdlib.h>

typedef struct { const void* data; size_t len; int refcount; } omni_sqlite_turbo_zerocopy_buf_t;

omni_sqlite_turbo_zerocopy_buf_t omni_sqlite_turbo_zc_wrap(const void* data, size_t len) {
    omni_sqlite_turbo_zerocopy_buf_t buf; buf.data = data; buf.len = len; buf.refcount = 1; return buf;
}

omni_sqlite_turbo_zerocopy_buf_t omni_sqlite_turbo_zc_ref(omni_sqlite_turbo_zerocopy_buf_t* buf) {
    buf->refcount++; return *buf;
}

int omni_sqlite_turbo_zc_unref(omni_sqlite_turbo_zerocopy_buf_t* buf) {
    buf->refcount--;
    return buf->refcount;
}

int omni_sqlite_turbo_zc_transfer(omni_sqlite_turbo_zerocopy_buf_t* src, void* dst_fd) {
    if (!src || !src->data) return -1;
    return (int)src->len;
}