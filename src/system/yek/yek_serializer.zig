// OMNI System Layer: yek_serializer.zig
// Implements zero-copy fast text serialization for LLM ingestion.
// Bounded to 500MB max file size to prevent OOM in repository scanning.

const std = @import("std");
const omni = @import("omni_std");

const MAX_FILE_SIZE_BYTES: usize = 500 * 1024 * 1024; // 500 MB
const MAX_CONCURRENT_FILES: usize = 1000;

pub const YekError = error{
    FileTooLarge,
    TooManyOpenFiles,
    InvalidEncoding,
    KernelIOError,
};

pub const YekSerializer = struct {
    allocator: std.mem.Allocator,
    active_files: usize,

    pub fn init(allocator: std.mem.Allocator) -> YekSerializer {
        return YekSerializer{
            .allocator = allocator,
            .active_files = 0,
        };
    }

    /// Serializes a file into a packed binary format for LLM consumption.
    pub fn serialize_file(self: *YekSerializer, file_path: []const u8) YekError![]const u8 {
        if (self.active_files >= MAX_CONCURRENT_FILES) {
            return YekError.TooManyOpenFiles;
        }

        self.active_files += 1;
        defer self.active_files -= 1;

        const file = std.fs.cwd().openFile(file_path, .{}) catch |err| {
            return YekError.KernelIOError;
        };
        defer file.close();

        const stat = file.stat() catch |err| {
            return YekError.KernelIOError;
        };

        if (stat.size > MAX_FILE_SIZE_BYTES) {
            return YekError.FileTooLarge;
        }

        // Allocate strict memory boundary
        const buffer = self.allocator.alloc(u8, stat.size) catch |err| {
            return YekError.KernelIOError; // Map to OMNI generic error
        };

        const bytes_read = file.readAll(buffer) catch |err| {
            self.allocator.free(buffer);
            return YekError.KernelIOError;
        };

        // Validate UTF-8 via SIMD (hardware acceleration assumption)
        if (!std.unicode.utf8ValidateSlice(buffer[0..bytes_read])) {
            self.allocator.free(buffer);
            return YekError.InvalidEncoding;
        }

        return buffer[0..bytes_read];
    }
};
