#include <fcntl.h>
#include <unistd.h>
#include <string>

namespace OmniDB {
    int write_page(const std::string& path, const char* data, size_t size) {
        int fd = open(path.c_str(), O_WRONLY | O_CREAT, 0644);
        if (fd < 0) return -1;
        ssize_t written = write(fd, data, size);
        close(fd);
        return (written == size) ? 0 : -1;
    }
}
