const std = @import("std");
const neo = @import("../../neo/native_vlm_bridge.zig");

test "Native VLM bridge tensor multiplication" {
    var visual: [4]f32 = .{1.0, 2.0, 3.0, 4.0};
    var text: [4]f32 = .{0.5, 0.5, 0.5, 0.5};
    
    const result = neo.bridge_vlm_tensors(&visual, &text, 4);
    
    try std.testing.expect(result.is_ok == true);
    try std.testing.expect(result.value == 5.0);
}
