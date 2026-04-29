// OMNI LOCALAI: Inference Pool
// Rust thread pool designed to handle concurrent LLM generation requests safely 
// while preventing GPU/CPU OOM via strict semaphore control.
// Source: mudler/LocalAI

use std::sync::{Arc, Mutex};
use std::thread;
use tokio::sync::{mpsc, Semaphore};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum PoolError {
    #[error("Inference queue is full.")]
    QueueFull,
    #[error("Worker thread panicked.")]
    WorkerPanic,
}

pub struct InferenceRequest {
    pub prompt: String,
    pub max_tokens: usize,
    pub tx: mpsc::Sender<String>, // Channel to stream tokens back
}

pub struct InferencePool {
    sender: mpsc::Sender<InferenceRequest>,
    concurrency_limit: Arc<Semaphore>,
}

impl InferencePool {
    pub fn new(workers: usize, queue_size: usize) -> Self {
        let (tx, mut rx) = mpsc::channel::<InferenceRequest>(queue_size);
        let sem = Arc::new(Semaphore::new(workers));

        // Spawn a dedicated manager thread to avoid blocking async executors
        let sem_clone = sem.clone();
        thread::spawn(move || {
            let rt = tokio::runtime::Runtime::new().unwrap();
            rt.block_on(async move {
                while let Some(req) = rx.recv().await {
                    let permit = sem_clone.clone().acquire_owned().await.unwrap();
                    
                    tokio::spawn(async move {
                        // Pass to GGML backend via FFI
                        Self::execute_inference(req).await;
                        drop(permit); // Release lock when done
                    });
                }
            });
        });

        Self {
            sender: tx,
            concurrency_limit: sem,
        }
    }

    pub async fn submit(&self, req: InferenceRequest) -> Result<(), PoolError> {
        self.sender.send(req).await.map_err(|_| PoolError::QueueFull)
    }

    async fn execute_inference(req: InferenceRequest) {
        // Simulated execution replacing the actual FFI call for structural purposes
        for i in 0..req.max_tokens {
            let token = format!(" token_{}", i);
            if req.tx.send(token).await.is_err() {
                break; // Client disconnected
            }
            tokio::time::sleep(std::time::Duration::from_millis(50)).await;
        }
    }
}
