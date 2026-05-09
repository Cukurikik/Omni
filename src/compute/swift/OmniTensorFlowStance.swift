// OMNI Framework - Swift for TensorFlow Stance Detection Layer
// Represents a modular layer for KE-MLM operations.

import TensorFlow

public struct OmniStanceDenseLayer: Layer {
    public var weight: Tensor<Float>
    public var bias: Tensor<Float>

    public init(inputSize: Int, outputSize: Int) {
        weight = Tensor<Float>(glorotUniform: [inputSize, outputSize])
        bias = Tensor<Float>(zeros: [outputSize])
    }

    @differentiable
    public func callAsFunction(_ input: Tensor<Float>) -> Tensor<Float> {
        return matmul(input, weight) + bias
    }
}

public struct OmniStanceClassifier: Layer {
    public var hidden: OmniStanceDenseLayer
    public var output: OmniStanceDenseLayer

    public init(hiddenSize: Int, numClasses: Int) {
        hidden = OmniStanceDenseLayer(inputSize: hiddenSize, outputSize: hiddenSize / 2)
        output = OmniStanceDenseLayer(inputSize: hiddenSize / 2, outputSize: numClasses)
    }

    @differentiable
    public func callAsFunction(_ input: Tensor<Float>) -> Tensor<Float> {
        let hiddenActivation = relu(hidden(input))
        return output(hiddenActivation)
    }
}
