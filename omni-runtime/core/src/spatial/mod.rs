#![allow(dead_code)]
// ==========================================
// 🕶️ OMNI-SPATIAL ENGINE
// ==========================================
// The Universal UI Renderer — satu engine rendering
// yang menargetkan SEMUA platform grafis:
//
//   WebGPU → Browser, PWA, Electron
//   Vulkan → Linux, Android, Windows
//   Metal  → macOS, iOS
//   DX12   → Windows (fallback)
//
// ARSITEKTUR:
//   SceneGraph → LayoutEngine → Compositor → GPU Backend
//
// FITUR:
//   1. Retained-mode scene graph (React-like diffing)
//   2. Constraint-based layout (Flexbox + Grid + Absolute)
//   3. GPU-accelerated compositing with damage tracking
//   4. 120 FPS target with adaptive frame budget
//   5. Resolution-independent rendering (DPI-aware)
//
// DNA: Flutter Impeller + Chrome Skia + Qt RHI + Bevy ECS
// ==========================================

pub mod renderer;
pub mod scene_graph;
pub mod compositor;

use renderer::{GPURenderer, RenderBackend};
use scene_graph::SceneGraph;
use compositor::{FrameCompositor, CompositorConfig};

/// 🕶️ THE OMNI-SPATIAL ENGINE
/// Orchestrates scene graph → layout → composite → present
pub struct SpatialEngine {
    pub renderer: GPURenderer,
    pub scene: SceneGraph,
    pub compositor: FrameCompositor,
    pub config: SpatialConfig,
    pub stats: RenderStats,
}

/// Engine configuration
#[derive(Debug, Clone)]
pub struct SpatialConfig {
    pub target_fps: u32,
    pub resolution: Resolution,
    pub dpi_scale: f64,
    pub vsync: bool,
    pub msaa_samples: u32,
    pub hdr_enabled: bool,
    pub backend_preference: Vec<RenderBackend>,
}

impl Default for SpatialConfig {
    fn default() -> Self {
        Self {
            target_fps: 120,
            resolution: Resolution { width: 1920, height: 1080 },
            dpi_scale: 1.0,
            vsync: true,
            msaa_samples: 4,
            hdr_enabled: false,
            backend_preference: vec![
                RenderBackend::WebGPU,
                RenderBackend::Vulkan,
                RenderBackend::Metal,
                RenderBackend::DX12,
            ],
        }
    }
}

/// Screen resolution
#[derive(Debug, Clone, Copy)]
pub struct Resolution {
    pub width: u32,
    pub height: u32,
}

impl Resolution {
    pub fn pixels(&self) -> u64 {
        self.width as u64 * self.height as u64
    }

    pub fn aspect_ratio(&self) -> f64 {
        self.width as f64 / self.height as f64
    }
}

/// Rendering statistics
#[derive(Debug, Clone, Default)]
pub struct RenderStats {
    pub frames_rendered: u64,
    pub total_draw_calls: u64,
    pub total_triangles: u64,
    pub total_vertices: u64,
    pub avg_frame_time_ms: f64,
    pub peak_frame_time_ms: f64,
    pub gpu_memory_used_bytes: u64,
    pub texture_count: u32,
    pub shader_count: u32,
    pub compositor_recomposites: u64,
    pub damage_rects_processed: u64,
    pub frames_dropped: u64,
}

impl SpatialEngine {
    pub fn new(config: SpatialConfig) -> Self {
        println!("[SPATIAL] 🕶️  OMNI-Spatial Engine initialized.");
        println!("[SPATIAL] 🎯 Target: {} FPS @ {}x{} ({}x DPI)",
            config.target_fps, config.resolution.width, config.resolution.height, config.dpi_scale);
        println!("[SPATIAL] 🖥️  Backend preference: {:?}", config.backend_preference);

        let renderer = GPURenderer::new(&config.backend_preference);
        let compositor_config = CompositorConfig {
            frame_budget_ms: 1000.0 / config.target_fps as f64,
            max_damage_rects: 32,
            enable_partial_update: true,
            triple_buffering: true,
        };

        Self {
            renderer,
            scene: SceneGraph::new(),
            compositor: FrameCompositor::new(compositor_config),
            config,
            stats: RenderStats::default(),
        }
    }

    /// Build a scene and render one frame
    pub fn render_frame(&mut self) -> FrameResult {
        // Phase 1: Layout pass
        let layout_time = self.scene.compute_layout(
            self.config.resolution.width as f64,
            self.config.resolution.height as f64,
        );

        // Phase 2: Diff pass (find what changed since last frame)
        let damage = self.compositor.compute_damage(&self.scene);

        // Phase 3: Composite + GPU submit
        let draw_calls = self.compositor.composite(&self.scene, &self.renderer);

        // Phase 4: Present
        let frame_time = layout_time + damage.compute_time_ms + draw_calls.submit_time_ms;
        
        // Update stats
        self.stats.frames_rendered += 1;
        self.stats.total_draw_calls += draw_calls.count as u64;
        self.stats.total_triangles += draw_calls.triangles as u64;
        self.stats.total_vertices += draw_calls.vertices as u64;
        self.stats.damage_rects_processed += damage.rects_count as u64;
        self.stats.compositor_recomposites += 1;
        
        let budget = 1000.0 / self.config.target_fps as f64;
        if frame_time > budget {
            self.stats.frames_dropped += 1;
        }

        // Running average
        self.stats.avg_frame_time_ms = 
            (self.stats.avg_frame_time_ms * (self.stats.frames_rendered - 1) as f64 + frame_time)
            / self.stats.frames_rendered as f64;
        if frame_time > self.stats.peak_frame_time_ms {
            self.stats.peak_frame_time_ms = frame_time;
        }

        FrameResult {
            frame_number: self.stats.frames_rendered,
            frame_time_ms: frame_time,
            draw_calls: draw_calls.count,
            triangles: draw_calls.triangles,
            within_budget: frame_time <= budget,
        }
    }

    /// Print rendering dashboard
    pub fn print_dashboard(&self) {
        let fps = if self.stats.avg_frame_time_ms > 0.0 {
            1000.0 / self.stats.avg_frame_time_ms
        } else { 0.0 };

        println!("\n╔══════════════════════════════════════════════════════╗");
        println!("║  🕶️  OMNI-SPATIAL ENGINE — RENDER DASHBOARD          ║");
        println!("╠══════════════════════════════════════════════════════╣");
        println!("║  Backend:           {:>18}             ║", format!("{:?}", self.renderer.active_backend));
        println!("║  Resolution:        {:>10}             ║", 
            format!("{}x{}", self.config.resolution.width, self.config.resolution.height));
        println!("║  Frames Rendered:   {:>8}                        ║", self.stats.frames_rendered);
        println!("║  Avg Frame Time:    {:>7.2} ms                     ║", self.stats.avg_frame_time_ms);
        println!("║  Effective FPS:     {:>7.1}                        ║", fps);
        println!("║  Draw Calls:        {:>8}                        ║", self.stats.total_draw_calls);
        println!("║  Triangles:         {:>8}                        ║", self.stats.total_triangles);
        println!("║  Damage Rects:      {:>8}                        ║", self.stats.damage_rects_processed);
        println!("║  Frames Dropped:    {:>8}                        ║", self.stats.frames_dropped);
        println!("║  GPU Memory:        {:>6} KB                      ║", self.stats.gpu_memory_used_bytes / 1024);
        println!("║  Scene Nodes:       {:>8}                        ║", self.scene.node_count());
        println!("╚══════════════════════════════════════════════════════╝");
    }
}

/// Result of rendering one frame
#[derive(Debug, Clone)]
pub struct FrameResult {
    pub frame_number: u64,
    pub frame_time_ms: f64,
    pub draw_calls: u32,
    pub triangles: u32,
    pub within_budget: bool,
}
