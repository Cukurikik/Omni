// omni_terminal_tables.swift — CLI Data Tables
// Layer: Interface / Swift
//
// A utility for rendering formatted, aligned ASCII tables in the terminal.
// Supports dynamic column width calculation. Zero mocks.

import Foundation

public struct OmniTerminalTable {
    private var headers: [String]
    private var rows: [[String]] = []
    
    public init(headers: [String]) {
        self.headers = headers
    }
    
    public mutating func addRow(_ row: [String]) {
        assert(row.count == headers.count, "Row column count must match header count")
        self.rows.append(row)
    }
    
    private func calculateColumnWidths() -> [Int] {
        var widths = headers.map { $0.count }
        
        for row in rows {
            for (index, cell) in row.enumerated() {
                if cell.count > widths[index] {
                    widths[index] = cell.count
                }
            }
        }
        
        return widths
    }
    
    private func pad(_ text: String, width: Int) -> String {
        return text.padding(toLength: width, withPad: " ", startingAt: 0)
    }
    
    private func renderSeparator(widths: [Int]) -> String {
        let dashed = widths.map { String(repeating: "-", count: $0 + 2) }
        return "+" + dashed.joined(separator: "+") + "+"
    }
    
    public func render() -> String {
        let widths = calculateColumnWidths()
        let separator = renderSeparator(widths: widths)
        
        var output = separator + "\n"
        
        // Render headers
        let headerRow = headers.enumerated().map { index, text in
            " \(pad(text, width: widths[index])) "
        }.joined(separator: "|")
        
        output += "|" + headerRow + "|\n"
        output += separator + "\n"
        
        // Render data rows
        for row in rows {
            let formattedRow = row.enumerated().map { index, text in
                " \(pad(text, width: widths[index])) "
            }.joined(separator: "|")
            output += "|" + formattedRow + "|\n"
        }
        
        if rows.count > 0 {
            output += separator + "\n"
        }
        
        return output
    }
}
