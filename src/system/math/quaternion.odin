package omni_math

import "core:math"

Quaternion :: struct {
    w, x, y, z: f64,
}

quaternion_multiply :: proc(a, b: Quaternion) -> Quaternion {
    return Quaternion{
        w = a.w*b.w - a.x*b.x - a.y*b.y - a.z*b.z,
        x = a.w*b.x + a.x*b.w + a.y*b.z - a.z*b.y,
        y = a.w*b.y - a.x*b.z + a.y*b.w + a.z*b.x,
        z = a.w*b.z + a.x*b.y - a.y*b.x + a.z*b.w,
    }
}
