# OMNI System Layer — RISC-V Vector Extension Dot Product
# RVV (RISC-V Vector) accelerated dot product for edge AI.
# float omni_rvv_dot_f32(const float* a, const float* b, size_t n);

.global omni_rvv_dot_f32
.type omni_rvv_dot_f32, @function

# a0 = const float* a
# a1 = const float* b
# a2 = size_t n
# Returns: fa0 = float result

omni_rvv_dot_f32:
    # Initialize accumulator
    fmv.w.x     fa0, zero           # fa0 = 0.0 (result)
    vsetvli     zero, zero, e32, m4 # Set vector length for f32
    vmv.v.i     v0, 0               # v0 = vector accumulator

.Lrvv_loop:
    beqz        a2, .Lrvv_reduce    # If n == 0, go to reduce
    vsetvli     t0, a2, e32, m4     # Set vl = min(vlmax, n)

    # Vector load
    vle32.v     v4, (a0)            # v4 = a[0..vl-1]
    vle32.v     v8, (a1)            # v8 = b[0..vl-1]

    # Vector fused multiply-add: v0 += v4 * v8
    vfmacc.vv   v0, v4, v8

    # Advance pointers
    slli        t1, t0, 2           # t1 = vl * 4 bytes
    add         a0, a0, t1
    add         a1, a1, t1
    sub         a2, a2, t0
    j           .Lrvv_loop

.Lrvv_reduce:
    # Horizontal reduction of vector accumulator
    vsetvli     t0, zero, e32, m4
    vmv.s.x     v12, zero           # v12[0] = 0.0
    vfredusum.vs v12, v0, v12       # v12[0] = sum(v0)
    vfmv.f.s    fa0, v12            # fa0 = v12[0]
    ret
