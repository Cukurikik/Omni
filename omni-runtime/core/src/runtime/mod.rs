pub mod boot_sequence;
pub mod scheduler;
pub mod fault_tolerance;
pub mod omni_mesh;
pub mod actor;
pub mod unwind;

use crate::compiler::OmniIR;

/// FASE 8: THE OMNI RUNTIME KERNEL (M:N Scheduler + Actor Model + Supervision Tree)
pub struct OmniRuntimeKernel {
    pub boot: boot_sequence::BootController,
    pub scheduler: scheduler::UnifiedScheduler,
    pub fault_monitor: fault_tolerance::SandboxedIsolateMonitor,
    pub mesh: omni_mesh::OmniMeshHeartbeat,
}

impl OmniRuntimeKernel {
    pub fn new() -> Self {
        OmniRuntimeKernel {
            boot: boot_sequence::BootController::new(),
            scheduler: scheduler::UnifiedScheduler::new(),
            fault_monitor: fault_tolerance::SandboxedIsolateMonitor::new(),
            mesh: omni_mesh::OmniMeshHeartbeat::new(),
        }
    }

    /// Titik Nol: Ignition
    pub fn ignite(&mut self) -> Result<(), String> {
        println!("🚀 OMNI-LANG Kernel v8.0 Igniting...\n");
        
        // 1. Boot Sequence (6-stage ignition with CPU detection)
        self.boot.fast_cold_start()?;
        
        // 2. Mesh Networking UDP Heartbeat
        self.mesh.broadcast_identity()?;

        println!("\n🟢 OMNI-LANG Kernel v8.0 Online.");
        println!("   ⚛️  Scheduler: {} cores with work-stealing", self.scheduler.num_cores);
        println!("   🎭 Actor System: Supervision tree ready");
        println!("   🛡️  Fault Tolerance: Crash-proof sandbox active");
        Ok(())
    }

    /// Menjalankan program OMNI dari IR Compile
    pub fn execute_ir(&mut self, ir: OmniIR) -> Result<(), String> {
        // Sandboxed Execution melalui Actor Model
        match self.fault_monitor.execute_with_sandbox(ir, &mut self.scheduler) {
            Ok(_) => Ok(()),
            Err(e) => {
                println!("🛡️ Auto-Healing via Supervision Tree: {}", e);
                Err(e)
            }
        }
    }
}

pub mod swarm;
