#![allow(dead_code)]
// ==========================================
// 🎭 OMNI ACTOR MODEL (DNA Erlang/Elixir/Akka)
// ==========================================
// Setiap spawn berjalan sebagai Actor terisolasi.
// Actor berkomunikasi hanya melalui Message Passing.
// Jika satu Actor crash, ia di-restart oleh Supervisor.
// Sistem tetap berjalan — IMMORTAL.
//
// LIFECYCLE:
//   Created → Starting → Running → (Crash → Restarting → Running)
//                                    ↓
//                                  Stopped
// ==========================================

use std::collections::VecDeque;

/// State dalam lifecycle Actor
#[derive(Debug, Clone, PartialEq)]
pub enum ActorState {
    Created,
    Starting,
    Running,
    Suspended,
    Crashed(String),  // Error message
    Restarting,
    Stopped,
}

/// Pesan yang dikirim antar Actor
#[derive(Debug, Clone)]
pub struct ActorMessage {
    pub id: u64,
    pub from: u64,        // Sender actor ID (0 = system)
    pub to: u64,          // Recipient actor ID
    pub payload: MessagePayload,
    pub timestamp: u64,
}

/// Tipe payload yang bisa dikirim
#[derive(Debug, Clone)]
pub enum MessagePayload {
    /// Data string biasa
    Text(String),
    /// Data binary (bytes)
    Binary(Vec<u8>),
    /// Perintah system (start, stop, kill)
    SystemCommand(SystemCommand),
    /// Sinyal dari supervisor
    SupervisorSignal(SupervisorSignal),
    /// Custom numbered payload
    Numeric(f64),
}

#[derive(Debug, Clone)]
pub enum SystemCommand {
    Start,
    Stop,
    Kill,
    Restart,
    HealthCheck,
}

#[derive(Debug, Clone)]
pub enum SupervisorSignal {
    ChildCrashed { child_id: u64, error: String },
    ChildRestarted { child_id: u64 },
    Escalate { error: String },
}

/// Statistik per Actor
#[derive(Debug, Clone)]
pub struct ActorStats {
    pub messages_received: u64,
    pub messages_sent: u64,
    pub crashes: u32,
    pub restarts: u32,
    pub total_cpu_time_us: u64,
    pub last_heartbeat: u64,
}

impl ActorStats {
    pub fn new() -> Self {
        Self {
            messages_received: 0,
            messages_sent: 0,
            crashes: 0,
            restarts: 0,
            total_cpu_time_us: 0,
            last_heartbeat: 0,
        }
    }
}

/// 🎭 THE OMNI ACTOR
/// Unit eksekusi terisolasi — berkomunikasi hanya via mailbox
pub struct OmniActor {
    pub id: u64,
    pub name: String,
    pub state: ActorState,
    pub supervisor_id: Option<u64>,   // Parent supervisor
    pub children: Vec<u64>,           // Child actor IDs
    pub mailbox: VecDeque<ActorMessage>,
    pub mailbox_capacity: usize,
    pub stats: ActorStats,
    pub crash_budget: CrashBudget,
}

/// Crash budget — berapa kali Actor boleh crash sebelum di-escalate
#[derive(Debug, Clone)]
pub struct CrashBudget {
    pub max_crashes: u32,
    pub window_seconds: u64,
    pub crashes_in_window: u32,
    pub window_start: u64,
}

impl CrashBudget {
    pub fn new(max_crashes: u32, window_seconds: u64) -> Self {
        Self {
            max_crashes,
            window_seconds,
            crashes_in_window: 0,
            window_start: 0,
        }
    }

    /// Check apakah masih dalam budget
    pub fn can_restart(&self) -> bool {
        self.crashes_in_window < self.max_crashes
    }

    /// Record a crash
    pub fn record_crash(&mut self) {
        self.crashes_in_window += 1;
    }

    /// Reset window jika sudah expired
    pub fn reset_if_expired(&mut self, current_time: u64) {
        if current_time - self.window_start > self.window_seconds * 1_000_000 {
            self.crashes_in_window = 0;
            self.window_start = current_time;
        }
    }
}

impl OmniActor {
    pub fn new(id: u64, name: &str) -> Self {
        Self {
            id,
            name: name.to_string(),
            state: ActorState::Created,
            supervisor_id: None,
            children: Vec::new(),
            mailbox: VecDeque::new(),
            mailbox_capacity: 1000, // Default 1000 messages
            stats: ActorStats::new(),
            crash_budget: CrashBudget::new(5, 60), // 5 crashes per 60 seconds
        }
    }

    pub fn with_supervisor(mut self, supervisor_id: u64) -> Self {
        self.supervisor_id = Some(supervisor_id);
        self
    }

    pub fn with_crash_budget(mut self, max_crashes: u32, window_seconds: u64) -> Self {
        self.crash_budget = CrashBudget::new(max_crashes, window_seconds);
        self
    }

    // =============================
    // LIFECYCLE HOOKS
    // =============================

    /// Start the actor
    pub fn start(&mut self) {
        self.state = ActorState::Starting;
        println!("[ACTOR {}] 🎭 Starting: {}", self.id, self.name);
        self.state = ActorState::Running;
    }

    /// Stop the actor gracefully
    pub fn stop(&mut self) {
        println!("[ACTOR {}] ⏹️  Stopping: {}", self.id, self.name);
        self.state = ActorState::Stopped;
    }

    /// Simulate a crash
    pub fn crash(&mut self, error: &str) {
        println!("[ACTOR {}] 💥 CRASH: {} — Error: {}", self.id, self.name, error);
        self.state = ActorState::Crashed(error.to_string());
        self.stats.crashes += 1;
        self.crash_budget.record_crash();
    }

    /// Restart after crash
    pub fn restart(&mut self) -> Result<(), String> {
        if !self.crash_budget.can_restart() {
            return Err(format!(
                "❌ Actor '{}' exceeded crash budget ({}/{} in {} sec window) — ESCALATING to supervisor",
                self.name, 
                self.crash_budget.crashes_in_window, 
                self.crash_budget.max_crashes,
                self.crash_budget.window_seconds
            ));
        }

        println!("[ACTOR {}] 🔄 Restarting: {} (crash #{}/{})", 
            self.id, self.name, 
            self.crash_budget.crashes_in_window,
            self.crash_budget.max_crashes);
        
        self.state = ActorState::Restarting;
        // Clear mailbox on restart (messages during crash are lost)
        self.mailbox.clear();
        self.stats.restarts += 1;
        self.state = ActorState::Running;
        
        Ok(())
    }

    // =============================
    // MESSAGE PASSING
    // =============================

    /// Send message to this actor's mailbox
    pub fn receive(&mut self, message: ActorMessage) -> Result<(), String> {
        if self.mailbox.len() >= self.mailbox_capacity {
            return Err(format!(
                "❌ Mailbox full for actor '{}' (capacity: {})",
                self.name, self.mailbox_capacity
            ));
        }

        self.mailbox.push_back(message);
        self.stats.messages_received += 1;
        Ok(())
    }

    /// Process next message in mailbox
    pub fn process_next(&mut self) -> Option<ActorMessage> {
        let msg = self.mailbox.pop_front()?;
        
        // Handle system commands
        match &msg.payload {
            MessagePayload::SystemCommand(cmd) => {
                match cmd {
                    SystemCommand::Stop => self.stop(),
                    SystemCommand::Kill => {
                        self.state = ActorState::Stopped;
                    },
                    SystemCommand::Restart => {
                        let _ = self.restart();
                    },
                    SystemCommand::HealthCheck => {
                        // Update heartbeat
                        self.stats.last_heartbeat = msg.timestamp;
                    },
                    _ => {}
                }
            },
            _ => {
                // Application-level message processing
                self.stats.total_cpu_time_us += 10; // Simulated processing time
            }
        }

        Some(msg)
    }

    /// Check if actor is alive and healthy
    pub fn is_alive(&self) -> bool {
        matches!(self.state, ActorState::Running | ActorState::Starting | ActorState::Suspended)
    }

    /// Get mailbox depth
    pub fn mailbox_depth(&self) -> usize {
        self.mailbox.len()
    }
}

/// Auto-incrementing message ID generator
static mut NEXT_MSG_ID: u64 = 1;

pub fn create_message(from: u64, to: u64, payload: MessagePayload) -> ActorMessage {
    let id = unsafe {
        let id = NEXT_MSG_ID;
        NEXT_MSG_ID += 1;
        id
    };
    ActorMessage {
        id,
        from,
        to,
        payload,
        timestamp: 0,
    }
}
