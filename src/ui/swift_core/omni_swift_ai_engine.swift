// ============================================================================
// OmniSwiftAiEngine — Native Swift Neural Network Engine
//
// Studied from: Swift-AI/Swift-AI (6.1k★)
// Implements: Feed-forward neural network with configurable hidden layers,
// activation functions (Sigmoid, ReLU, Tanh), backpropagation with SGD,
// weight initialization (Xavier/He), and inference API.
//
// Key insights from Swift-AI:
// - Uses Apple Accelerate framework for BLAS-level matrix ops
// - NeuralNet struct with layer-wise weight matrices
// - Backpropagation with configurable learning rate and momentum
//
// OMNI Domain: ui/ (Swift — Apple ecosystem / spatial computing)
// CODE RULE 001-005 compliant.
// ============================================================================

import Foundation

// MARK: - Engine Metadata

let ENGINE_VERSION = "1.0.0-omni"
let ENGINE_NAME = "OmniSwiftAiEngine"

// MARK: - Activation Functions

/// Activation function types supported by the neural network.
enum ActivationFunction {
    case sigmoid
    case relu
    case tanh
    case linear

    /// Compute the activation value.
    func activate(_ x: Double) -> Double {
        switch self {
        case .sigmoid:
            return 1.0 / (1.0 + exp(-max(min(x, 500), -500)))
        case .relu:
            return max(0.0, x)
        case .tanh:
            return Foundation.tanh(x)
        case .linear:
            return x
        }
    }

    /// Compute the derivative given the activation output.
    func derivative(_ output: Double) -> Double {
        switch self {
        case .sigmoid:
            return output * (1.0 - output)
        case .relu:
            return output > 0 ? 1.0 : 0.0
        case .tanh:
            return 1.0 - output * output
        case .linear:
            return 1.0
        }
    }
}

// MARK: - Weight Initialization

/// Weight initialization strategies studied from Swift-AI's NeuralNet.
enum WeightInit {
    case xavier
    case he
    case uniform(range: Double)

    /// Generate a random weight for a layer with given fan-in and fan-out.
    func generate(fanIn: Int, fanOut: Int) -> Double {
        let limit: Double
        switch self {
        case .xavier:
            limit = sqrt(6.0 / Double(fanIn + fanOut))
        case .he:
            limit = sqrt(2.0 / Double(fanIn))
        case .uniform(let range):
            limit = range
        }
        return Double.random(in: -limit...limit)
    }
}

// MARK: - Layer Configuration

/// Configuration for a single layer in the network.
struct LayerConfig {
    let neurons: Int
    let activation: ActivationFunction

    init(neurons: Int, activation: ActivationFunction = .sigmoid) {
        self.neurons = neurons
        self.activation = activation
    }
}

// MARK: - Dense Layer

/// A fully-connected layer with weights, biases, and activation.
struct DenseLayer {
    var weights: [[Double]]  // [outputNeurons × inputNeurons]
    var biases: [Double]     // [outputNeurons]
    let activation: ActivationFunction
    var outputs: [Double]    // Cached activations for backprop

    /// Create a dense layer with initialized weights.
    init(inputSize: Int, outputSize: Int,
         activation: ActivationFunction = .sigmoid,
         weightInit: WeightInit = .xavier) {
        self.activation = activation
        self.outputs = Array(repeating: 0.0, count: outputSize)
        self.biases = Array(repeating: 0.0, count: outputSize)
        self.weights = (0..<outputSize).map { _ in
            (0..<inputSize).map { _ in
                weightInit.generate(fanIn: inputSize, fanOut: outputSize)
            }
        }
    }

    /// Forward pass: compute y = activation(Wx + b).
    mutating func forward(input: [Double]) -> [Double] {
        let outputSize = weights.count
        let inputSize = input.count
        var result = Array(repeating: 0.0, count: outputSize)

        for j in 0..<outputSize {
            var sum = biases[j]
            for i in 0..<inputSize {
                sum += weights[j][i] * input[i]
            }
            result[j] = activation.activate(sum)
        }

        outputs = result
        return result
    }
}

// MARK: - Neural Network

/// Feed-forward neural network with backpropagation training.
///
/// Architecture studied from Swift-AI's NeuralNet:
/// - Configurable hidden layers and activation functions
/// - Backpropagation with learning rate and momentum
/// - MSE loss computation
struct NeuralNetwork {
    var layers: [DenseLayer]
    var learningRate: Double
    var momentum: Double
    private var previousDeltas: [[[Double]]]  // momentum storage

    /// Initialize a neural network.
    ///
    /// - Parameters:
    ///   - inputSize: Number of input features.
    ///   - hiddenLayers: Configuration for hidden layers.
    ///   - outputSize: Number of output neurons.
    ///   - learningRate: Learning rate for SGD.
    ///   - momentum: Momentum coefficient.
    ///   - weightInit: Weight initialization strategy.
    init(inputSize: Int,
         hiddenLayers: [LayerConfig],
         outputSize: Int,
         outputActivation: ActivationFunction = .sigmoid,
         learningRate: Double = 0.01,
         momentum: Double = 0.9,
         weightInit: WeightInit = .xavier) {

        self.learningRate = learningRate
        self.momentum = momentum
        self.layers = []
        self.previousDeltas = []

        var prevSize = inputSize

        // Build hidden layers
        for config in hiddenLayers {
            let layer = DenseLayer(
                inputSize: prevSize,
                outputSize: config.neurons,
                activation: config.activation,
                weightInit: weightInit
            )
            layers.append(layer)
            previousDeltas.append(
                Array(repeating: Array(repeating: 0.0, count: prevSize),
                      count: config.neurons)
            )
            prevSize = config.neurons
        }

        // Output layer
        let outputLayer = DenseLayer(
            inputSize: prevSize,
            outputSize: outputSize,
            activation: outputActivation,
            weightInit: weightInit
        )
        layers.append(outputLayer)
        previousDeltas.append(
            Array(repeating: Array(repeating: 0.0, count: prevSize),
                  count: outputSize)
        )
    }

    /// Forward pass through the entire network.
    ///
    /// - Parameter input: Input feature vector.
    /// - Returns: Network output vector.
    mutating func predict(input: [Double]) -> [Double] {
        var current = input
        for i in 0..<layers.count {
            current = layers[i].forward(input: current)
        }
        return current
    }

    /// Train on a single sample using backpropagation with SGD + momentum.
    ///
    /// - Parameters:
    ///   - input: Training input.
    ///   - target: Expected output.
    /// - Returns: MSE loss for this sample.
    @discardableResult
    mutating func train(input: [Double], target: [Double]) -> Double {
        // Forward pass (stores activations)
        let output = predict(input: input)

        // Compute MSE loss
        var loss = 0.0
        for i in 0..<output.count {
            let diff = output[i] - target[i]
            loss += diff * diff
        }
        loss /= Double(output.count)

        // Backward pass
        let layerCount = layers.count

        // Compute output layer errors
        var errors: [[Double]] = Array(repeating: [], count: layerCount)
        var outputErrors = Array(repeating: 0.0, count: output.count)
        for i in 0..<output.count {
            let err = output[i] - target[i]
            outputErrors[i] = err * layers[layerCount - 1].activation.derivative(output[i])
        }
        errors[layerCount - 1] = outputErrors

        // Propagate errors backwards
        for l in stride(from: layerCount - 2, through: 0, by: -1) {
            let nextLayer = layers[l + 1]
            let nextErrors = errors[l + 1]
            var layerErrors = Array(repeating: 0.0, count: layers[l].outputs.count)

            for j in 0..<layers[l].outputs.count {
                var sum = 0.0
                for k in 0..<nextErrors.count {
                    sum += nextErrors[k] * nextLayer.weights[k][j]
                }
                layerErrors[j] = sum * layers[l].activation.derivative(layers[l].outputs[j])
            }
            errors[l] = layerErrors
        }

        // Update weights with momentum
        for l in 0..<layerCount {
            let layerInput: [Double]
            if l == 0 {
                layerInput = input
            } else {
                layerInput = layers[l - 1].outputs
            }

            for j in 0..<layers[l].weights.count {
                for i in 0..<layers[l].weights[j].count {
                    let delta = -learningRate * errors[l][j] * layerInput[i]
                        + momentum * previousDeltas[l][j][i]
                    layers[l].weights[j][i] += delta
                    previousDeltas[l][j][i] = delta
                }
                // Update bias
                layers[l].biases[j] -= learningRate * errors[l][j]
            }
        }

        return loss
    }

    /// Train on a dataset for multiple epochs.
    ///
    /// - Parameters:
    ///   - data: List of (input, target) pairs.
    ///   - epochs: Number of training epochs.
    /// - Returns: List of average loss per epoch.
    mutating func fit(data: [([Double], [Double])], epochs: Int) -> [Double] {
        var epochLosses: [Double] = []

        for _ in 0..<epochs {
            var totalLoss = 0.0
            var shuffled = data
            shuffled.shuffle()

            for (input, target) in shuffled {
                totalLoss += train(input: input, target: target)
            }

            epochLosses.append(totalLoss / Double(data.count))
        }

        return epochLosses
    }
}

// MARK: - Engine Facade

/// Production-grade Swift neural network engine.
///
/// Capabilities:
///   - Feed-forward neural network with configurable architecture
///   - Sigmoid/ReLU/Tanh/Linear activations
///   - Backpropagation with SGD + momentum
///   - Xavier/He weight initialization
///   - Single-sample and batch training
///   - Inference API
class OmniSwiftAiEngine {
    private let version: String
    private let name: String

    init() {
        self.version = ENGINE_VERSION
        self.name = ENGINE_NAME
    }

    /// Create a neural network.
    ///
    /// - Parameters:
    ///   - inputSize: Input feature dimension.
    ///   - hidden: Hidden layer configurations.
    ///   - outputSize: Output dimension.
    ///   - learningRate: SGD learning rate.
    /// - Returns: Configured NeuralNetwork.
    func createNetwork(
        inputSize: Int,
        hidden: [LayerConfig],
        outputSize: Int,
        learningRate: Double = 0.01
    ) -> NeuralNetwork {
        return NeuralNetwork(
            inputSize: inputSize,
            hiddenLayers: hidden,
            outputSize: outputSize,
            learningRate: learningRate
        )
    }

    /// Engine health diagnostics.
    func health() -> [String: Any] {
        return [
            "engine": name,
            "version": version,
            "status": "operational",
            "activations": ["sigmoid", "relu", "tanh", "linear"],
            "weight_init": ["xavier", "he", "uniform"],
            "optimizer": "sgd_momentum",
            "capabilities": [
                "feed_forward_network",
                "backpropagation",
                "configurable_hidden_layers",
                "batch_training",
                "inference"
            ]
        ]
    }
}
