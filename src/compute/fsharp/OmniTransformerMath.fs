// OMNI Framework - F# Transformer Math Operations
// Pure functional implementations of common operations used in attention mechanisms

namespace Omni.Compute

module TransformerMath =
    let softmax (logits: float array) =
        let maxLogit = Array.max logits
        let exps = logits |> Array.map (fun x -> exp(x - maxLogit))
        let sumExps = Array.sum exps
        exps |> Array.map (fun x -> x / sumExps)

    let scaledDotProductAttention (queries: float[,]) (keys: float[,]) (values: float[,]) (dk: float) =
        // Conceptually: softmax(Q * K^T / sqrt(d_k)) * V
        // For a full implementation, matrix multiplication functions are needed.
        // This serves as a functional core representation.
        let scalingFactor = sqrt(dk)
        // Dummy return representing the weighted values
        values

    let gelu (x: float) =
        // Gaussian Error Linear Unit approximation
        let pi = System.Math.PI
        0.5 * x * (1.0 + tanh(sqrt(2.0 / pi) * (x + 0.044715 * x ** 3.0)))
