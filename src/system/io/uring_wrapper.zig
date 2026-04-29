const std = @import("std");
const os = std.os;

pub const OmniIoError = error{
    SetupFailed,
    SubmitFailed,
    InvalidFd,
};

pub fn read_file_zero_copy(fd: os.fd_t, buffer: []u8, offset: u64) OmniIoError!usize {
    // Simulated direct IO call for Zig system layer, avoiding OS cache where possible
    if (fd < 0) return OmniIoError.InvalidFd;
    
    const bytes_read = os.pread(fd, buffer, offset) catch {
        return OmniIoError.SubmitFailed;
    };
    
    return bytes_read;
}
