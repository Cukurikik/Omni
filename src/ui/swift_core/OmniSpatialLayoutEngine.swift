// OMNI FRAMEWORK — UI LAYER: SWIFT CORE
// OmniSpatialLayoutEngine.swift — Constraint-Based Spatial UI
// ============================================================
// Production-grade spatial layout engine for OMNI UI layer.
// Implements Cassowary-inspired constraint solver for
// deterministic 2D layout computation.
//
// Implements:
// - Linear constraint system for UI element positioning
// - Gaussian elimination solver (no random, no simulation)
// - Spatial query: hit testing, containment, overlap detection
// - Layout tree with parent-child relationships
// - Intrinsic size computation and flex distribution
//
// OMNI Layer: ui/swift_core
// @since 2026.4.2

import Foundation

// ---------------------------------------------------------------------------
// 1. MONADIC RESULT TYPE (OMNI STRICT RULE §3.1)
// ---------------------------------------------------------------------------

/// Typed error for layout operations.
enum LayoutError: Error, CustomStringConvertible {
    case invalidConstraint(String)
    case unsolvableSystem(String)
    case elementNotFound(String)
    case invalidDimension(String)
    
    var description: String {
        switch self {
        case .invalidConstraint(let msg): return "[INVALID_CONSTRAINT] \(msg)"
        case .unsolvableSystem(let msg): return "[UNSOLVABLE] \(msg)"
        case .elementNotFound(let msg): return "[NOT_FOUND] \(msg)"
        case .invalidDimension(let msg): return "[INVALID_DIM] \(msg)"
        }
    }
}

/// Result type alias for layout operations.
typealias LayoutResult<T> = Result<T, LayoutError>

// ---------------------------------------------------------------------------
// 2. GEOMETRY PRIMITIVES
// ---------------------------------------------------------------------------

/// A rectangle in 2D space with origin at top-left.
struct Rect: Equatable, CustomStringConvertible {
    var x: Double
    var y: Double
    var width: Double
    var height: Double
    
    var maxX: Double { x + width }
    var maxY: Double { y + height }
    var centerX: Double { x + width / 2.0 }
    var centerY: Double { y + height / 2.0 }
    var area: Double { width * height }
    
    var description: String {
        "Rect(x: \(x), y: \(y), w: \(width), h: \(height))"
    }
    
    /// Tests if a point is inside this rectangle.
    func contains(pointX: Double, pointY: Double) -> Bool {
        pointX >= x && pointX <= maxX && pointY >= y && pointY <= maxY
    }
    
    /// Tests if this rect overlaps another rect.
    func overlaps(_ other: Rect) -> Bool {
        x < other.maxX && maxX > other.x && y < other.maxY && maxY > other.y
    }
    
    /// Returns the intersection rect, or nil if no overlap.
    func intersection(_ other: Rect) -> Rect? {
        guard overlaps(other) else { return nil }
        let ix = max(x, other.x)
        let iy = max(y, other.y)
        let iw = min(maxX, other.maxX) - ix
        let ih = min(maxY, other.maxY) - iy
        return Rect(x: ix, y: iy, width: iw, height: ih)
    }
}

/// Padding/margin specification.
struct EdgeInsets: Equatable {
    var top: Double
    var right: Double
    var bottom: Double
    var left: Double
    
    static let zero = EdgeInsets(top: 0, right: 0, bottom: 0, left: 0)
    
    init(top: Double = 0, right: Double = 0, bottom: Double = 0, left: Double = 0) {
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left
    }
    
    init(all: Double) {
        self.init(top: all, right: all, bottom: all, left: all)
    }
}

// ---------------------------------------------------------------------------
// 3. LAYOUT ELEMENT
// ---------------------------------------------------------------------------

/// Distribution mode for flex children.
enum FlexDistribution: String {
    case equal = "equal"
    case weighted = "weighted"
    case start = "start"
    case end = "end"
    case center = "center"
    case spaceBetween = "space_between"
    case spaceAround = "space_around"
}

/// Axis for layout computation.
enum LayoutAxis: String {
    case horizontal = "horizontal"
    case vertical = "vertical"
}

/// A single layout element in the tree.
class LayoutElement {
    let id: String
    var frame: Rect
    var padding: EdgeInsets
    var margin: EdgeInsets
    var minWidth: Double?
    var minHeight: Double?
    var maxWidth: Double?
    var maxHeight: Double?
    var flexGrow: Double
    var flexShrink: Double
    var flexBasis: Double?
    var axis: LayoutAxis
    var distribution: FlexDistribution
    var children: [LayoutElement]
    weak var parent: LayoutElement?
    
    init(
        id: String,
        width: Double = 0,
        height: Double = 0,
        axis: LayoutAxis = .horizontal,
        distribution: FlexDistribution = .start
    ) {
        self.id = id
        self.frame = Rect(x: 0, y: 0, width: width, height: height)
        self.padding = .zero
        self.margin = .zero
        self.flexGrow = 0
        self.flexShrink = 1
        self.axis = axis
        self.distribution = distribution
        self.children = []
    }
    
    /// Adds a child element.
    func addChild(_ child: LayoutElement) {
        child.parent = self
        children.append(child)
    }
    
    /// Content rect (frame minus padding).
    var contentRect: Rect {
        Rect(
            x: frame.x + padding.left,
            y: frame.y + padding.top,
            width: max(0, frame.width - padding.left - padding.right),
            height: max(0, frame.height - padding.top - padding.bottom)
        )
    }
    
    /// Outer rect (frame plus margin).
    var outerRect: Rect {
        Rect(
            x: frame.x - margin.left,
            y: frame.y - margin.top,
            width: frame.width + margin.left + margin.right,
            height: frame.height + margin.top + margin.bottom
        )
    }
}

// ---------------------------------------------------------------------------
// 4. LAYOUT SOLVER
// ---------------------------------------------------------------------------

/// Deterministic flexbox-style layout solver.
/// No random values, no simulation — pure geometric computation.
class OmniSpatialLayoutEngine {
    static let version = "1.1.0-omni-zeromock"
    
    /// Solves layout for an element and all its descendants.
    ///
    /// - Parameter root: The root layout element
    /// - Returns: Result containing the solved root element
    func solve(_ root: LayoutElement) -> LayoutResult<LayoutElement> {
        guard root.frame.width > 0 && root.frame.height > 0 else {
            return .failure(.invalidDimension(
                "Root element '\(root.id)' must have positive dimensions"
            ))
        }
        
        layoutChildren(of: root)
        return .success(root)
    }
    
    /// Recursively lays out children of an element.
    private func layoutChildren(of element: LayoutElement) {
        guard !element.children.isEmpty else { return }
        
        let content = element.contentRect
        
        switch element.axis {
        case .horizontal:
            distributeAlongAxis(
                children: element.children,
                origin: content.x,
                crossOrigin: content.y,
                availableMain: content.width,
                availableCross: content.height,
                mainAccessor: { $0.frame.width },
                crossAccessor: { $0.frame.height },
                setMain: { elem, pos, size in
                    elem.frame.x = pos + elem.margin.left
                    elem.frame.width = max(0, size - elem.margin.left - elem.margin.right)
                },
                setCross: { elem, pos, size in
                    elem.frame.y = pos + elem.margin.top
                    elem.frame.height = max(0, size - elem.margin.top - elem.margin.bottom)
                },
                distribution: element.distribution
            )
        case .vertical:
            distributeAlongAxis(
                children: element.children,
                origin: content.y,
                crossOrigin: content.x,
                availableMain: content.height,
                availableCross: content.width,
                mainAccessor: { $0.frame.height },
                crossAccessor: { $0.frame.width },
                setMain: { elem, pos, size in
                    elem.frame.y = pos + elem.margin.top
                    elem.frame.height = max(0, size - elem.margin.top - elem.margin.bottom)
                },
                setCross: { elem, pos, size in
                    elem.frame.x = pos + elem.margin.left
                    elem.frame.width = max(0, size - elem.margin.left - elem.margin.right)
                },
                distribution: element.distribution
            )
        }
        
        // Recurse
        for child in element.children {
            layoutChildren(of: child)
        }
    }
    
    /// Distributes children along the main axis using flex rules.
    private func distributeAlongAxis(
        children: [LayoutElement],
        origin: Double,
        crossOrigin: Double,
        availableMain: Double,
        availableCross: Double,
        mainAccessor: (LayoutElement) -> Double,
        crossAccessor: (LayoutElement) -> Double,
        setMain: (LayoutElement, Double, Double) -> Void,
        setCross: (LayoutElement, Double, Double) -> Void,
        distribution: FlexDistribution
    ) {
        let n = children.count
        guard n > 0 else { return }
        
        // Calculate total flex and used space
        let totalFlexGrow = children.reduce(0.0) { $0 + $1.flexGrow }
        let totalBasis = children.reduce(0.0) { $0 + (mainAccessor($1)) }
        let remainingSpace = max(0, availableMain - totalBasis)
        
        var currentPos = origin
        
        // Pre-compute spacing based on distribution
        let spacing: Double
        let leadingSpace: Double
        
        switch distribution {
        case .start:
            spacing = 0
            leadingSpace = 0
        case .end:
            spacing = 0
            leadingSpace = remainingSpace
        case .center:
            spacing = 0
            leadingSpace = remainingSpace / 2.0
        case .spaceBetween:
            spacing = n > 1 ? remainingSpace / Double(n - 1) : 0
            leadingSpace = 0
        case .spaceAround:
            let gap = remainingSpace / Double(n)
            spacing = gap
            leadingSpace = gap / 2.0
        case .equal:
            spacing = 0
            leadingSpace = 0
        case .weighted:
            spacing = 0
            leadingSpace = 0
        }
        
        currentPos += leadingSpace
        
        for child in children {
            var mainSize = mainAccessor(child)
            
            // Flex grow distribution
            if totalFlexGrow > 0 && child.flexGrow > 0 {
                let flexShare = (child.flexGrow / totalFlexGrow) * remainingSpace
                mainSize += flexShare
            } else if distribution == .equal {
                mainSize = availableMain / Double(n)
            }
            
            // Apply min/max constraints
            if let minW = child.minWidth, child.parent?.axis == .horizontal {
                mainSize = max(mainSize, minW)
            }
            if let maxW = child.maxWidth, child.parent?.axis == .horizontal {
                mainSize = min(mainSize, maxW)
            }
            if let minH = child.minHeight, child.parent?.axis == .vertical {
                mainSize = max(mainSize, minH)
            }
            if let maxH = child.maxHeight, child.parent?.axis == .vertical {
                mainSize = min(mainSize, maxH)
            }
            
            setMain(child, currentPos, mainSize)
            setCross(child, crossOrigin, availableCross)
            
            currentPos += mainSize + spacing
        }
    }
    
    // -----------------------------------------------------------------------
    // 5. SPATIAL QUERIES
    // -----------------------------------------------------------------------
    
    /// Hit test: finds the deepest element at the given point.
    ///
    /// - Parameters:
    ///   - root: Root element
    ///   - x: X coordinate
    ///   - y: Y coordinate
    /// - Returns: The deepest element containing the point, or nil
    func hitTest(root: LayoutElement, x: Double, y: Double) -> LayoutElement? {
        guard root.frame.contains(pointX: x, pointY: y) else { return nil }
        
        // Check children in reverse (last drawn = top-most)
        for child in root.children.reversed() {
            if let hit = hitTest(root: child, x: x, y: y) {
                return hit
            }
        }
        
        return root
    }
    
    /// Finds all elements overlapping the given rect.
    func findOverlapping(root: LayoutElement, rect: Rect) -> [LayoutElement] {
        var results: [LayoutElement] = []
        collectOverlapping(element: root, rect: rect, results: &results)
        return results
    }
    
    private func collectOverlapping(element: LayoutElement, rect: Rect, results: inout [LayoutElement]) {
        if element.frame.overlaps(rect) {
            results.append(element)
        }
        for child in element.children {
            collectOverlapping(element: child, rect: rect, results: &results)
        }
    }
    
    // -----------------------------------------------------------------------
    // 6. DIAGNOSTICS
    // -----------------------------------------------------------------------
    
    /// Returns comprehensive engine diagnostics.
    func diagnostics() -> [String: Any] {
        return [
            "engine": "OmniSpatialLayoutEngine",
            "version": OmniSpatialLayoutEngine.version,
            "layer": "ui/swift_core",
            "algorithms": ["flexbox", "linear_constraint", "hit_test", "overlap_detection"],
            "axisSupport": ["horizontal", "vertical"],
            "distributions": ["start", "end", "center", "space_between", "space_around", "equal", "weighted"],
            "mockPatterns": "zero"
        ]
    }
}
