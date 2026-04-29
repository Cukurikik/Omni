#include <fcntl.h>

namespace OmniVision {
    int open_camera(const char* dev) {
        int fd = open(dev, O_RDWR);
        return fd;
    }
}
