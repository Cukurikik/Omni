#ifndef OMNI_EPOLL_SERVER_H
#define OMNI_EPOLL_SERVER_H

// OMNI MOTHER: C Epoll Server Header

#ifdef __cplusplus
extern "C" {
#endif

int omni_epoll_init();
void omni_epoll_add_socket(int epoll_fd, int socket_fd);
void omni_epoll_wait_loop(int epoll_fd);

#ifdef __cplusplus
}
#endif

#endif
