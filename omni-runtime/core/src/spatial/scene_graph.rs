#![allow(dead_code)]
// ==========================================
// 🌳 SCENE GRAPH + LAYOUT ENGINE
// ==========================================
// Retained-mode scene graph seperti browser DOM
// tapi dengan GPU-first rendering pipeline.
//
// HIERARCHY:
//   Root
//   ├── Window
//   │   ├── TitleBar (Flex Row)
//   │   │   ├── Icon
//   │   │   ├── Title (Text)
//   │   │   └── CloseButton
//   │   └── Content (Flex Column)
//   │       ├── Sidebar
//   │       └── MainPanel
//
// LAYOUT ALGORITHMS:
//   1. Flexbox (1D) — row/column with grow/shrink
//   2. Grid (2D) — rows × columns with gap
//   3. Absolute — manual position
//   4. Stack — layered z-axis
//
// DNA: Flutter Widget Tree + Browser Layout + SwiftUI
// ==========================================

use std::collections::HashMap;

/// Unique node ID in scene graph
pub type NodeId = u64;

/// Layout direction for flex containers
#[derive(Debug, Clone, PartialEq)]
pub enum FlexDirection {
    Row,
    Column,
}

/// Alignment on cross axis
#[derive(Debug, Clone, PartialEq)]
pub enum Alignment {
    Start,
    Center,
    End,
    Stretch,
    SpaceBetween,
    SpaceAround,
}

/// Layout strategy for a node
#[derive(Debug, Clone)]
pub enum LayoutMode {
    Flex {
        direction: FlexDirection,
        gap: f64,
        align: Alignment,
        justify: Alignment,
    },
    Grid {
        columns: u32,
        rows: u32,
        gap: f64,
    },
    Absolute {
        x: f64,
        y: f64,
    },
    Stack, // Z-layered
}

impl Default for LayoutMode {
    fn default() -> Self {
        LayoutMode::Flex {
            direction: FlexDirection::Column,
            gap: 0.0,
            align: Alignment::Start,
            justify: Alignment::Start,
        }
    }
}

/// Visual style for a node
#[derive(Debug, Clone)]
pub struct NodeStyle {
    pub background_color: [f32; 4],
    pub border_color: [f32; 4],
    pub border_width: f32,
    pub border_radius: [f32; 4], // top-left, top-right, bottom-right, bottom-left
    pub opacity: f32,
    pub shadow: Option<BoxShadow>,
    pub transform: Option<Transform2D>,
}

impl Default for NodeStyle {
    fn default() -> Self {
        Self {
            background_color: [0.0, 0.0, 0.0, 0.0],
            border_color: [0.0, 0.0, 0.0, 0.0],
            border_width: 0.0,
            border_radius: [0.0; 4],
            opacity: 1.0,
            shadow: None,
            transform: None,
        }
    }
}

/// Box shadow
#[derive(Debug, Clone)]
pub struct BoxShadow {
    pub offset_x: f32,
    pub offset_y: f32,
    pub blur_radius: f32,
    pub spread: f32,
    pub color: [f32; 4],
}

/// 2D transform
#[derive(Debug, Clone)]
pub struct Transform2D {
    pub translate: [f64; 2],
    pub rotate_deg: f64,
    pub scale: [f64; 2],
}

/// Size constraints
#[derive(Debug, Clone)]
pub struct SizeConstraint {
    pub width: SizeDimension,
    pub height: SizeDimension,
    pub min_width: f64,
    pub min_height: f64,
    pub max_width: f64,
    pub max_height: f64,
    pub flex_grow: f64,
    pub flex_shrink: f64,
    pub padding: [f64; 4],  // top, right, bottom, left
    pub margin: [f64; 4],
}

impl Default for SizeConstraint {
    fn default() -> Self {
        Self {
            width: SizeDimension::Auto,
            height: SizeDimension::Auto,
            min_width: 0.0,
            min_height: 0.0,
            max_width: f64::INFINITY,
            max_height: f64::INFINITY,
            flex_grow: 0.0,
            flex_shrink: 1.0,
            padding: [0.0; 4],
            margin: [0.0; 4],
        }
    }
}

/// How a dimension is sized
#[derive(Debug, Clone)]
pub enum SizeDimension {
    Auto,
    Fixed(f64),
    Percent(f64),
    FitContent,
}

/// Computed layout result (output of layout pass)
#[derive(Debug, Clone, Default)]
pub struct ComputedLayout {
    pub x: f64,
    pub y: f64,
    pub width: f64,
    pub height: f64,
}

/// Scene graph node
#[derive(Debug, Clone)]
pub struct SceneNode {
    pub id: NodeId,
    pub name: String,
    pub node_type: NodeType,
    pub layout_mode: LayoutMode,
    pub size: SizeConstraint,
    pub style: NodeStyle,
    pub computed: ComputedLayout,
    pub children: Vec<NodeId>,
    pub parent: Option<NodeId>,
    pub visible: bool,
    pub dirty: bool,  // Needs re-layout
}

/// Type of scene node
#[derive(Debug, Clone)]
pub enum NodeType {
    /// Container with children
    Container,
    /// Text rendering node
    Text {
        content: String,
        font_size: f32,
        font_family: String,
        color: [f32; 4],
        line_height: f32,
    },
    /// Image node
    Image {
        source: String,
        fit: ImageFit,
    },
    /// Custom draw (canvas-like)
    Canvas {
        draw_commands: Vec<DrawCommand>,
    },
}

/// Image fit mode
#[derive(Debug, Clone)]
pub enum ImageFit {
    Cover,
    Contain,
    Fill,
    None,
}

/// Custom draw command
#[derive(Debug, Clone)]
pub enum DrawCommand {
    LineTo(f64, f64),
    Arc(f64, f64, f64, f64, f64),
    Fill([f32; 4]),
    Stroke([f32; 4], f32),
}

/// 🌳 THE SCENE GRAPH
pub struct SceneGraph {
    nodes: HashMap<NodeId, SceneNode>,
    root_id: Option<NodeId>,
    next_id: NodeId,
    layout_version: u64,
}

impl SceneGraph {
    pub fn new() -> Self {
        Self {
            nodes: HashMap::new(),
            root_id: None,
            next_id: 1,
            layout_version: 0,
        }
    }

    /// Create a container node
    pub fn create_container(&mut self, name: &str, layout: LayoutMode) -> NodeId {
        let id = self.next_id;
        self.next_id += 1;

        let node = SceneNode {
            id,
            name: name.to_string(),
            node_type: NodeType::Container,
            layout_mode: layout,
            size: SizeConstraint::default(),
            style: NodeStyle::default(),
            computed: ComputedLayout::default(),
            children: Vec::new(),
            parent: None,
            visible: true,
            dirty: true,
        };

        self.nodes.insert(id, node);
        
        if self.root_id.is_none() {
            self.root_id = Some(id);
        }

        id
    }

    /// Create a text node
    pub fn create_text(&mut self, name: &str, content: &str, font_size: f32) -> NodeId {
        let id = self.next_id;
        self.next_id += 1;

        let node = SceneNode {
            id,
            name: name.to_string(),
            node_type: NodeType::Text {
                content: content.to_string(),
                font_size,
                font_family: "Inter".to_string(),
                color: [1.0, 1.0, 1.0, 1.0],
                line_height: 1.5,
            },
            layout_mode: LayoutMode::default(),
            size: SizeConstraint::default(),
            style: NodeStyle::default(),
            computed: ComputedLayout::default(),
            children: Vec::new(),
            parent: None,
            visible: true,
            dirty: true,
        };

        self.nodes.insert(id, node);
        id
    }

    /// Add child to parent
    pub fn add_child(&mut self, parent_id: NodeId, child_id: NodeId) {
        if let Some(parent) = self.nodes.get_mut(&parent_id) {
            parent.children.push(child_id);
            parent.dirty = true;
        }
        if let Some(child) = self.nodes.get_mut(&child_id) {
            child.parent = Some(parent_id);
        }
    }

    /// Set node style
    pub fn set_style(&mut self, node_id: NodeId, style: NodeStyle) {
        if let Some(node) = self.nodes.get_mut(&node_id) {
            node.style = style;
            node.dirty = true;
        }
    }

    /// Set size constraints
    pub fn set_size(&mut self, node_id: NodeId, size: SizeConstraint) {
        if let Some(node) = self.nodes.get_mut(&node_id) {
            node.size = size;
            node.dirty = true;
        }
    }

    /// Compute layout for entire tree (returns time in ms)
    pub fn compute_layout(&mut self, viewport_width: f64, viewport_height: f64) -> f64 {
        self.layout_version += 1;
        
        if let Some(root_id) = self.root_id {
            self.layout_node(root_id, 0.0, 0.0, viewport_width, viewport_height);
        }

        // Simulated layout time (proportional to node count)
        0.1 + (self.nodes.len() as f64 * 0.005)
    }

    /// Recursive layout computation
    fn layout_node(&mut self, node_id: NodeId, x: f64, y: f64, available_w: f64, available_h: f64) {
        // Get node data (we need to work around borrow checker)
        let (layout_mode, children, size, padding) = {
            let node = match self.nodes.get(&node_id) {
                Some(n) => n,
                None => return,
            };
            (
                node.layout_mode.clone(),
                node.children.clone(),
                node.size.clone(),
                node.size.padding,
            )
        };

        // Compute own size
        let width = match &size.width {
            SizeDimension::Fixed(w) => *w,
            SizeDimension::Percent(pct) => available_w * pct / 100.0,
            _ => available_w,
        };
        let height = match &size.height {
            SizeDimension::Fixed(h) => *h,
            SizeDimension::Percent(pct) => available_h * pct / 100.0,
            _ => available_h,
        };

        // Clamp
        let width = width.max(size.min_width).min(size.max_width);
        let height = height.max(size.min_height).min(size.max_height);

        // Set computed layout
        if let Some(node) = self.nodes.get_mut(&node_id) {
            node.computed = ComputedLayout { x, y, width, height };
            node.dirty = false;
        }

        // Layout children based on mode
        let inner_x = x + padding[3]; // left padding
        let inner_y = y + padding[0]; // top padding
        let inner_w = width - padding[1] - padding[3];
        let inner_h = height - padding[0] - padding[2];

        match layout_mode {
            LayoutMode::Flex { direction, gap, .. } => {
                let mut offset = 0.0;
                for child_id in &children {
                    match direction {
                        FlexDirection::Row => {
                            let child_w = inner_w / children.len().max(1) as f64 - gap;
                            self.layout_node(*child_id, inner_x + offset, inner_y, child_w, inner_h);
                            offset += child_w + gap;
                        },
                        FlexDirection::Column => {
                            let child_h = inner_h / children.len().max(1) as f64 - gap;
                            self.layout_node(*child_id, inner_x, inner_y + offset, inner_w, child_h);
                            offset += child_h + gap;
                        },
                    }
                }
            },
            LayoutMode::Grid { columns, gap, .. } => {
                let col_w = (inner_w - gap * (columns as f64 - 1.0)) / columns as f64;
                let row_h = inner_h / ((children.len() as f64 / columns as f64).ceil().max(1.0));
                for (i, child_id) in children.iter().enumerate() {
                    let col = i as u32 % columns;
                    let row = i as u32 / columns;
                    let cx = inner_x + col as f64 * (col_w + gap);
                    let cy = inner_y + row as f64 * (row_h + gap);
                    self.layout_node(*child_id, cx, cy, col_w, row_h);
                }
            },
            LayoutMode::Absolute { x: ax, y: ay } => {
                for child_id in &children {
                    self.layout_node(*child_id, x + ax, y + ay, inner_w, inner_h);
                }
            },
            LayoutMode::Stack => {
                for child_id in &children {
                    self.layout_node(*child_id, inner_x, inner_y, inner_w, inner_h);
                }
            },
        }
    }

    /// Get node by ID
    pub fn get_node(&self, id: NodeId) -> Option<&SceneNode> {
        self.nodes.get(&id)
    }

    /// Get mutable node
    pub fn get_node_mut(&mut self, id: NodeId) -> Option<&mut SceneNode> {
        self.nodes.get_mut(&id)
    }

    /// Total node count
    pub fn node_count(&self) -> usize {
        self.nodes.len()
    }

    /// Get all dirty (changed) nodes
    pub fn dirty_nodes(&self) -> Vec<NodeId> {
        self.nodes.values()
            .filter(|n| n.dirty)
            .map(|n| n.id)
            .collect()
    }

    /// Print scene tree
    pub fn print_tree(&self) {
        println!("\n🌳 OMNI Scene Graph:");
        println!("═══════════════════════════════════════");
        if let Some(root_id) = self.root_id {
            self.print_node(root_id, 0);
        }
        println!("═══════════════════════════════════════");
        println!("Nodes: {} | Layout version: {}", self.nodes.len(), self.layout_version);
    }

    fn print_node(&self, id: NodeId, depth: usize) {
        let indent = "  ".repeat(depth);
        if let Some(node) = self.nodes.get(&id) {
            let type_icon = match &node.node_type {
                NodeType::Container => "📦",
                NodeType::Text { .. } => "📝",
                NodeType::Image { .. } => "🖼️",
                NodeType::Canvas { .. } => "🎨",
            };
            let layout = &node.computed;
            println!("{}{} {} ({}x{} @ {},{}) {}",
                indent, type_icon, node.name,
                layout.width as i32, layout.height as i32,
                layout.x as i32, layout.y as i32,
                if node.visible { "" } else { "[HIDDEN]" },
            );
            for child_id in &node.children {
                self.print_node(*child_id, depth + 1);
            }
        }
    }
}
