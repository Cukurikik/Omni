// Stable Diffusion — UNet Configurator (System Layer)
const std = @import("std");

pub const OmniResult = struct {
    is_ok: bool,
    alloc_size: u64,
    error_msg: [*:0]const u8,
};

export fn stablediff_compute_vram_requirement(
    image_size: u32,
    batch_size: u32,
    is_fp16: bool,
) OmniResult {
    if (image_size % 8 != 0) {
        return OmniResult{ .is_ok = false, .alloc_size = 0, .error_msg = "Image size must be mod 8" };
    }
    
    // Latent space is 1/8th resolution, 4 channels
    const latent_res = image_size / 8;
    const latent_elements = batch_size * 4 * latent_res * latent_res;
    const bytes_per_element = if (is_fp16) @as(u64, 2) else @as(u64, 4);
    
    // UNet activations roughly 50x latent size in training, 10x in inference
    const inference_vram = latent_elements * bytes_per_element * 10;
    
    return OmniResult{
        .is_ok = true,
        .alloc_size = inference_vram + (2 * 1024 * 1024 * 1024), // Base model 2GB
        .error_msg = "",
    };
}
