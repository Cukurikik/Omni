module Omni.Compute.GradientCheckpoint

using Zygote
using Flux

# OMNI MOTHER Production Zero-Mock Gradient Checkpointing
# Julia implementation of memory-efficient backpropagation for extremely large
# MoE models, recalculating forward passes during backward to save VRAM.

function checkpointed_chain(layers::Vector{Any}, x)
    # Forward pass
    # We only save the input to the chunk, and recalculate intermediate activations
    # during the backward pass.
    
    function forward_chunk(input)
        out = input
        for layer in layers
            out = layer(out)
        end
        return out
    end
    
    # Zygote.checkpoint tells the AD system to discard intermediate activations
    # and recompute them using `forward_chunk` when gradients are needed.
    return Zygote.checkpoint(forward_chunk, x)
end

# Example usage structure
struct CheckpointedMoE
    layer1
    layer2
    layer3
end

Flux.@functor CheckpointedMoE

function (m::CheckpointedMoE)(x)
    # Split execution into checkpoints to save memory
    out1 = checkpointed_chain([m.layer1], x)
    out2 = checkpointed_chain([m.layer2], out1)
    out3 = checkpointed_chain([m.layer3], out2)
    return out3
end

end # module
