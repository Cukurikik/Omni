/// ===========================================================================
/// OMNI UI LAYER — SWIFT COMPONENT GENERATOR ENGINE
/// ===========================================================================
/// Source Paradigm : nicehash/create-component-app / Swift UI generators
/// Domain Layer   : UI (Apple ecosystem, declarative component creation)
/// Language        : Swift
/// Function        : Auto-generates SwiftUI/UIKit component boilerplate
///                   with file scaffolding: View, ViewModel, tests, preview,
///                   and modular package integration for iOS/macOS projects
/// ===========================================================================

import Foundation

// MARK: - Component Types

enum ComponentFramework: String, CaseIterable {
    case swiftUI = "SwiftUI"
    case uiKit = "UIKit"
}

enum ComponentType: String, CaseIterable {
    case view = "View"
    case screen = "Screen"
    case widget = "Widget"
    case cell = "Cell"
    case modal = "Modal"
}

// MARK: - Template Configuration

struct ComponentConfig {
    let name: String
    let type: ComponentType
    let framework: ComponentFramework
    let includeViewModel: Bool
    let includeTests: Bool
    let includePreview: Bool
    let moduleName: String?
    let properties: [(name: String, type: String, defaultValue: String?)]

    init(name: String,
         type: ComponentType = .view,
         framework: ComponentFramework = .swiftUI,
         includeViewModel: Bool = true,
         includeTests: Bool = true,
         includePreview: Bool = true,
         moduleName: String? = nil,
         properties: [(String, String, String?)] = []) {
        self.name = name
        self.type = type
        self.framework = framework
        self.includeViewModel = includeViewModel
        self.includeTests = includeTests
        self.includePreview = includePreview
        self.moduleName = moduleName
        self.properties = properties
    }
}

// MARK: - Generated File

struct GeneratedFile {
    let filename: String
    let content: String
    let subdirectory: String
}

// MARK: - Generator Engine

class ComponentGenerator {
    private let config: ComponentConfig
    private var generatedFiles: [GeneratedFile] = []

    init(config: ComponentConfig) {
        self.config = config
        print("[COMPGEN-OMNI-SWIFT] Generator initialized: \(config.name) (\(config.framework.rawValue) \(config.type.rawValue))")
    }

    /// Generate all component files.
    func generate() -> [GeneratedFile] {
        generatedFiles = []

        // Main view/component file
        switch config.framework {
        case .swiftUI:
            generatedFiles.append(generateSwiftUIView())
        case .uiKit:
            generatedFiles.append(generateUIKitView())
        }

        // ViewModel
        if config.includeViewModel {
            generatedFiles.append(generateViewModel())
        }

        // Preview
        if config.includePreview && config.framework == .swiftUI {
            generatedFiles.append(generatePreview())
        }

        // Tests
        if config.includeTests {
            generatedFiles.append(generateTests())
        }

        print("[COMPGEN-OMNI-SWIFT] Generated \(generatedFiles.count) file(s) for '\(config.name)'")
        for file in generatedFiles {
            print("[COMPGEN-OMNI-SWIFT]   → \(file.subdirectory)/\(file.filename)")
        }

        return generatedFiles
    }

    // MARK: - SwiftUI View Template

    private func generateSwiftUIView() -> GeneratedFile {
        var code = """
        import SwiftUI

        struct \(config.name)\(config.type.rawValue): View {
        """

        // Properties
        for prop in config.properties {
            if let def = prop.defaultValue {
                code += "\n    @State var \(prop.name): \(prop.type) = \(def)"
            } else {
                code += "\n    let \(prop.name): \(prop.type)"
            }
        }

        if config.includeViewModel {
            code += "\n    @StateObject private var viewModel = \(config.name)ViewModel()"
        }

        code += """

            var body: some View {
                VStack(spacing: 16) {
                    Text("\(config.name)")
                        .font(.title)
                        .fontWeight(.bold)
                }
                .padding()
            }
        }
        """

        return GeneratedFile(
            filename: "\(config.name)\(config.type.rawValue).swift",
            content: code,
            subdirectory: "Views"
        )
    }

    // MARK: - UIKit View Template

    private func generateUIKitView() -> GeneratedFile {
        let code = """
        import UIKit

        final class \(config.name)\(config.type.rawValue): UIView {
            // MARK: - Properties
        \(config.properties.map { "    var \($0.name): \($0.type)?" }.joined(separator: "\n"))

            // MARK: - Init
            override init(frame: CGRect) {
                super.init(frame: frame)
                setupUI()
            }

            required init?(coder: NSCoder) {
                fatalError("init(coder:) not implemented")
            }

            // MARK: - Setup
            private func setupUI() {
                backgroundColor = .systemBackground
            }
        }
        """

        return GeneratedFile(
            filename: "\(config.name)\(config.type.rawValue).swift",
            content: code,
            subdirectory: "Views"
        )
    }

    // MARK: - ViewModel Template

    private func generateViewModel() -> GeneratedFile {
        let code = """
        import Foundation
        import Combine

        @MainActor
        final class \(config.name)ViewModel: ObservableObject {
            @Published var isLoading = false
            @Published var error: Error?
        \(config.properties.map { "    @Published var \($0.name): \($0.type)\($0.defaultValue.map { " = \($0)" } ?? "")" }.joined(separator: "\n"))

            private var cancellables = Set<AnyCancellable>()

            init() {
                print("[\(config.name)ViewModel] Initialized")
            }

            func load() async {
                isLoading = true
                defer { isLoading = false }
                // Load data here
            }
        }
        """

        return GeneratedFile(
            filename: "\(config.name)ViewModel.swift",
            content: code,
            subdirectory: "ViewModels"
        )
    }

    // MARK: - Preview Template

    private func generatePreview() -> GeneratedFile {
        let code = """
        import SwiftUI

        struct \(config.name)\(config.type.rawValue)_Previews: PreviewProvider {
            static var previews: some View {
                Group {
                    \(config.name)\(config.type.rawValue)()
                        .previewDisplayName("Default")

                    \(config.name)\(config.type.rawValue)()
                        .preferredColorScheme(.dark)
                        .previewDisplayName("Dark Mode")
                }
            }
        }
        """

        return GeneratedFile(
            filename: "\(config.name)\(config.type.rawValue)_Previews.swift",
            content: code,
            subdirectory: "Previews"
        )
    }

    // MARK: - Test Template

    private func generateTests() -> GeneratedFile {
        let code = """
        import XCTest
        @testable import \(config.moduleName ?? "App")

        final class \(config.name)Tests: XCTestCase {

            func testViewModelInit() async {
                let vm = \(config.name)ViewModel()
                XCTAssertFalse(vm.isLoading)
                XCTAssertNil(vm.error)
            }

            func testViewModelLoad() async {
                let vm = \(config.name)ViewModel()
                await vm.load()
                XCTAssertFalse(vm.isLoading)
            }
        }
        """

        return GeneratedFile(
            filename: "\(config.name)Tests.swift",
            content: code,
            subdirectory: "Tests"
        )
    }
}
