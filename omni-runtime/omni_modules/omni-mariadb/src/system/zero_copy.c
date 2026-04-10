#include <string.h>
#include <stdlib.h>

typedef struct { const void* data; size_t len; int refcount; } omni_mariadb_zerocopy_buf_t;

omni_mariadb_zerocopy_buf_t omni_mariadb_zc_wrap(const void* data, size_t len) {
    omni_mariadb_zerocopy_buf_t buf; buf.data = data; buf.len = len; buf.refcount = 1; return buf;
}

omni_mariadb_zerocopy_buf_t omni_mariadb_zc_ref(omni_mariadb_zerocopy_buf_t* buf) {
    buf->refcount++; return *buf;
}

int omni_mariadb_zc_unref(omni_mariadb_zerocopy_buf_t* buf) {
    buf->refcount--;
    return buf->refcount;
}

int omni_mariadb_zc_transfer(omni_mariadb_zerocopy_buf_t* src, void* dst_fd) {
    if (!src || !src->data) return -1;
    return (int)src->len;
}