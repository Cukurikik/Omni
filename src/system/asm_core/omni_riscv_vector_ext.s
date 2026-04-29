# Omni RISC-V Vector Extension Assembly
# Highly optimized vector operations for embedded edge devices.

.global omni_riscv_vadd
.type omni_riscv_vadd, @function

# void omni_riscv_vadd(float* a, float* b, float* c, size_t n)
# a0 = a, a1 = b, a2 = c, a3 = n
omni_riscv_vadd:
    vsetvli t0, a3, e32, m8, ta, ma  # Set vector length based on a3 (n)
    beq t0, zero, .done              # If n == 0, exit

.loop:
    vle32.v v8, (a0)                 # Load vector A
    vle32.v v16, (a1)                # Load vector B
    vfadd.vv v24, v8, v16            # Add vectors
    vse32.v v24, (a2)                # Store vector C

    slli t1, t0, 2                   # Multiply elements processed by 4 bytes
    add a0, a0, t1                   # Advance pointer A
    add a1, a1, t1                   # Advance pointer B
    add a2, a2, t1                   # Advance pointer C
    sub a3, a3, t0                   # Decrement remaining elements
    
    vsetvli t0, a3, e32, m8, ta, ma  # Update vector length
    bnez t0, .loop                   # Loop if remaining > 0

.done:
    ret
