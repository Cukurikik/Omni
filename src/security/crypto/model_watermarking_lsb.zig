const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// Least Significant Bit (LSB) Model Watermarking
/// Mathematically evaluates steganographic injection of cryptographic identifiers into the mantissas of FP32 tensors to track model provenance.
/// Absorbed from: Model-Security-Provenance

pub const WatermarkError = error{
    MessageTooLong,
    BufferTooSmall,
};

pub const ModelWatermarker = struct {

    /// Structurally injects an 8-bit character into the Least Significant Bits of 8 consecutive 32-bit floats.
    /// In IEEE 754 float32, mutating the lowest bit of the 23-bit mantissa introduces negligible error (~1e-7),
    /// preserving the neural network's accuracy while embedding the watermark.
    ///
    /// @param weights Slice of exactly 8 floats.
    /// @param char The byte to embed.
    fn embed_byte(weights: []f32, char: u8) !void {
        if (weights.len != 8) return WatermarkError.BufferTooSmall;

        for (0..8) |i| {
            // Reinterpret float as u32 to manipulate bits
            var bits: u32 = @bitCast(weights[i]);
            
            // Extract the i-th bit of the character
            const bit = @as(u32, (char >> @as(u3, @truncate(i))) & 1);
            
            // Clear the LSB of the float, then OR with the payload bit
            bits = (bits & 0xFFFFFFFE) | bit;
            
            // Reinterpret back to float
            weights[i] = @bitCast(bits);
        }
    }

    /// Extracts an 8-bit character from the LSBs of 8 consecutive floats.
    fn extract_byte(weights: []const f32) !u8 {
        if (weights.len != 8) return WatermarkError.BufferTooSmall;

        var char: u8 = 0;
        for (0..8) |i| {
            const bits: u32 = @bitCast(weights[i]);
            const bit = @as(u8, @truncate(bits & 1));
            char |= (bit << @as(u3, @truncate(i)));
        }
        return char;
    }

    /// Embeds a full ASCII string into a flattened model weight tensor.
    /// Adds a null terminator '\0' at the end to signify string termination.
    pub fn embed_watermark(weights: []f32, message: []const u8) !void {
        // Need 8 floats per byte, plus 8 floats for the null terminator
        const required_floats = (message.len + 1) * 8;
        if (weights.len < required_floats) {
            return WatermarkError.MessageTooLong;
        }

        var offset: usize = 0;

        // Embed payload
        for (message) |char| {
            try embed_byte(weights[offset .. offset + 8], char);
            offset += 8;
        }

        // Embed null terminator
        try embed_byte(weights[offset .. offset + 8], 0);
    }

    /// Reads the watermark back from the tensor until a null terminator is hit or max_len is reached.
    pub fn extract_watermark(weights: []const f32, buffer: []u8) !usize {
        var offset: usize = 0;
        var bytes_read: usize = 0;

        while (offset + 8 <= weights.len) {
            const char = try extract_byte(weights[offset .. offset + 8]);
            
            if (char == 0) {
                break; // Null terminator found
            }

            if (bytes_read < buffer.len) {
                buffer[bytes_read] = char;
                bytes_read += 1;
            } else {
                return WatermarkError.BufferTooSmall;
            }

            offset += 8;
        }

        return bytes_read;
    }
};
