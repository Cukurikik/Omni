// moe_swift_coreml_bridge.swift — System / Mobile
// Layer: System / CoreML — iOS MoE Execution Bridge
//
// To execute the OMNI MoE natively on iPhones/iPads, we cannot rely on CUDA.
// This Swift module provides the bridge to Apple's CoreML engine, utilizing the 
// Apple Neural Engine (ANE) for highly efficient, low-power inference of 
// local on-device experts.

import Foundation
import CoreML

public class MoeCoreMLBridge {
    private var expertModels: [Int: MLModel] = [:]
    
    public init() {
        print("[CoreML Bridge] Initialized iOS Apple Neural Engine (ANE) Interface.")
    }
    
    /// Loads an compiled .mlmodelc expert from the iOS app bundle into ANE memory.
    public func loadExpert(expertId: Int, bundlePath: String) throws {
        guard let modelUrl = URL(string: bundlePath) else {
            print("[CoreML Bridge] Error: Invalid URL for Expert \(expertId).")
            return
        }
        
        let config = MLModelConfiguration()
        // Force the model to use the Neural Engine and GPU for maximum efficiency
        config.computeUnits = .all
        
        do {
            let model = try MLModel(contentsOf: modelUrl, configuration: config)
            expertModels[expertId] = model
            print("[CoreML Bridge] Expert \(expertId) successfully loaded into ANE.")
        } catch {
            print("[CoreML Bridge] Failed to load Expert \(expertId): \(error)")
            throw error
        }
    }
    
    /// Executes a forward pass through the specified CoreML expert.
    public func executeExpert(expertId: Int, inputTensor: MLMultiArray) -> MLMultiArray? {
        guard let model = expertModels[expertId] else {
            print("[CoreML Bridge] Error: Expert \(expertId) is not loaded.")
            return nil
        }
        
        do {
            // Create the feature provider map matching the model's expected inputs
            let inputName = "hidden_states" // Standardized input name for OMNI CoreML export
            let featureProvider = try MLDictionaryFeatureProvider(dictionary: [inputName: inputTensor])
            
            // Perform inference on the ANE
            let output = try model.prediction(from: featureProvider)
            
            // Extract the resulting tensor
            if let outputTensor = output.featureValue(for: "output")?.multiArrayValue {
                return outputTensor
            } else {
                print("[CoreML Bridge] Error: Output feature 'output' not found.")
                return nil
            }
            
        } catch {
            print("[CoreML Bridge] Inference failed for Expert \(expertId): \(error)")
            return nil
        }
    }
}
