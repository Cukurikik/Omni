// OmniAnsiColors.swift — ANSI Terminal Colors
// Layer: Interface / Swift
//
// Utility structure for printing stylized, colored text to standard output
// for the local OMNI CLI and log streams.

import Foundation

struct ANSIColors {
    static let reset = "\u{001B}[0m"
    
    static let black = "\u{001B}[0;30m"
    static let red = "\u{001B}[0;31m"
    static let green = "\u{001B}[0;32m"
    static let yellow = "\u{001B}[0;33m"
    static let blue = "\u{001B}[0;34m"
    static let magenta = "\u{001B}[0;35m"
    static let cyan = "\u{001B}[0;36m"
    static let white = "\u{001B}[0;37m"
    
    // Bold variants
    static let boldBlack = "\u{001B}[1;30m"
    static let boldRed = "\u{001B}[1;31m"
    static let boldGreen = "\u{001B}[1;32m"
    static let boldYellow = "\u{001B}[1;33m"
    static let boldBlue = "\u{001B}[1;34m"
    static let boldMagenta = "\u{001B}[1;35m"
    static let boldCyan = "\u{001B}[1;36m"
    static let boldWhite = "\u{001B}[1;37m"
}

struct OmniLogger {
    static func info(_ message: String) {
        print("\(ANSIColors.boldBlue)[INFO]\(ANSIColors.reset) \(message)")
    }
    
    static func success(_ message: String) {
        print("\(ANSIColors.boldGreen)[SUCCESS]\(ANSIColors.reset) \(message)")
    }
    
    static func warning(_ message: String) {
        print("\(ANSIColors.boldYellow)[WARNING]\(ANSIColors.reset) \(message)")
    }
    
    static func error(_ message: String) {
        print("\(ANSIColors.boldRed)[ERROR]\(ANSIColors.reset) \(message)")
    }
    
    static func highlight(_ message: String) -> String {
        return "\(ANSIColors.boldCyan)\(message)\(ANSIColors.reset)"
    }
}
