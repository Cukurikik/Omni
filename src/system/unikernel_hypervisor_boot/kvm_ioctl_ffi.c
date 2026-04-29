#include <stdint.h>

extern "C" {

// Fast FFI simulating bare-metal KVM (Kernel-based Virtual Machine) ioctls
// To run a unikernel, we use Linux KVM to create a virtual CPU and inject it with our binary.
void omni_kvm_run_vcpu_sim(
    int32_t vcpu_fd,
    int32_t* out_exit_reason,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!out_exit_reason || vcpu_fd < 0) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution simulation
    // Simulates the KVM_RUN ioctl, which transfers control from the host OS to the guest Unikernel.
    // The call blocks until the guest voluntarily yields (e.g., via HLT instruction or an I/O request).
    
    unsafe {
        // Deterministic mock data: KVM_EXIT_HLT (Guest went to sleep)
        *out_exit_reason = 1; // 1 = KVM_EXIT_HLT in linux headers
        *err_code = 0;
    }
}

}
