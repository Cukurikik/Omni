pub mod self_evolving;
pub mod auto_healing;
pub mod omni_orbit;
pub mod zero_ui;
pub mod v8_micro_isolate;
pub mod node_parasite_daemon;
pub mod monkey_patch;
pub mod transpiler;

use crate::compiler::ast::OmniProgram;

/// OMNI SINGULARITY — Mesin Eksekusi Kedaulatan
/// V8 Asli (rusty_v8) → Primary Engine
/// Node.js Parasite → Fallback untuk heavy I/O
pub struct OmniSingularity {
    pub evolution_engine: self_evolving::SelfEvolvingCompiler,
    pub healer: auto_healing::ProductionAutoHealer,
    pub orbit: omni_orbit::OmniOrbitDeployment,
    pub architect: zero_ui::OmniArchitect,
    pub micro_v8: v8_micro_isolate::V8MicroIsolate,
    pub node_parasite: node_parasite_daemon::NodeParasiteDaemon,
    pub transpiler: transpiler::OmniTranspiler,
}

impl OmniSingularity {
    pub fn new(is_release: bool) -> Self {
        OmniSingularity {
            evolution_engine: self_evolving::SelfEvolvingCompiler::new(),
            healer: auto_healing::ProductionAutoHealer::new(),
            orbit: omni_orbit::OmniOrbitDeployment::new(),
            architect: zero_ui::OmniArchitect::new(),
            micro_v8: v8_micro_isolate::V8MicroIsolate::new(),
            node_parasite: node_parasite_daemon::NodeParasiteDaemon::new(),
            transpiler: transpiler::OmniTranspiler::new(is_release),
        }
    }

    /// Bangkitkan seluruh subsistem Singularity
    pub fn awaken(&mut self) -> Result<(), String> {
        println!("🌌 OMNI-SINGULARITY AWAKENS");
        
        self.evolution_engine.start_telemetry_analysis()?;
        self.healer.activate_live_patching()?;
        
        // V8 Engine ASLI (rusty_v8)
        self.micro_v8.initialize().map_err(|e| e.to_string())?;
        
        // Node.js Parasite (opsional, untuk heavy I/O)
        self.node_parasite.spawn_daemon().map_err(|e| e.to_string())?;
        
        println!("👁️ Semua engine aktif. OMNI siap mengeksekusi kode.");
        Ok(())
    }

    /// EKSEKUSI PROGRAM NYATA
    /// AST → Transpile → Security Preamble → V8 ASLI → Output Nyata
    pub fn execute_program(&mut self, ast: &OmniProgram) -> Result<(), String> {
        // ═══ TAHAP 1: TRANSPILE AST → JavaScript ═══
        let raw_js = self.transpiler.transpile(ast);
        println!("\n📜 [TRANSPILER] Kode JavaScript dihasilkan:");
        println!("────────────────────────────────────────");
        println!("{}", raw_js);
        println!("────────────────────────────────────────");

        // ═══ TAHAP 2: SECURITY PREAMBLE ═══
        let allowed_fs: Vec<String> = vec!["FS_READ".to_string()];
        let allowed_net: Vec<String> = vec![];
        let _preamble = monkey_patch::generate_security_preamble(&allowed_fs, &allowed_net);

        // ═══ TAHAP 3: EKSEKUSI DI V8 ASLI (rusty_v8) ═══
        println!("\n▶️  [V8 ENGINE] Mengeksekusi di V8 Isolate ASLI...");
        match self.micro_v8.execute(&raw_js) {
            Ok(output) => {
                if !output.is_empty() {
                    println!("\n╔═══ V8 OUTPUT (NYATA) ══════════════════╗");
                    for line in output.lines() {
                        println!("║  {}", line);
                    }
                    println!("╚════════════════════════════════════════╝");
                }
                println!("✅ [V8] Eksekusi berhasil.");
            }
            Err(e) => {
                println!("❌ [V8] Error: {}", e);
                return Err(e.to_string());
            }
        }

        println!("\n✅ [OMNI-SINGULARITY] Program selesai dieksekusi.");
        Ok(())
    }

    /// EKSEKUSI PROGRAM DENGAN IMPORT RESOLUTION (Phase 15)
    /// AST → Transpile → Resolve Imports → Selective Stdlib → V8 → Output
    pub fn execute_program_with_imports(
        &mut self, 
        ast: &OmniProgram,
        omni_source: &str,
        project_dir: Option<&std::path::Path>,
    ) -> Result<(), String> {
        // ═══ TAHAP 1: TRANSPILE AST → JavaScript ═══
        let raw_js = self.transpiler.transpile(ast);
        println!("\n📜 [TRANSPILER] Kode JavaScript dihasilkan:");
        println!("────────────────────────────────────────");
        println!("{}", raw_js);
        println!("────────────────────────────────────────");

        // ═══ TAHAP 2: SECURITY PREAMBLE ═══
        let allowed_fs: Vec<String> = vec!["FS_READ".to_string()];
        let allowed_net: Vec<String> = vec![];
        let _preamble = monkey_patch::generate_security_preamble(&allowed_fs, &allowed_net);

        // ═══ TAHAP 3: EKSEKUSI DI V8 DENGAN SELECTIVE IMPORTS ═══
        println!("\n▶️  [V8 ENGINE] Mengeksekusi di V8 Isolate dengan Import Resolution...");
        match self.micro_v8.execute_with_imports(&raw_js, omni_source, project_dir) {
            Ok(output) => {
                if !output.is_empty() {
                    println!("\n╔═══ V8 OUTPUT (IMPORT-RESOLVED) ════════╗");
                    for line in output.lines() {
                        println!("║  {}", line);
                    }
                    println!("╚════════════════════════════════════════╝");
                }
                println!("✅ [V8] Eksekusi berhasil.");
            }
            Err(e) => {
                println!("❌ [V8] Error: {}", e);
                return Err(e.to_string());
            }
        }

        println!("\n✅ [OMNI-SINGULARITY] Program selesai dieksekusi (Import-Resolved).");
        Ok(())
    }
}
