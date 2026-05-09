# omni_stale_detector.jl — Temporal Action Detection
# Inspired by: STALE (Zero-Shot Temporal Action Detection)
# Layer: Compute / Julia
#
# Vision-Language prompt matching for video segment classification.
# Utilizes Julia's fast multidimensional arrays and broadcast capabilities.

module OmniStaleDetector

using LinearAlgebra

export StaleConfig, TemporalSegment, detect_actions, compute_similarities

"""
Configuration for STALE Action Detection.
"""
struct StaleConfig
    threshold::Float64
    temperature::Float64
    max_segments::Int
end

Base.@kwdef struct StaleConfig
    threshold::Float64 = 0.5
    temperature::Float64 = 0.05
    max_segments::Int = 100
end

"""
Represents a predicted action segment in time.
"""
struct TemporalSegment
    start_time::Float64
    end_time::Float64
    action_label::String
    confidence::Float64
end

"""
Compute cosine similarities between video frame embeddings and text prompts.
- `video_features`: Matrix of size (Dim, Frames)
- `text_prompts`: Matrix of size (Dim, Classes)
Returns Matrix of size (Frames, Classes)
"""
function compute_similarities(video_features::Matrix{Float64}, text_prompts::Matrix{Float64}, config::StaleConfig)
    # Normalize features
    v_norms = sqrt.(sum(video_features.^2, dims=1))
    v_normalized = video_features ./ max.(v_norms, 1e-8)
    
    t_norms = sqrt.(sum(text_prompts.^2, dims=1))
    t_normalized = text_prompts ./ max.(t_norms, 1e-8)
    
    # Cosine similarity: (Dim, Frames)^T * (Dim, Classes) -> (Frames, Classes)
    sim_matrix = transpose(v_normalized) * t_normalized
    
    # Temperature scaling and softmax across classes
    scaled_sim = sim_matrix ./ config.temperature
    
    # Numerically stable softmax
    max_vals = maximum(scaled_sim, dims=2)
    exp_vals = exp.(scaled_sim .- max_vals)
    probs = exp_vals ./ sum(exp_vals, dims=2)
    
    return probs
end

"""
Extract continuous temporal segments from frame-level probabilities.
"""
function detect_actions(
    probs::Matrix{Float64}, 
    class_names::Vector{String}, 
    fps::Float64, 
    config::StaleConfig
)::Vector{TemporalSegment}
    
    num_frames, num_classes = size(probs)
    segments = TemporalSegment[]
    
    for c in 1:num_classes
        class_probs = probs[:, c]
        in_segment = false
        start_frame = 0
        seg_conf = 0.0
        
        for f in 1:num_frames
            if class_probs[f] > config.threshold
                if !in_segment
                    in_segment = true
                    start_frame = f
                    seg_conf = class_probs[f]
                else
                    seg_conf = max(seg_conf, class_probs[f])
                end
            else
                if in_segment
                    # End of segment
                    end_frame = f - 1
                    push!(segments, TemporalSegment(
                        (start_frame - 1) / fps,
                        end_frame / fps,
                        class_names[c],
                        seg_conf
                    ))
                    in_segment = false
                end
            end
        end
        
        # Handle segment at the end of video
        if in_segment
            push!(segments, TemporalSegment(
                (start_frame - 1) / fps,
                num_frames / fps,
                class_names[c],
                seg_conf
            ))
        end
    end
    
    # Sort by confidence descending and truncate
    sort!(segments, by = x -> x.confidence, rev = true)
    
    if length(segments) > config.max_segments
        return segments[1:config.max_segments]
    end
    
    return segments
end

end # module
