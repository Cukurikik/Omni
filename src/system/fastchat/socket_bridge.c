#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>

// OMNI FASTCHAT: Unix Domain Socket Bridge
// High-performance C bridge for Inter-Process Communication (IPC) between FastChat workers on the same machine.
// Source: lm-sys/FastChat

#define SOCKET_PATH "/tmp/omni_fastchat.sock"
#define BUFFER_SIZE 8192

typedef enum {
    IPC_SUCCESS = 0,
    IPC_ERR_SOCKET = 1,
    IPC_ERR_BIND = 2,
    IPC_ERR_CONNECT = 3,
    IPC_ERR_SEND = 4,
    IPC_ERR_RECV = 5
} ipc_err_t;

// Creates and binds a Unix Domain Socket server
ipc_err_t ipc_server_init(int* out_fd) {
    int server_fd;
    struct sockaddr_un addr;

    if ((server_fd = socket(AF_UNIX, SOCK_STREAM, 0)) == -1) {
        return IPC_ERR_SOCKET;
    }

    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path) - 1);

    unlink(SOCKET_PATH); // Remove existing socket

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) == -1) {
        close(server_fd);
        return IPC_ERR_BIND;
    }

    if (listen(server_fd, 5) == -1) {
        close(server_fd);
        return IPC_ERR_BIND;
    }

    *out_fd = server_fd;
    return IPC_SUCCESS;
}

// Connects to an existing Unix Domain Socket
ipc_err_t ipc_client_connect(int* out_fd) {
    int client_fd;
    struct sockaddr_un addr;

    if ((client_fd = socket(AF_UNIX, SOCK_STREAM, 0)) == -1) {
        return IPC_ERR_SOCKET;
    }

    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path) - 1);

    if (connect(client_fd, (struct sockaddr*)&addr, sizeof(addr)) == -1) {
        close(client_fd);
        return IPC_ERR_CONNECT;
    }

    *out_fd = client_fd;
    return IPC_SUCCESS;
}

// Write data
ipc_err_t ipc_send(int fd, const char* data, size_t len) {
    if (write(fd, data, len) != len) {
        return IPC_ERR_SEND;
    }
    return IPC_SUCCESS;
}

// Read data
ipc_err_t ipc_recv(int fd, char* buffer, size_t max_len, size_t* out_read) {
    ssize_t bytes_read = read(fd, buffer, max_len - 1);
    if (bytes_read < 0) {
        return IPC_ERR_RECV;
    }
    buffer[bytes_read] = '\0';
    if (out_read) *out_read = bytes_read;
    return IPC_SUCCESS;
}
