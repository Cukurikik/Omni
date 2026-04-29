/// OMNI llama.cpp: Thread Pool for GGML Computation
/// Rust concurrency abstractions mapped over C/GGML workloads for CPU-based tensor operations.
/// Source: ggerganov/llama.cpp

use std::sync::{Arc, Mutex, Condvar};
use std::thread;

pub enum ThreadPoolError {
    InitializationFailed,
    TaskSubmissionFailed,
}

type Job = Box<dyn FnOnce() + Send + 'static>;

struct Worker {
    id: usize,
    thread: Option<thread::JoinHandle<()>>,
}

struct SharedState {
    jobs: Vec<Job>,
    terminate: bool,
}

pub struct GGMLThreadPool {
    workers: Vec<Worker>,
    state: Arc<(Mutex<SharedState>, Condvar)>,
}

impl GGMLThreadPool {
    pub fn new(num_threads: usize) -> Result<Self, ThreadPoolError> {
        if num_threads == 0 {
            return Err(ThreadPoolError::InitializationFailed);
        }

        let state = Arc::new((
            Mutex::new(SharedState {
                jobs: Vec::new(),
                terminate: false,
            }),
            Condvar::new(),
        ));

        let mut workers = Vec::with_capacity(num_threads);

        for id in 0..num_threads {
            let state_clone = Arc::clone(&state);
            
            let handle = thread::spawn(move || {
                let (lock, cvar) = &*state_clone;
                loop {
                    let mut state = lock.lock().unwrap();
                    
                    while state.jobs.is_empty() && !state.terminate {
                        state = cvar.wait(state).unwrap();
                    }

                    if state.terminate && state.jobs.is_empty() {
                        break;
                    }

                    if let Some(job) = state.jobs.pop() {
                        // Drop lock while executing the job to allow other workers to pick up tasks
                        drop(state);
                        job();
                    }
                }
            });

            workers.push(Worker {
                id,
                thread: Some(handle),
            });
        }

        Ok(GGMLThreadPool { workers, state })
    }

    pub fn execute<F>(&self, f: F) -> Result<(), ThreadPoolError>
    where
        F: FnOnce() + Send + 'static,
    {
        let (lock, cvar) = &*self.state;
        let mut state = lock.lock().map_err(|_| ThreadPoolError::TaskSubmissionFailed)?;
        
        state.jobs.push(Box::new(f));
        cvar.notify_one();
        
        Ok(())
    }
}

impl Drop for GGMLThreadPool {
    fn drop(&mut self) {
        let (lock, cvar) = &*self.state;
        
        {
            let mut state = lock.lock().unwrap();
            state.terminate = true;
        }
        
        cvar.notify_all();

        for worker in &mut self.workers {
            if let Some(thread) = worker.thread.take() {
                thread.join().unwrap();
            }
        }
    }
}
