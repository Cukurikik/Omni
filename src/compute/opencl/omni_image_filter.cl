// OMNI Framework - OpenCL Kernel for Image Pre-processing
// Accelerates contrast normalization before Inverse DALL-E feature extraction

__kernel void normalize_contrast(
    __global const uchar* input_image,
    __global uchar* output_image,
    const int width,
    const int height,
    const float min_val,
    const float max_val) 
{
    // Get the index of the current work item
    int id = get_global_id(0);
    
    // Ensure we don't read out of bounds
    if (id < width * height) {
        float pixel = (float)input_image[id];
        
        // Normalize pixel to [0, 255] based on min/max bounds
        float normalized = ((pixel - min_val) / (max_val - min_val)) * 255.0f;
        
        // Clamp bounds
        if (normalized > 255.0f) normalized = 255.0f;
        if (normalized < 0.0f) normalized = 0.0f;
        
        output_image[id] = (uchar)normalized;
    }
}
