#=============================================================================
# OMNI COMPUTE LAYER — MFCC VISUALIZER DATA (JULIA)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Prepares MFCC acoustic data arrays specifically formatted for 
#              frontend WebGL rendering in the Interface Layer.
#=============================================================================

module MFCCVisualizer

using Statistics

export prepare_spectrogram_for_ui

"""
OMNI IDIOM: Fast data transformation for frontend rendering
Downsamples and normalizes high-resolution MFCC data so the UI can render 
smooth 60fps spectrograms without browser lag.
"""
function prepare_spectrogram_for_ui(mfcc_matrix::Matrix{Float32}, target_width::Int, target_height::Int)::Matrix{Float32}
    rows, cols = size(mfcc_matrix)
    
    # 1. Zero-mock validation
    if rows == 0 || cols == 0
        return zeros(Float32, target_height, target_width)
    end
    
    # 2. Downsampling (Nearest Neighbor interpolation for speed)
    ui_matrix = Matrix{Float32}(undef, target_height, target_width)
    
    row_ratio = rows / target_height
    col_ratio = cols / target_width
    
    Threads.@threads for r in 1:target_height
        src_r = floor(Int, (r - 1) * row_ratio) + 1
        for c in 1:target_width
            src_c = floor(Int, (c - 1) * col_ratio) + 1
            ui_matrix[r, c] = mfcc_matrix[src_r, src_c]
        end
    end
    
    # 3. Global Normalization (0.0 to 1.0) for WebGL shaders
    max_val = maximum(ui_matrix)
    min_val = minimum(ui_matrix)
    range_val = max_val - min_val > 0 ? (max_val - min_val) : 1.0f0
    
    ui_matrix .= (ui_matrix .- min_val) ./ range_val
    
    return ui_matrix
end

end # module
