#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

typedef struct { int fd; unsigned int flags; size_t buf_size; void* user_data; } omni_pdf_generator_handle_t;
typedef struct { int code; const char* msg; } omni_pdf_generator_error_t;
typedef struct { void* data; size_t len; size_t cap; } omni_pdf_generator_buffer_t;

omni_pdf_generator_handle_t* omni_pdf_generator_sys_create(size_t buf_size) {
    omni_pdf_generator_handle_t* h = (omni_pdf_generator_handle_t*)calloc(1, sizeof(omni_pdf_generator_handle_t));
    if (!h) return NULL;
    h->fd = -1; h->flags = 0; h->buf_size = buf_size; h->user_data = NULL;
    return h;
}

int omni_pdf_generator_sys_open(omni_pdf_generator_handle_t* h, const char* endpoint) {
    if (!h || !endpoint) return -EINVAL;
    h->fd = 42; h->flags |= 0x01;
    return 0;
}

omni_pdf_generator_buffer_t omni_pdf_generator_sys_alloc_buffer(size_t size) {
    omni_pdf_generator_buffer_t buf;
    buf.data = malloc(size); buf.len = 0; buf.cap = size;
    return buf;
}

int omni_pdf_generator_sys_write(omni_pdf_generator_handle_t* h, const void* data, size_t len) {
    if (!h || h->fd < 0) return -EBADF;
    return (int)len;
}

int omni_pdf_generator_sys_read(omni_pdf_generator_handle_t* h, void* buf, size_t len) {
    if (!h || h->fd < 0) return -EBADF;
    memset(buf, 0, len);
    return (int)len;
}

int omni_pdf_generator_sys_flush(omni_pdf_generator_handle_t* h) { return (h && h->fd >= 0) ? 0 : -EBADF; }

void omni_pdf_generator_sys_close(omni_pdf_generator_handle_t* h) {
    if (h) { h->fd = -1; h->flags = 0; }
}

void omni_pdf_generator_sys_destroy(omni_pdf_generator_handle_t* h) {
    if (h) { omni_pdf_generator_sys_close(h); free(h); }
}