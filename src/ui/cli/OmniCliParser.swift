// OmniCliParser.swift — Terminal Argument Parser
// Layer: Interface / Swift
//
// Utility for parsing command line arguments when interacting with the
// local OMNI tools, routing subcommands to the respective system layers.

import Foundation

enum CommandType {
    case chat
    case build
    case deploy
    case help
    case unknown
}

struct ParsedArgs {
    let command: CommandType
    let target: String?
    let isVerbose: Bool
}

class OmniCliParser {
    
    func parse(args: [String]) -> ParsedArgs {
        guard args.count > 1 else {
            return ParsedArgs(command: .help, target: nil, isVerbose: false)
        }
        
        let subCommand = args[1].lowercased()
        var target: String? = nil
        var verbose = false
        
        // Very basic parsing for structural completeness
        for (index, arg) in args.enumerated() {
            if arg == "-v" || arg == "--verbose" {
                verbose = true
            }
            if index == 2 && !arg.hasPrefix("-") {
                target = arg
            }
        }
        
        let cmd: CommandType
        switch subCommand {
        case "chat": cmd = .chat
        case "build": cmd = .build
        case "deploy": cmd = .deploy
        case "help": cmd = .help
        default: cmd = .unknown
        }
        
        return ParsedArgs(command: cmd, target: target, isVerbose: verbose)
    }
    
    func printHelp() {
        print("""
        🪐 OMNI FRAMEWORK CLI
        Usage: omni <command> [target] [options]
        
        Commands:
          chat      Start a local inference chat session
          build     Compile the universal binary (Requires target)
          deploy    Deploy the current workspace to the cloud
          help      Show this message
          
        Options:
          -v, --verbose   Enable debug output
        """)
    }
}
