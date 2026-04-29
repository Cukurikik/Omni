// OMNI System Layer - MemGPT OS Bridge
#include <fcntl.h>
#include <unistd.h>
#include <string.h>

typedef enum {
    OK = 0,
    ERR_OPEN = 1,
    ERR_WRITE = 2
} IOErrorCode;

typedef struct {
    bool success;
    IOErrorCode error;
} IOResult;

extern "omni-c" IOResult write_to_disk_cache(const char* filepath, const char* data) {
    if (!filepath || !data) return (IOResult){false, ERR_OPEN};
    
    int fd = open(filepath, O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (fd < 0) return (IOResult){false, ERR_OPEN};
    
    ssize_t written = write(fd, data, strlen(data));
    close(fd);
    
    if (written < 0) return (IOResult){false, ERR_WRITE};
    return (IOResult){true, OK};
}
