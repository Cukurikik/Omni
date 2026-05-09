/*
 * omni_epoll_server.c — Fast epoll TCP Event Loop
 * Layer: System / C
 *
 * An asynchronous TCP server utilizing the Linux epoll API. This circumvents
 * the one-thread-per-connection bottleneck, allowing a single thread to handle
 * thousands of concurrent connections efficiently. Zero mock.
 */

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define MAX_EVENTS 1024

// Utility to set a file descriptor to non-blocking mode
static int make_socket_non_blocking(int sfd) {
    int flags = fcntl(sfd, F_GETFL, 0);
    if (flags == -1) return -1;
    flags |= O_NONBLOCK;
    if (fcntl(sfd, F_SETFL, flags) == -1) return -1;
    return 0;
}

/**
 * Initializes and runs an epoll-based TCP server loop.
 * Note: Error handling prints to stderr. In production, routes to OmniLogger.
 */
int omni_run_epoll_server(int port) {
    int sfd, efd;
    struct sockaddr_in server_addr;
    struct epoll_event event;
    struct epoll_event *events;

    sfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sfd == -1) {
        perror("OMNI epoll: socket create failed");
        return -1;
    }

    int opt = 1;
    setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(port);

    if (bind(sfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1) {
        perror("OMNI epoll: bind failed");
        close(sfd);
        return -1;
    }

    if (make_socket_non_blocking(sfd) == -1) {
        perror("OMNI epoll: non-blocking failed");
        close(sfd);
        return -1;
    }

    if (listen(sfd, SOMAXCONN) == -1) {
        perror("OMNI epoll: listen failed");
        close(sfd);
        return -1;
    }

    efd = epoll_create1(0);
    if (efd == -1) {
        perror("OMNI epoll: epoll_create failed");
        close(sfd);
        return -1;
    }

    event.data.fd = sfd;
    event.events = EPOLLIN | EPOLLET; // Edge-Triggered
    if (epoll_ctl(efd, EPOLL_CTL_ADD, sfd, &event) == -1) {
        perror("OMNI epoll: epoll_ctl failed");
        close(sfd);
        close(efd);
        return -1;
    }

    events = calloc(MAX_EVENTS, sizeof(struct epoll_event));
    if (!events) {
        close(sfd);
        close(efd);
        return -1;
    }

    printf("OMNI epoll: Server listening on port %d\n", port);

    // Event Loop
    while (1) {
        int n = epoll_wait(efd, events, MAX_EVENTS, -1);
        for (int i = 0; i < n; i++) {
            if ((events[i].events & EPOLLERR) || (events[i].events & EPOLLHUP) || 
                (!(events[i].events & EPOLLIN))) {
                // An error has occurred, or the socket is not ready for reading
                close(events[i].data.fd);
                continue;
            } else if (sfd == events[i].data.fd) {
                // New incoming connection
                while (1) {
                    struct sockaddr_in in_addr;
                    socklen_t in_len = sizeof(in_addr);
                    int infd = accept(sfd, (struct sockaddr *)&in_addr, &in_len);
                    if (infd == -1) {
                        if ((errno == EAGAIN) || (errno == EWOULDBLOCK)) {
                            break; // Processed all incoming connections
                        } else {
                            perror("OMNI epoll: accept failed");
                            break;
                        }
                    }

                    make_socket_non_blocking(infd);
                    event.data.fd = infd;
                    event.events = EPOLLIN | EPOLLET;
                    epoll_ctl(efd, EPOLL_CTL_ADD, infd, &event);
                }
            } else {
                // Data on existing connection
                int done = 0;
                while (1) {
                    char buf[512];
                    ssize_t count = read(events[i].data.fd, buf, sizeof(buf));
                    if (count == -1) {
                        if (errno != EAGAIN) {
                            done = 1;
                        }
                        break;
                    } else if (count == 0) {
                        done = 1; // EOF
                        break;
                    }
                    
                    // Simple echo for this pure implementation
                    write(events[i].data.fd, buf, count);
                }

                if (done) {
                    close(events[i].data.fd);
                }
            }
        }
    }

    free(events);
    close(sfd);
    close(efd);
    return 0;
}
