#![allow(dead_code)]
// ==========================================
// 🔥 HOT PATH PROFILER
// ==========================================
// Setiap basic block yang dieksekusi oleh interpreter
// dicatat frekuensinya di sini. Ketika counter melebihi
// threshold, path dipromosikan ke tier berikutnya:
//
//   Cold (0) → Warm (100) → Hot (1000) → Compiled
//
// DNA: V8 Ignition → TurboFan pipeline
// ==========================================

use std::collections::HashMap;

/// Tier eksekusi — semakin tinggi, semakin optimal
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ExecutionTier {
    /// Belum pernah dieksekusi atau jarang
    Cold,
    /// Dieksekusi cukup sering, mulai dicatat
    Warm,
    /// Dieksekusi sangat sering, siap di-JIT compile
    Hot,
    /// Sudah di-compile ke native machine code
    Compiled,
    /// De-optimized karena assumption violation
    Deoptimized,
}

/// Entry profiling untuk satu code path
#[derive(Debug, Clone)]
pub struct HotPathEntry {
    pub path_id: String,
    pub execution_count: u64,
    pub total_instructions: u64,
    pub tier: ExecutionTier,
    pub avg_instructions_per_exec: f64,
    pub last_execution_timestamp: u64,
    /// Type feedback: observed types at each position
    pub type_feedback: Vec<TypeObservation>,
    /// Branch prediction data
    pub branch_history: Vec<BranchRecord>,
}

/// Observed type at a specific instruction position
#[derive(Debug, Clone)]
pub struct TypeObservation {
    pub position: u32,
    pub observed_types: Vec<String>,
    pub is_monomorphic: bool,  // Only one type seen = safe to specialize
    pub is_megamorphic: bool,  // Too many types = don't specialize
}

/// Branch taken/not-taken history
#[derive(Debug, Clone)]
pub struct BranchRecord {
    pub branch_id: u32,
    pub taken_count: u64,
    pub not_taken_count: u64,
}

impl BranchRecord {
    pub fn bias(&self) -> f64 {
        let total = self.taken_count + self.not_taken_count;
        if total == 0 { return 0.5; }
        self.taken_count as f64 / total as f64
    }

    /// Strongly biased branches (>90% one way) can be speculated
    pub fn is_predictable(&self) -> bool {
        let bias = self.bias();
        bias > 0.9 || bias < 0.1
    }
}

/// 🔥 THE HOT PATH PROFILER
pub struct HotPathProfiler {
    entries: HashMap<String, HotPathEntry>,
    warm_threshold: u64,
    hot_threshold: u64,
    timestamp_counter: u64,
}

impl HotPathProfiler {
    pub fn new(warm_threshold: u64, hot_threshold: u64) -> Self {
        Self {
            entries: HashMap::new(),
            warm_threshold,
            hot_threshold,
            timestamp_counter: 0,
        }
    }

    /// Record an execution of a path. Returns tier change if applicable.
    pub fn record(&mut self, path_id: &str, instruction_count: u64) -> Option<ExecutionTier> {
        self.timestamp_counter += 1;
        
        let entry = self.entries.entry(path_id.to_string()).or_insert_with(|| {
            HotPathEntry {
                path_id: path_id.to_string(),
                execution_count: 0,
                total_instructions: 0,
                tier: ExecutionTier::Cold,
                avg_instructions_per_exec: 0.0,
                last_execution_timestamp: 0,
                type_feedback: Vec::new(),
                branch_history: Vec::new(),
            }
        });

        entry.execution_count += 1;
        entry.total_instructions += instruction_count;
        entry.avg_instructions_per_exec = 
            entry.total_instructions as f64 / entry.execution_count as f64;
        entry.last_execution_timestamp = self.timestamp_counter;

        // Check tier promotion
        let old_tier = entry.tier.clone();
        
        if entry.execution_count >= self.hot_threshold && old_tier == ExecutionTier::Warm {
            entry.tier = ExecutionTier::Hot;
            return Some(ExecutionTier::Hot);
        }
        
        if entry.execution_count >= self.warm_threshold && old_tier == ExecutionTier::Cold {
            entry.tier = ExecutionTier::Warm;
            return Some(ExecutionTier::Warm);
        }

        None
    }

    /// Record type feedback at a position
    pub fn record_type(&mut self, path_id: &str, position: u32, observed_type: &str) {
        if let Some(entry) = self.entries.get_mut(path_id) {
            // Find or create the type observation
            if let Some(obs) = entry.type_feedback.iter_mut().find(|o| o.position == position) {
                if !obs.observed_types.contains(&observed_type.to_string()) {
                    obs.observed_types.push(observed_type.to_string());
                }
                obs.is_monomorphic = obs.observed_types.len() == 1;
                obs.is_megamorphic = obs.observed_types.len() > 4;
            } else {
                entry.type_feedback.push(TypeObservation {
                    position,
                    observed_types: vec![observed_type.to_string()],
                    is_monomorphic: true,
                    is_megamorphic: false,
                });
            }
        }
    }

    /// Record branch outcome
    pub fn record_branch(&mut self, path_id: &str, branch_id: u32, taken: bool) {
        if let Some(entry) = self.entries.get_mut(path_id) {
            if let Some(br) = entry.branch_history.iter_mut().find(|b| b.branch_id == branch_id) {
                if taken { br.taken_count += 1; } else { br.not_taken_count += 1; }
            } else {
                entry.branch_history.push(BranchRecord {
                    branch_id,
                    taken_count: if taken { 1 } else { 0 },
                    not_taken_count: if taken { 0 } else { 1 },
                });
            }
        }
    }

    /// Mark a path as compiled
    pub fn mark_compiled(&mut self, path_id: &str) {
        if let Some(entry) = self.entries.get_mut(path_id) {
            entry.tier = ExecutionTier::Compiled;
        }
    }

    /// Mark a path as deoptimized
    pub fn mark_deoptimized(&mut self, path_id: &str) {
        if let Some(entry) = self.entries.get_mut(path_id) {
            entry.tier = ExecutionTier::Deoptimized;
            // Reset counter for re-profiling
            entry.execution_count = 0;
        }
    }

    /// Get execution count for a path
    pub fn get_count(&self, path_id: &str) -> u64 {
        self.entries.get(path_id).map(|e| e.execution_count).unwrap_or(0)
    }

    /// Get entry for a path
    pub fn get_entry(&self, path_id: &str) -> Option<&HotPathEntry> {
        self.entries.get(path_id)
    }

    /// Total tracked paths
    pub fn total_paths(&self) -> usize {
        self.entries.len()
    }

    /// Get all hot paths
    pub fn hot_paths(&self) -> Vec<&HotPathEntry> {
        self.entries.values()
            .filter(|e| e.tier == ExecutionTier::Hot || e.tier == ExecutionTier::Compiled)
            .collect()
    }

    /// Print profiling report
    pub fn print_report(&self) {
        println!("\n🔥 HOT PATH PROFILING REPORT:");
        println!("═══════════════════════════════════════════════════════");
        
        let mut sorted: Vec<_> = self.entries.values().collect();
        sorted.sort_by(|a, b| b.execution_count.cmp(&a.execution_count));
        
        for entry in sorted.iter().take(20) {
            let tier_icon = match entry.tier {
                ExecutionTier::Cold => "❄️ ",
                ExecutionTier::Warm => "🌡️",
                ExecutionTier::Hot => "🔥",
                ExecutionTier::Compiled => "⚡",
                ExecutionTier::Deoptimized => "⚠️ ",
            };
            println!("  {} {:30} exec={:>8} avg_inst={:.1} types={} branches={}",
                tier_icon,
                entry.path_id,
                entry.execution_count,
                entry.avg_instructions_per_exec,
                entry.type_feedback.len(),
                entry.branch_history.len(),
            );
        }
        println!("═══════════════════════════════════════════════════════");
    }
}
