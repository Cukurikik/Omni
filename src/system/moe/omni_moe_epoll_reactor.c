#include <sys/epoll.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

#define MAX_EVENTS 1024

// OMNI MOTHER Production Zero-Mock Epoll Reactor
// High-performance Linux C Reactor handling non-blocking IPC connections
// for MoE routing telemetry without spawning threads.

typedef struct {
    int epoll_fd;
    struct epoll_event* events;
} OmniReactor;

OmniReactor* omni_reactor_create() {
    OmniReactor* reactor = (OmniReactor*)malloc(sizeof(OmniReactor));
    if (!reactor) return NULL;

    reactor->epoll_fd = epoll_create1(0);
    if (reactor->epoll_fd == -1) {
        perror("OMNI CRITICAL: epoll_create1 failed");
        free(reactor);
        return NULL;
    }

    reactor->events = (struct epoll_event*)calloc(MAX_EVENTS, sizeof(struct epoll_event));
    return reactor;
}

int omni_reactor_add(OmniReactor* reactor, int fd, uint32_t events) {
    // Set socket to non-blocking
    int flags = fcntl(fd, F_GETFL, 0);
    fcntl(fd, F_SETFL, flags | O_NONBLOCK);

    struct epoll_event ev;
    ev.events = events;
    ev.data.fd = fd;

    if (epoll_ctl(reactor->epoll_fd, EPOLL_CTL_ADD, fd, &ev) == -1) {
        perror("OMNI CRITICAL: epoll_ctl EPOLL_CTL_ADD failed");
        return -1;
    }
    return 0;
}

void omni_reactor_poll(OmniReactor* reactor, void (*callback)(int, uint32_t)) {
    int nfds = epoll_wait(reactor->epoll_fd, reactor->events, MAX_EVENTS, -1);
    if (nfds == -1) {
        if (errno != EINTR) {
            perror("OMNI CRITICAL: epoll_wait failed");
        }
        return;
    }

    for (int n = 0; n < nfds; ++n) {
        callback(reactor->events[n].data.fd, reactor->events[n].events);
    }
}

void omni_reactor_destroy(OmniReactor* reactor) {
    if (reactor) {
        close(reactor->epoll_fd);
        free(reactor->events);
        free(reactor);
    }
}
