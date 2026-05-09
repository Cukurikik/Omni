// omni_loading_spinner.swift — CLI Async Spinner
// Layer: Interface / Swift
//
// Native asynchronous terminal spinner to indicate ongoing operations.
// Provides feedback during long compilation or network tasks. Zero mocks.

import Foundation

public class OmniLoadingSpinner {
    private let frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    private var isRunning = false
    private var task: Task<Void, Never>?
    private var currentText: String
    private let queue = DispatchQueue(label: "omni.cli.spinner")
    
    public init(text: String = "Loading...") {
        self.currentText = text
    }
    
    public func updateText(_ text: String) {
        queue.async {
            self.currentText = text
        }
    }
    
    public func start() {
        guard !isRunning else { return }
        isRunning = true
        
        task = Task {
            var frameIndex = 0
            
            while !Task.isCancelled {
                let frame = self.frames[frameIndex]
                
                self.queue.sync {
                    // \u{1B}[2K clears the line, \r returns to the beginning
                    print("\u{1B}[2K\r\(frame) \(self.currentText)", terminator: "")
                    fflush(stdout)
                }
                
                frameIndex = (frameIndex + 1) % self.frames.count
                
                do {
                    try await Task.sleep(nanoseconds: 80_000_000) // 80ms
                } catch {
                    break
                }
            }
        }
    }
    
    public func stop(success: Bool = true, message: String? = nil) {
        guard isRunning else { return }
        task?.cancel()
        isRunning = false
        
        queue.sync {
            let symbol = success ? "✓" : "✗"
            let msg = message ?? self.currentText
            print("\u{1B}[2K\r\(symbol) \(msg)")
            fflush(stdout)
        }
    }
}
