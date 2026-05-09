// @omni-layer System | @omni-lang RISC-V Assembly | @omni-batch 18 | @omni-semester 16
// @omni-description RISC-V vector extension (RVV) dot product kernel for
// transformer attention score computation on RISC-V hardware.

.section .text
.globl omni_rvv_dot_product
.globl omni_rvv_softmax
.type omni_rvv_dot_product, @function
.type omni_rvv_softmax, @function

# float omni_rvv_dot_product(const float* a, const float* b, int n)
# a0 = pointer to array a
# a1 = pointer to array b
# a2 = n (number of elements)
# Returns dot product in fa0
omni_rvv_dot_product:
    fcvt.s.w fa0, zero          # acc = 0.0
    beqz     a2, .dot_done

.dot_loop:
    vsetvli  t0, a2, e32, m4    # Set vector length for float32
    vle32.v  v0, (a0)           # Load a[i:i+vl]
    vle32.v  v4, (a1)           # Load b[i:i+vl]
    vfmul.vv v8, v0, v4         # v8 = a * b element-wise

    # Horizontal sum reduction
    vfredosum.vs v12, v8, v12   # Reduce sum
    vfmv.f.s ft0, v12           # Move scalar result
    fadd.s   fa0, fa0, ft0      # Accumulate

    slli     t1, t0, 2          # t1 = vl * 4 (sizeof float)
    add      a0, a0, t1         # Advance pointer a
    add      a1, a1, t1         # Advance pointer b
    sub      a2, a2, t0         # Remaining elements
    bnez     a2, .dot_loop

.dot_done:
    ret

# void omni_rvv_softmax(float* data, int n)
# a0 = pointer to float array (in-place)
# a1 = n
omni_rvv_softmax:
    addi     sp, sp, -32
    fsw      fs0, 0(sp)
    fsw      fs1, 4(sp)
    sw       s0, 8(sp)
    sw       s1, 12(sp)
    mv       s0, a0             # Save data pointer
    mv       s1, a1             # Save n

    # Phase 1: Find max
    li       a2, 0x FF800000    # -inf
    fmv.w.x  fs0, a2            # max = -inf
    mv       a0, s0
    mv       a2, s1

.max_loop:
    beqz     a2, .max_done
    vsetvli  t0, a2, e32, m4
    vle32.v  v0, (a0)
    vfredmax.vs v4, v0, v4
    vfmv.f.s ft0, v4
    fmax.s   fs0, fs0, ft0
    slli     t1, t0, 2
    add      a0, a0, t1
    sub      a2, a2, t0
    j        .max_loop

.max_done:
    # Phase 2: exp(x - max) and sum
    fcvt.s.w fs1, zero          # sum = 0.0
    mv       a0, s0
    mv       a2, s1

.exp_loop:
    beqz     a2, .exp_done
    vsetvli  t0, a2, e32, m4
    vle32.v  v0, (a0)
    vfsub.vf v0, v0, fs0        # x - max
    # Approximate exp using polynomial (Taylor)
    li       t2, 0x3F800000     # 1.0
    fmv.w.x  ft1, t2
    vfadd.vf v4, v0, ft1        # 1 + x (first-order approx)
    vse32.v  v4, (a0)           # Store exp approximation
    vfredosum.vs v8, v4, v8
    vfmv.f.s ft0, v8
    fadd.s   fs1, fs1, ft0
    slli     t1, t0, 2
    add      a0, a0, t1
    sub      a2, a2, t0
    j        .exp_loop

.exp_done:
    # Phase 3: Normalize by sum
    li       t2, 0x358637BD     # 1e-6
    fmv.w.x  ft1, t2
    fadd.s   fs1, fs1, ft1      # sum + eps
    mv       a0, s0
    mv       a2, s1

.norm_loop:
    beqz     a2, .norm_done
    vsetvli  t0, a2, e32, m4
    vle32.v  v0, (a0)
    vfdiv.vf v0, v0, fs1
    vse32.v  v0, (a0)
    slli     t1, t0, 2
    add      a0, a0, t1
    sub      a2, a2, t0
    j        .norm_loop

.norm_done:
    flw      fs0, 0(sp)
    flw      fs1, 4(sp)
    lw       s0, 8(sp)
    lw       s1, 12(sp)
    addi     sp, sp, 32
    ret
