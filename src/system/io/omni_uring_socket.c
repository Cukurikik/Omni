// omni_uring_socket.c — io_uring Socket Wrapper
// Layer: System / C
//
// High-performance asynchronous socket I/O using Linux io_uring,
// bypassing the overhead of standard epoll()/read()/write() syscalls.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netinet/in.h>
#include <liburing.h>

#define MAX_CONNECTIONS 4096
#define BUF_SIZE 2048

struct conn_info {
    int fd;
    int type; // 0 = accept, 1 = read, 2 = write
    char buf[BUF_SIZE];
};

struct io_uring ring;

void setup_io_uring() {
    // Initialize io_uring with 256 entries
    if (io_uring_queue_init(256, &ring, 0) < 0) {
        perror("io_uring_queue_init");
        exit(1);
    }
}

void add_accept_request(int server_socket, struct sockaddr_in *client_addr, socklen_t *client_len) {
    struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
    
    struct conn_info *conn = malloc(sizeof(struct conn_info));
    conn->fd = server_socket;
    conn->type = 0;
    
    io_uring_prep_accept(sqe, server_socket, (struct sockaddr *)client_addr, client_len, 0);
    io_uring_sqe_set_data(sqe, conn);
}

void add_read_request(int client_socket) {
    struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
    
    struct conn_info *conn = malloc(sizeof(struct conn_info));
    conn->fd = client_socket;
    conn->type = 1;
    
    io_uring_prep_recv(sqe, client_socket, conn->buf, BUF_SIZE, 0);
    io_uring_sqe_set_data(sqe, conn);
}

void process_uring_events() {
    struct io_uring_cqe *cqe;
    
    // Blocking wait for at least one event
    if (io_uring_wait_cqe(&ring, &cqe) < 0) {
        perror("io_uring_wait_cqe");
        return;
    }
    
    struct io_uring_cqe *cqes[256];
    int cqe_count = io_uring_peek_batch_cqe(&ring, cqes, 256);
    
    for (int i = 0; i < cqe_count; ++i) {
        struct io_uring_cqe *ev = cqes[i];
        struct conn_info *conn = (struct conn_info *)io_uring_cqe_get_data(ev);
        
        if (conn->type == 0) { // Accept
            int client_fd = ev->res;
            if (client_fd >= 0) {
                // Read from new client
                add_read_request(client_fd);
            }
            // Re-arm accept (would pass proper struct in real loop)
            // add_accept_request(conn->fd, ...);
        } else if (conn->type == 1) { // Read
            int bytes_read = ev->res;
            if (bytes_read <= 0) {
                close(conn->fd);
            } else {
                // Mock echo response using standard write for brevity
                // (In production, this would queue an io_uring_prep_send)
                write(conn->fd, conn->buf, bytes_read);
                add_read_request(conn->fd);
            }
        }
        
        free(conn);
        io_uring_cqe_seen(&ring, ev);
    }
}
