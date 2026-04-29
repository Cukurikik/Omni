#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/un.h>

// OMNI CHATOLLAMA: IPC Bridge
// C Unix Domain Socket bridge allowing the high-level UI server to communicate 
// directly with the low-level Ollama inference daemon without TCP overhead.
// Source: ollama

#define SOCKET_PATH "/tmp/omni_ollama.sock"
#define BUFFER_SIZE 8192

typedef enum {
    IPC_OK = 0,
    IPC_ERR_SOCKET = -1,
    IPC_ERR_CONNECT = -2,
    IPC_ERR_WRITE = -3
} IPCError;

IPCError send_to_daemon(const char* payload, char* response_buffer, size_t response_size) {
    int sock = 0;
    struct sockaddr_un serv_addr;

    if ((sock = socket(AF_UNIX, SOCK_STREAM, 0)) < 0) {
        return IPC_ERR_SOCKET;
    }

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sun_family = AF_UNIX;
    strncpy(serv_addr.sun_path, SOCKET_PATH, sizeof(serv_addr.sun_path) - 1);

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        close(sock);
        return IPC_ERR_CONNECT;
    }

    if (write(sock, payload, strlen(payload)) < 0) {
        close(sock);
        return IPC_ERR_WRITE;
    }

    // Read response (Mock implementation)
    // int bytes_read = read(sock, response_buffer, response_size - 1);
    snprintf(response_buffer, response_size, "{\"status\": \"received\"}");
    
    close(sock);
    return IPC_OK;
}
