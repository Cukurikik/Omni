# @omni-layer System | @omni-lang Assembly (RISC-V RV64) | @omni-batch 17
# @omni-description RISC-V vector dot product: RV64GV vector extension
# accelerated float32 dot product for edge AI inference.
# Uses RISC-V "V" vector extension (RVV 1.0)

    .text
    .global omni_dot_product_rvv
    .global omni_relu_rvv

# float omni_dot_product_rvv(const float* a, const float* b, int64_t n)
# a0 = pointer to A, a1 = pointer to B, a2 = count
# Returns fa0 = dot product
omni_dot_product_rvv:
    fmv.w.x     fa0, zero           # acc = 0.0
    beqz        a2, .dot_done       # if n == 0, return

.dot_loop:
    vsetvli     t0, a2, e32, m4     # set vector length (32-bit, LMUL=4)
    vle32.v     v0, (a0)            # load A[i:i+vl]
    vle32.v     v4, (a1)            # load B[i:i+vl]
    vfmul.vv    v8, v0, v4          # v8 = A * B
    vfredusum.vs v12, v8, v12       # reduce sum into v12[0]
    vfmv.f.s    ft0, v12            # extract scalar
    fadd.s      fa0, fa0, ft0       # accumulate

    slli        t1, t0, 2           # t1 = vl * 4 (bytes)
    add         a0, a0, t1          # advance A pointer
    add         a1, a1, t1          # advance B pointer
    sub         a2, a2, t0          # remaining -= vl
    bnez        a2, .dot_loop       # continue if remaining > 0

.dot_done:
    ret

# void omni_relu_rvv(float* data, int64_t n)
# a0 = data pointer, a1 = count
omni_relu_rvv:
    fmv.w.x     ft0, zero           # ft0 = 0.0
    beqz        a1, .relu_done

.relu_loop:
    vsetvli     t0, a1, e32, m4     # set vector length
    vle32.v     v0, (a0)            # load data[i:i+vl]
    vfmax.vf    v0, v0, ft0         # max(data, 0.0)
    vse32.v     v0, (a0)            # store back

    slli        t1, t0, 2
    add         a0, a0, t1
    sub         a1, a1, t0
    bnez        a1, .relu_loop

.relu_done:
    ret
