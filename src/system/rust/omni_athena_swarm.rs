use std::sync::Arc;
use tokio::sync::mpsc;
use log::{info, error};

pub struct SwarmAgent {
    pub id: String,
    pub capability: String,
}

pub struct AthenaSwarmOS {
    agents: Vec<Arc<SwarmAgent>>,
    task_tx: mpsc::Sender<String>,
    task_rx: mpsc::Receiver<String>,
}

impl AthenaSwarmOS {
    pub fn new(capacity: usize) -> Self {
        let (tx, rx) = mpsc::channel(capacity);
        Self {
            agents: Vec::new(),
            task_tx: tx,
            task_rx: rx,
        }
    }

    pub fn register_agent(&mut self, agent: SwarmAgent) {
        info!("Registering agent: {}", agent.id);
        self.agents.push(Arc::new(agent));
    }

    pub async fn dispatch_task(&self, task: String) -> Result<(), mpsc::error::SendError<String>> {
        self.task_tx.send(task).await
    }

    pub async fn run_event_loop(&mut self) {
        while let Some(task) = self.task_rx.recv().await {
            info!("AthenaOS Swarm processing task: {}", task);
            // In a real system, tasks are matched to agent capabilities
            if let Some(agent) = self.agents.first() {
                info!("Agent {} executing {}", agent.id, task);
            } else {
                error!("No agents available for task: {}", task);
            }
        }
    }
}
