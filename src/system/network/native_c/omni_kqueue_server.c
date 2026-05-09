/*
 * omni_kqueue_server.c — High-Performance Kqueue Event Loop
 * Layer: System / Network
 * Inspired by: NGINX (macOS/FreeBSD core)
 *
 * Demonstrates a non-blocking TCP server utilizing the BSD kqueue API.
 * The macOS/FreeBSD equivalent to Linux epoll, providing O(1) event scaling
 * for massive concurrent connection handling. Zero mock architecture.
 */

#if defined(__APPLE__) || defined(__FreeBSD__)

#include <sys/types.h>
#include <sys/event.h>
#include <sys/time.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_EVENTS 1024
#define PORT 8080

static int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

void omni_start_kqueue_server() {
    int server_fd, kq;
    struct sockaddr_in server_addr;
    struct kevent change_event[1], events[MAX_EVENTS];

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1) {
        perror("socket");
        return;
    }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    set_nonblocking(server_fd);

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("bind");
        close(server_fd);
        return;
    }

    if (listen(server_fd, SOMAXCONN) == -1) {
        perror("listen");
        close(server_fd);
        return;
    }

    // Initialize kqueue
    kq = kqueue();
    if (kq == -1) {
        perror("kqueue");
        close(server_fd);
        return;
    }

    // Register server_fd for read events
    EV_SET(&change_event[0], server_fd, EVFILT_READ, EV_ADD | EV_ENABLE, 0, 0, NULL);
    if (kevent(kq, change_event, 1, NULL, 0, NULL) == -1) {
        perror("kevent register");
        return;
    }

    printf("OMNI Kqueue Server listening on port %d...\n", PORT);

    while (1) {
        int nev = kevent(kq, NULL, 0, events, MAX_EVENTS, NULL);
        if (nev == -1) {
            perror("kevent wait");
            break;
        }

        for (int i = 0; i < nev; i++) {
            if (events[i].ident == server_fd) {
                // Accept new connection
                struct sockaddr_in client_addr;
                socklen_t client_len = sizeof(client_addr);
                int client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &client_len);
                
                if (client_fd == -1) continue;

                set_nonblocking(client_fd);
                
                // Add client_fd to kqueue
                EV_SET(&change_event[0], client_fd, EVFILT_READ, EV_ADD | EV_ENABLE, 0, 0, NULL);
                kevent(kq, change_event, 1, NULL, 0, NULL);
                
            } else if (events[i].filter == EVFILT_READ) {
                // Read data from client
                int client_fd = events[i].ident;
                
                // Check if connection closed by peer
                if (events[i].flags & EV_EOF) {
                    close(client_fd);
                    continue;
                }
                
                char buf[512];
                ssize_t count = read(client_fd, buf, sizeof(buf));
                
                if (count > 0) {
                    // Echo back
                    write(client_fd, buf, count);
                } else if (count == 0 || (count == -1 && errno != EAGAIN)) {
                    close(client_fd);
                }
            }
        }
    }

    close(server_fd);
    close(kq);
}

#endif
