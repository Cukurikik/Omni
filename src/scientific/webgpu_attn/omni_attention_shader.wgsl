// @omni-layer Scientific | @omni-lang WGSL | @omni-batch 18 | @omni-semester 16
// @omni-description WebGPU shader for browser-based transformer inference:
// matrix multiply compute shader for attention score computation.

struct Params {
    M: u32,   // rows of A / rows of C
    N: u32,   // cols of B / cols of C
    K: u32,   // cols of A / rows of B
    scale: f32,
};

@group(0) @binding(0) var<uniform> params: Params;
@group(0) @binding(1) var<storage, read> matQ: array<f32>;
@group(0) @binding(2) var<storage, read> matK: array<f32>;
@group(0) @binding(3) var<storage, read_write> matOut: array<f32>;

const TILE_SIZE: u32 = 16u;

var<workgroup> tileA: array<array<f32, 16>, 16>;
var<workgroup> tileB: array<array<f32, 16>, 16>;

@compute @workgroup_size(16, 16, 1)
fn matmul_attention(@builtin(global_invocation_id) gid: vec3<u32>,
                     @builtin(local_invocation_id) lid: vec3<u32>) {
    let row = gid.x;
    let col = gid.y;

    if (row >= params.M || col >= params.N) {
        return;
    }

    var sum: f32 = 0.0;

    let numTiles = (params.K + TILE_SIZE - 1u) / TILE_SIZE;

    for (var t: u32 = 0u; t < numTiles; t = t + 1u) {
        let aCol = t * TILE_SIZE + lid.y;
        let bRow = t * TILE_SIZE + lid.x;

        if (row < params.M && aCol < params.K) {
            tileA[lid.x][lid.y] = matQ[row * params.K + aCol];
        } else {
            tileA[lid.x][lid.y] = 0.0;
        }

        if (bRow < params.K && col < params.N) {
            tileB[lid.x][lid.y] = matK[bRow * params.N + col];
        } else {
            tileB[lid.x][lid.y] = 0.0;
        }

        workgroupBarrier();

        for (var k: u32 = 0u; k < TILE_SIZE; k = k + 1u) {
            sum = sum + tileA[lid.x][k] * tileB[k][lid.y];
        }

        workgroupBarrier();
    }

    matOut[row * params.N + col] = sum * params.scale;
}

// Softmax compute shader - per row normalization
@group(0) @binding(0) var<uniform> softmax_params: Params;
@group(0) @binding(1) var<storage, read_write> scores: array<f32>;

@compute @workgroup_size(256, 1, 1)
fn softmax_kernel(@builtin(global_invocation_id) gid: vec3<u32>) {
    let row = gid.x;
    if (row >= softmax_params.M) {
        return;
    }

    let n = softmax_params.N;
    var maxVal: f32 = -1e30;

    for (var j: u32 = 0u; j < n; j = j + 1u) {
        let v = scores[row * n + j];
        if (v > maxVal) { maxVal = v; }
    }

    var sum: f32 = 0.0;
    for (var j: u32 = 0u; j < n; j = j + 1u) {
        let e = exp(scores[row * n + j] - maxVal);
        scores[row * n + j] = e;
        sum = sum + e;
    }

    let inv = 1.0 / (sum + 1e-10);
    for (var j: u32 = 0u; j < n; j = j + 1u) {
        scores[row * n + j] = scores[row * n + j] * inv;
    }
}
