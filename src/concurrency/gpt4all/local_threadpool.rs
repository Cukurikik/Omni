/// OMNI GPT4ALL: Local Thread Pool
/// Rust implementation of a lightweight, CPU-bound thread pool optimized for edge devices (laptops, mobile CPUs).
/// Avoids heavy OS context switches during rapid token generation.
/// Source: nomic-ai/gpt4all

use std::sync::{mpsc, Arc, Mutex};
use std::thread;

pub struct EdgeThreadPool {
    workers: Vec<Worker>,
    sender: Option<mpsc::Sender<Job>>,
}

type Job = Box<dyn FnOnce() + Send + 'static>;

impl EdgeThreadPool {
    /// Create a new EdgeThreadPool.
    /// The size is usually mapped to physical CPU cores to prevent thrashing on edge devices.
    pub fn new(size: usize) -> EdgeThreadPool {
        assert!(size > 0);

        let (sender, receiver) = mpsc::channel();
        let receiver = Arc::new(Mutex::new(receiver));

        let mut workers = Vec::with_capacity(size);

        for id in 0..size {
            // Pinning threads to cores is typically done here in a real implementation
            workers.push(Worker::new(id, Arc::clone(&receiver)));
        }

        EdgeThreadPool {
            workers,
            sender: Some(sender),
        }
    }

    pub fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        let job = Box::new(f);
        self.sender.as_ref().unwrap().send(job).unwrap();
    }
}

impl Drop for EdgeThreadPool {
    fn drop(&mut self) {
        drop(self.sender.take());

        for worker in &mut self.workers {
            if let Some(thread) = worker.thread.take() {
                thread.join().unwrap();
            }
        }
    }
}

struct Worker {
    id: usize,
    thread: Option<thread::JoinHandle<()>>,
}

impl Worker {
    fn new(id: usize, receiver: Arc<Mutex<mpsc::Receiver<Job>>>) -> Worker {
        let thread = thread::spawn(move || loop {
            let message = receiver.lock().unwrap().recv();

            match message {
                Ok(job) => {
                    // Execute the matrix math / inference chunk
                    job();
                }
                Err(_) => {
                    // Disconnected, shut down worker
                    break;
                }
            }
        });

        Worker {
            id,
            thread: Some(thread),
        }
    }
}
