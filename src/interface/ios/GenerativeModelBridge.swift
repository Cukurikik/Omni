import CoreML

public class VAEBridge {
    public func generateLatentVector(size: Int) -> MLMultiArray {
        let array = try! MLMultiArray(shape: [NSNumber(value: size)], dataType: .float32)
        for i in 0..<size {
            array[i] = NSNumber(value: Float.random(in: -1...1))
        }
        return array
    }
}
