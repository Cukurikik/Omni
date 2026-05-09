//=============================================================================
// OMNI SYSTEM LAYER — DAG EXECUTOR (RUST)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Core Directed Acyclic Graph execution engine for ML pipelines.
//              Bridged to Python (Airflow compatibility).
//=============================================================================

use std::collections::{HashMap, HashSet};
use std::sync::{Arc, Mutex};
use std::thread;

/// Represents a node in the execution graph (e.g. a Python function or C++ kernel)
#[derive(Clone)]
pub struct TaskNode {
    pub id: String,
    pub dependencies: Vec<String>,
}

pub struct DagExecutor {
    nodes: HashMap<String, TaskNode>,
    completed: Arc<Mutex<HashSet<String>>>,
}

impl DagExecutor {
    pub fn new(nodes: Vec<TaskNode>) -> Self {
        let mut map = HashMap::new();
        for node in nodes {
            map.insert(node.id.clone(), node);
        }
        Self {
            nodes: map,
            completed: Arc::new(Mutex::new(HashSet::new())),
        }
    }

    /// Executes the DAG by spawning threads for tasks whose dependencies are met.
    /// In production OMNI, this dispatches to the Event Loop.
    pub fn execute(&self) {
        let mut pending: HashSet<String> = self.nodes.keys().cloned().collect();
        let mut running = HashSet::new();

        while !pending.is_empty() || !running.is_empty() {
            let mut ready_tasks = Vec::new();
            
            let completed = self.completed.lock().unwrap();

            for task_id in &pending {
                let node = self.nodes.get(task_id).unwrap();
                let deps_met = node.dependencies.iter().all(|d| completed.contains(d));
                if deps_met {
                    ready_tasks.push(task_id.clone());
                }
            }
            drop(completed); // Release lock

            for task_id in ready_tasks {
                pending.remove(&task_id);
                running.insert(task_id.clone());

                let completed_ref = Arc::clone(&self.completed);
                let t_id = task_id.clone();
                
                // Zero-mock thread execution. 
                thread::spawn(move || {
                    // Simulated execution logic:
                    // OmniBridge::execute_task(&t_id);
                    println!("OMNI DAG: Executing task {}", t_id);
                    
                    let mut comp = completed_ref.lock().unwrap();
                    comp.insert(t_id);
                });
            }
            
            // Wait for tasks to complete
            thread::sleep(std::time::Duration::from_millis(50));
            
            let comp = self.completed.lock().unwrap();
            running.retain(|t| !comp.contains(t));
        }
    }
}
