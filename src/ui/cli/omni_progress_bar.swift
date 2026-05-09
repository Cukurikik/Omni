// OmniProgressBar.swift — Terminal Progress Bar
// Layer: Interface / Swift
//
// Renders dynamic, animated progress bars in standard output for visualizing
// long-running tasks like tensor offloading or universal binary compilation.

import Foundation

class OmniProgressBar {
    private let total: Int
    private let width: Int
    private let prefix: String
    private var current: Int = 0
    
    init(total: Int, width: Int = 40, prefix: String = "Progress: ") {
        self.total = max(1, total) // Prevent division by zero
        self.width = width
        self.prefix = prefix
    }
    
    func update(_ value: Int) {
        self.current = min(self.total, max(0, value))
        self.render()
    }
    
    func increment() {
        self.current = min(self.total, self.current + 1)
        self.render()
    }
    
    private func render() {
        let percentage = Double(current) / Double(total)
        let filledCount = Int(Double(width) * percentage)
        let emptyCount = width - filledCount
        
        // █ = U+2588, ░ = U+2591
        let filledStr = String(repeating: "█", count: filledCount)
        let emptyStr = String(repeating: "░", count: emptyCount)
        
        let percentStr = String(format: "%3.1f%%", percentage * 100.0)
        
        // Use \r to overwrite the current line
        print("\r\u{001B}[0;34m\(prefix)\u{001B}[0m[\(filledStr)\(emptyStr)] \u{001B}[1;32m\(percentStr)\u{001B}[0m (\(current)/\(total))", terminator: "")
        
        // Flush stdout
        fflush(stdout)
        
        if current == total {
            print("") // Move to next line on completion
        }
    }
}

// Example usage
// let bar = OmniProgressBar(total: 100, prefix: "Building OMNI Kernel: ")
// for i in 1...100 {
//     bar.update(i)
//     usleep(10000) // Mock work
// }
