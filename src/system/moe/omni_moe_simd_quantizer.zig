const std = @import("std");

/// OMNI MOTHER Production Zero-Mock SIMD Quantizer
/// Fast 32-bit float to 8-bit quantized int packing using Zig SIMD capabilities
/// Crucial for shrinking MoE Expert KV caches dynamically.

pub const QuantizerError = error{
    UnalignedBuffer,
    InvalidDimensions,
};

pub fn quantize_f32_to_i8_simd(input: []const f32, output: []i8, scale: f32) QuantizerError!void {
    if (input.len != output.len) return QuantizerError.InvalidDimensions;
    if (input.len % 8 != 0) return QuantizerError.UnalignedBuffer;

    const vector_len = 8;
    const V = @Vector(vector_len, f32);
    const VI = @Vector(vector_len, i8);

    const scale_vec: V = @splat(scale);
    
    var i: usize = 0;
    while (i < input.len) : (i += vector_len) {
        // Load f32 slice into SIMD vector
        const in_vec: V = input[i..][0..vector_len].*;
        
        // Multiply by scale factor
        const scaled: V = in_vec * scale_vec;
        
        // Float to Int cast (using builtins)
        const int_vec: @Vector(vector_len, i32) = @intFromFloat(scaled);
        
        // Clamp bounds to i8 limits
        var out_vec: VI = undefined;
        comptime var j = 0;
        inline while (j < vector_len) : (j += 1) {
            var val = int_vec[j];
            if (val > 127) val = 127;
            if (val < -128) val = -128;
            out_vec[j] = @intCast(val);
        }
        
        // Store directly to output slice
        output[i..][0..vector_len].* = out_vec;
    }
}

test "quantizer tests" {
    var input = [_]f32{ 1.0, -1.0, 0.5, -0.5, 2.0, -2.0, 0.0, 10.0 };
    var output: [8]i8 = undefined;
    
    try quantize_f32_to_i8_simd(&input, &output, 100.0);
    
    try std.testing.expectEqual(@as(i8, 100), output[0]);
    try std.testing.expectEqual(@as(i8, -100), output[1]);
    try std.testing.expectEqual(@as(i8, 50), output[2]);
    try std.testing.expectEqual(@as(i8, 127), output[7]); // Clamped
}
