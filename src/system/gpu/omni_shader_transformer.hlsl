// omni_shader_transformer.hlsl — Compute Shader Transformer Attention
// Layer: Interface / GPU Native (Unity/DirectX)
// Inspired by: SCRN-VRC/Language-Translation-with-Fragment-Shaders
//
// Implements the Multi-Head Attention Q*K^T / sqrt(d) operation directly
// on GPU VRAM via HLSL Compute Shaders. Allows inference rendering to be 
// coupled with graphics pipelines without CPU bounce. Zero mock.

#pragma kernel OmniComputeAttention

// Defines
#define BLOCK_SIZE 16

// Buffers
StructuredBuffer<float> QueryBuffer;    // Size: Batch * SeqLen * D
StructuredBuffer<float> KeyBuffer;      // Size: Batch * SeqLen * D
StructuredBuffer<float> ValueBuffer;    // Size: Batch * SeqLen * D
RWStructuredBuffer<float> OutputBuffer; // Size: Batch * SeqLen * D

// Meta-parameters
cbuffer Params {
    uint BatchSize;
    uint SeqLen;
    uint HeadDim;
    uint NumHeads;
    float Scale; // Usually 1.0 / sqrt(HeadDim)
};

// Groupshared memory for tile-based matrix multiplication
groupshared float tileQ[BLOCK_SIZE][BLOCK_SIZE];
groupshared float tileK[BLOCK_SIZE][BLOCK_SIZE];

[numthreads(BLOCK_SIZE, BLOCK_SIZE, 1)]
void OmniComputeAttention (uint3 id : SV_DispatchThreadID, uint3 groupTid : SV_GroupThreadID, uint3 groupId : SV_GroupID) {
    uint row = id.y; // Corresponds to Query Token Index (0 to SeqLen - 1)
    uint col = id.x; // Corresponds to Key Token Index (0 to SeqLen - 1)
    uint headId = id.z; // Corresponds to Head Index

    // Prevent out of bounds
    if (row >= SeqLen || col >= SeqLen || headId >= NumHeads) {
        return;
    }

    float dotProduct = 0.0;
    uint qOffset = headId * SeqLen * HeadDim + row * HeadDim;
    uint kOffset = headId * SeqLen * HeadDim + col * HeadDim;

    // Loop over the HeadDim dimension in chunks of BLOCK_SIZE
    for (uint i = 0; i < HeadDim; i += BLOCK_SIZE) {
        
        // Load into shared memory
        if (i + groupTid.x < HeadDim) {
            tileQ[groupTid.y][groupTid.x] = QueryBuffer[qOffset + i + groupTid.x];
            tileK[groupTid.x][groupTid.y] = KeyBuffer[kOffset + i + groupTid.x]; 
            // Note: K is transposed during shared load
        } else {
            tileQ[groupTid.y][groupTid.x] = 0.0;
            tileK[groupTid.x][groupTid.y] = 0.0;
        }

        GroupMemoryBarrierWithGroupSync();

        // Compute dot product for this tile
        for (uint j = 0; j < BLOCK_SIZE; ++j) {
            dotProduct += tileQ[groupTid.y][j] * tileK[j][groupTid.x];
        }

        GroupMemoryBarrierWithGroupSync();
    }

    // Apply scaling factor (1 / sqrt(d))
    dotProduct *= Scale;

    // Output to a raw Attention Matrix buffer.
    // NOTE: A subsequent compute shader would apply Softmax and multiply by ValueBuffer.
    // Due to HLSL constraints, separating QK^T and Softmax(QK^T)*V into two kernels
    // ensures synchronicity across the sequence length during the softmax reduction.
    
    uint outIndex = headId * SeqLen * SeqLen + row * SeqLen + col;
    OutputBuffer[outIndex] = dotProduct;
}
