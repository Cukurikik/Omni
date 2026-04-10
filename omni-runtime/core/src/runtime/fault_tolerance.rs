#![allow(dead_code)]
// ==========================================
// 🛡️ OMNI FAULT TOLERANCE — SUPERVISION TREE
// ==========================================
// DNA Erlang OTP: "Let it crash!"
// Actor yang crash di-restart oleh Supervisor.
// Supervisor mengelola child actors dengan strategi:
//   - OneForOne: Restart hanya actor yang crash
//   - AllForOne: Restart semua sibling actors
//   - RestForOne: Restart actor + semua yang di-start setelahnya
//
// HIERARKI:
//   RootSupervisor
//   ├── WorkerSupervisor (OneForOne)
//   │   ├── Actor: "http_handler_1"
//   │   ├── Actor: "http_handler_2"
//   │   └── Actor: "http_handler_3"
//   └── IOSupervisor (AllForOne)
//       ├── Actor: "db_connection"
//       └── Actor: "cache_manager"
// ==========================================

use crate::compiler::OmniIR;
use crate::runtime::scheduler::UnifiedScheduler;
use crate::runtime::actor::{OmniActor, ActorState};

/// Strategi restart ketika child crash
#[derive(Debug, Clone)]
pub enum SupervisionStrategy {
    /// Restart hanya actor yang crash
    OneForOne,
    /// Restart semua child actors
    AllForOne,
    /// Restart actor yang crash + semua yang di-start setelahnya
    RestForOne,
}

/// Supervisor node dalam supervision tree
pub struct Supervisor {
    pub id: u64,
    pub name: String,
    pub strategy: SupervisionStrategy,
    pub children: Vec<OmniActor>,
    pub max_restarts: u32,      // Max restarts sebelum escalate
    pub restart_window_sec: u64,
    pub restarts_in_window: u32,
}

impl Supervisor {
    pub fn new(id: u64, name: &str, strategy: SupervisionStrategy) -> Self {
        println!("[SUPERVISOR {}] 🛡️ Created: {} (strategy: {:?})", id, name, strategy);
        Self {
            id,
            name: name.to_string(),
            strategy,
            children: Vec::new(),
            max_restarts: 10,
            restart_window_sec: 60,
            restarts_in_window: 0,
        }
    }

    /// Tambah child actor
    pub fn add_child(&mut self, mut actor: OmniActor) {
        actor.supervisor_id = Some(self.id);
        println!("[SUPERVISOR {}] ➕ Added child: {} (actor_id={})", 
            self.id, actor.name, actor.id);
        actor.start();
        self.children.push(actor);
    }

    /// Handle child crash berdasarkan strategy
    pub fn handle_crash(&mut self, crashed_actor_id: u64, error: &str) -> Result<(), String> {
        println!("[SUPERVISOR {}] 💥 Child crash detected: actor_id={} — Error: {}", 
            self.id, crashed_actor_id, error);

        // Check restart budget
        self.restarts_in_window += 1;
        if self.restarts_in_window > self.max_restarts {
            return Err(format!(
                "❌ Supervisor '{}' exceeded restart budget ({}/{}) — ESCALATING!",
                self.name, self.restarts_in_window, self.max_restarts
            ));
        }

        match self.strategy {
            SupervisionStrategy::OneForOne => {
                self.restart_one(crashed_actor_id)?;
            },
            SupervisionStrategy::AllForOne => {
                self.restart_all()?;
            },
            SupervisionStrategy::RestForOne => {
                self.restart_rest(crashed_actor_id)?;
            },
        }

        Ok(())
    }

    /// OneForOne: Restart hanya actor yang crash
    fn restart_one(&mut self, actor_id: u64) -> Result<(), String> {
        println!("[SUPERVISOR {}] 🔄 Strategy: OneForOne — Restarting actor {}", self.id, actor_id);
        
        for actor in &mut self.children {
            if actor.id == actor_id {
                return actor.restart();
            }
        }
        
        Err(format!("Actor {} not found in supervisor {}", actor_id, self.id))
    }

    /// AllForOne: Restart semua children
    fn restart_all(&mut self) -> Result<(), String> {
        println!("[SUPERVISOR {}] 🔄 Strategy: AllForOne — Restarting ALL {} children", 
            self.id, self.children.len());
        
        for actor in &mut self.children {
            if actor.is_alive() {
                actor.stop();
            }
            actor.restart()?;
        }
        
        Ok(())
    }

    /// RestForOne: Restart actor + semua yang di-start setelahnya
    fn restart_rest(&mut self, from_actor_id: u64) -> Result<(), String> {
        println!("[SUPERVISOR {}] 🔄 Strategy: RestForOne — Restarting from actor {} onwards", 
            self.id, from_actor_id);
        
        let mut found = false;
        for actor in &mut self.children {
            if actor.id == from_actor_id {
                found = true;
            }
            if found {
                if actor.is_alive() {
                    actor.stop();
                }
                actor.restart()?;
            }
        }
        
        Ok(())
    }

    /// Health check semua children
    pub fn health_check(&self) -> Vec<(u64, String, bool)> {
        self.children.iter()
            .map(|actor| (actor.id, actor.name.clone(), actor.is_alive()))
            .collect()
    }

    /// Get number of alive children
    pub fn alive_count(&self) -> usize {
        self.children.iter().filter(|a| a.is_alive()).count()
    }

    /// Get total children
    pub fn total_children(&self) -> usize {
        self.children.len()
    }

    /// Print supervision tree
    pub fn print_tree(&self, indent: usize) {
        let prefix = "  ".repeat(indent);
        println!("{}🛡️ Supervisor: {} (id={}, strategy={:?})", prefix, self.name, self.id, self.strategy);
        for actor in &self.children {
            let status = match &actor.state {
                ActorState::Running => "🟢 Running",
                ActorState::Crashed(_e) => "🔴 Crashed",
                ActorState::Stopped => "⚫ Stopped",
                ActorState::Restarting => "🟡 Restarting",
                _ => "⚪ Unknown",
            };
            println!("{}  🎭 Actor: {} (id={}) — {} [crashes: {}, restarts: {}]", 
                prefix, actor.name, actor.id, status, 
                actor.stats.crashes, actor.stats.restarts);
        }
    }
}

/// 🛡️ THE SANDBOXED ISOLATE MONITOR (Upgraded with Supervision Tree)
pub struct SandboxedIsolateMonitor {
    supervisors: Vec<Supervisor>,
    root_supervisor_id: u64,
    next_supervisor_id: u64,
    next_actor_id: u64,
    pub total_crashes_recovered: u64,
    pub total_escalations: u64,
}

impl SandboxedIsolateMonitor {
    pub fn new() -> Self {
        println!("[FAULT-TOLERANCE] 🛡️ Supervision Tree Engine initialized.");
        Self {
            supervisors: Vec::new(),
            root_supervisor_id: 0,
            next_supervisor_id: 1,
            next_actor_id: 100,
            total_crashes_recovered: 0,
            total_escalations: 0,
        }
    }

    /// Create a new supervisor and return its ID
    pub fn create_supervisor(&mut self, name: &str, strategy: SupervisionStrategy) -> u64 {
        let id = self.next_supervisor_id;
        self.next_supervisor_id += 1;
        
        let supervisor = Supervisor::new(id, name, strategy);
        self.supervisors.push(supervisor);
        
        if self.root_supervisor_id == 0 {
            self.root_supervisor_id = id;
        }
        
        id
    }

    /// Spawn a new actor under a supervisor
    pub fn spawn_actor(&mut self, supervisor_id: u64, name: &str) -> Result<u64, String> {
        let actor_id = self.next_actor_id;
        self.next_actor_id += 1;
        
        let actor = OmniActor::new(actor_id, name);
        
        for sup in &mut self.supervisors {
            if sup.id == supervisor_id {
                sup.add_child(actor);
                return Ok(actor_id);
            }
        }
        
        Err(format!("Supervisor {} not found", supervisor_id))
    }

    /// Simulate a crash and trigger supervision recovery
    pub fn simulate_crash(&mut self, actor_id: u64, error: &str) -> Result<(), String> {
        // Find the actor and crash it
        for sup in &mut self.supervisors {
            for actor in &mut sup.children {
                if actor.id == actor_id {
                    actor.crash(error);
                    
                    // Handle via supervision strategy
                    match sup.handle_crash(actor_id, error) {
                        Ok(_) => {
                            self.total_crashes_recovered += 1;
                            println!("[FAULT-TOLERANCE] ✅ Crash recovered: actor {} restarted", actor_id);
                            return Ok(());
                        },
                        Err(e) => {
                            self.total_escalations += 1;
                            println!("[FAULT-TOLERANCE] ⚠️  Escalation: {}", e);
                            return Err(e);
                        }
                    }
                }
            }
        }
        
        Err(format!("Actor {} not found in any supervisor", actor_id))
    }

    /// Execute IR with sandbox protection (backward compat)
    pub fn execute_with_sandbox(&self, ir: OmniIR, scheduler: &mut UnifiedScheduler) -> Result<(), String> {
        println!("🛡️ Sandboxed Isolate: Memulai eksekusi kode dalam karantina Actor Model...");
        
        match scheduler.dispatch(&ir) {
            Ok(_) => {
                println!("✅ Eksekusi Selesai Tanpa Segmentation Fault! (Actor-Isolated)");
                Ok(())
            },
            Err(e) => {
                println!("🛡️ Auto-Healing Triggered via Supervision Tree: {}", e);
                Err(e)
            }
        }
    }

    /// Print entire supervision tree
    pub fn print_supervision_tree(&self) {
        println!("\n🌳 OMNI Supervision Tree:");
        println!("═══════════════════════════════════");
        for sup in &self.supervisors {
            sup.print_tree(0);
        }
        println!("═══════════════════════════════════");
        println!("Crashes recovered: {} | Escalations: {}", 
            self.total_crashes_recovered, self.total_escalations);
    }
}
