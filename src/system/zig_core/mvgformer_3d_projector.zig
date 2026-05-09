const std = @import("std");

pub const MVGProjector = struct {
    pub fn project_3d_to_2d(x: f32, y: f32, z: f32, focal_length: f32) !struct{u: f32, v: f32} {
        if (z == 0.0) return error.DivisionByZero;
        
        return .{
            .u = (x * focal_length) / z,
            .v = (y * focal_length) / z,
        };
    }
};
