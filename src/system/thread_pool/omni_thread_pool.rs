// omni_thread_pool.rs — Rayon-style Work-Stealing Thread Pool
// Inspired by: OMNI inference parallelism requirements
// Layer: System / Rust
//
// Fixed-size thread pool with work-stealing deques for
// parallel attention head computation and batch processing.

use std::sync::{Arc, Mutex, Condvar};
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::thread;
use std::collections::VecDeque;

type Job = Box<dyn FnOnce() + Send + 'static>;

struct WorkerQueue {
    jobs: Mutex<VecDeque<Job>>,
    notify: Condvar,
}

impl WorkerQueue {
    fn new() -> Self {
        Self {
            jobs: Mutex::new(VecDeque::new()),
            notify: Condvar::new(),
        }
    }

    fn push(&self, job: Job) {
        let mut queue = self.jobs.lock().unwrap();
        queue.push_back(job);
        self.notify.notify_one();
    }

    fn pop(&self) -> Option<Job> {
        let mut queue = self.jobs.lock().unwrap();
        queue.pop_front()
    }

    fn steal(&self) -> Option<Job> {
        let mut queue = self.jobs.lock().unwrap();
        queue.pop_back() // Steal from the back
    }

    fn wait_for_job(&self) -> Option<Job> {
        let mut queue = self.jobs.lock().unwrap();
        while queue.is_empty() {
            queue = self.notify.wait(queue).unwrap();
        }
        queue.pop_front()
    }

    fn len(&self) -> usize {
        self.jobs.lock().unwrap().len()
    }
}

pub struct OmniThreadPool {
    workers: Vec<thread::JoinHandle<()>>,
    queues: Vec<Arc<WorkerQueue>>,
    global_queue: Arc<WorkerQueue>,
    shutdown: Arc<AtomicBool>,
    active_jobs: Arc<AtomicUsize>,
    num_threads: usize,
}

impl OmniThreadPool {
    pub fn new(num_threads: usize) -> Self {
        let shutdown = Arc::new(AtomicBool::new(false));
        let active_jobs = Arc::new(AtomicUsize::new(0));
        let global_queue = Arc::new(WorkerQueue::new());

        let mut queues = Vec::with_capacity(num_threads);
        let mut workers = Vec::with_capacity(num_threads);

        for _ in 0..num_threads {
            queues.push(Arc::new(WorkerQueue::new()));
        }

        for worker_id in 0..num_threads {
            let shutdown = Arc::clone(&shutdown);
            let active = Arc::clone(&active_jobs);
            let local_queue = Arc::clone(&queues[worker_id]);
            let global = Arc::clone(&global_queue);
            let all_queues: Vec<Arc<WorkerQueue>> = queues.iter().map(Arc::clone).collect();

            let handle = thread::Builder::new()
                .name(format!("omni-worker-{}", worker_id))
                .spawn(move || {
                    Self::worker_loop(worker_id, shutdown, active, local_queue,
                                      global, all_queues);
                })
                .expect("Failed to spawn worker thread");

            workers.push(handle);
        }

        Self {
            workers,
            queues,
            global_queue,
            shutdown,
            active_jobs,
            num_threads,
        }
    }

    fn worker_loop(
        id: usize,
        shutdown: Arc<AtomicBool>,
        active: Arc<AtomicUsize>,
        local: Arc<WorkerQueue>,
        global: Arc<WorkerQueue>,
        all_queues: Vec<Arc<WorkerQueue>>,
    ) {
        while !shutdown.load(Ordering::Relaxed) {
            // Try local queue first
            if let Some(job) = local.pop() {
                active.fetch_add(1, Ordering::AcqRel);
                job();
                active.fetch_sub(1, Ordering::AcqRel);
                continue;
            }

            // Try global queue
            if let Some(job) = global.pop() {
                active.fetch_add(1, Ordering::AcqRel);
                job();
                active.fetch_sub(1, Ordering::AcqRel);
                continue;
            }

            // Try stealing from other workers
            let mut stolen = false;
            for (i, queue) in all_queues.iter().enumerate() {
                if i == id { continue; }
                if let Some(job) = queue.steal() {
                    active.fetch_add(1, Ordering::AcqRel);
                    job();
                    active.fetch_sub(1, Ordering::AcqRel);
                    stolen = true;
                    break;
                }
            }

            if !stolen {
                // Wait briefly before retrying
                thread::park_timeout(std::time::Duration::from_millis(1));
            }
        }
    }

    /// Submit a job to the global queue
    pub fn submit<F>(&self, job: F)
    where
        F: FnOnce() + Send + 'static,
    {
        if self.shutdown.load(Ordering::Relaxed) {
            panic!("Cannot submit to a shut-down thread pool");
        }
        self.global_queue.push(Box::new(job));
        // Wake a sleeping worker
        if let Some(queue) = self.queues.first() {
            queue.notify.notify_one();
        }
    }

    /// Submit to a specific worker's local queue (affinity)
    pub fn submit_to_worker<F>(&self, worker_id: usize, job: F)
    where
        F: FnOnce() + Send + 'static,
    {
        assert!(worker_id < self.num_threads);
        self.queues[worker_id].push(Box::new(job));
    }

    /// Execute a parallel for-each over a range
    pub fn parallel_for<F>(&self, start: usize, end: usize, func: F)
    where
        F: Fn(usize) + Send + Sync + 'static,
    {
        let func = Arc::new(func);
        let barrier = Arc::new(AtomicUsize::new(end - start));
        let done = Arc::new((Mutex::new(false), Condvar::new()));

        for i in start..end {
            let f = Arc::clone(&func);
            let b = Arc::clone(&barrier);
            let d = Arc::clone(&done);
            let worker = i % self.num_threads;

            self.submit_to_worker(worker, move || {
                f(i);
                if b.fetch_sub(1, Ordering::AcqRel) == 1 {
                    let (lock, cvar) = &*d;
                    let mut finished = lock.lock().unwrap();
                    *finished = true;
                    cvar.notify_all();
                }
            });
        }

        // Wait for all tasks to complete
        let (lock, cvar) = &*done;
        let mut finished = lock.lock().unwrap();
        while !*finished {
            finished = cvar.wait(finished).unwrap();
        }
    }

    pub fn active_count(&self) -> usize {
        self.active_jobs.load(Ordering::Relaxed)
    }

    pub fn pending_count(&self) -> usize {
        let global = self.global_queue.len();
        let local: usize = self.queues.iter().map(|q| q.len()).sum();
        global + local
    }

    pub fn num_threads(&self) -> usize {
        self.num_threads
    }
}

impl Drop for OmniThreadPool {
    fn drop(&mut self) {
        self.shutdown.store(true, Ordering::SeqCst);
        // Wake all workers
        for queue in &self.queues {
            queue.notify.notify_all();
        }
        for worker in self.workers.drain(..) {
            worker.thread().unpark();
            let _ = worker.join();
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_execution() {
        let pool = OmniThreadPool::new(4);
        let counter = Arc::new(AtomicUsize::new(0));

        for _ in 0..100 {
            let c = Arc::clone(&counter);
            pool.submit(move || {
                c.fetch_add(1, Ordering::Relaxed);
            });
        }

        // Wait for completion
        thread::sleep(std::time::Duration::from_millis(200));
        assert_eq!(counter.load(Ordering::Relaxed), 100);
    }

    #[test]
    fn test_parallel_for() {
        let pool = OmniThreadPool::new(4);
        let results = Arc::new(Mutex::new(vec![0u64; 16]));

        let r = Arc::clone(&results);
        pool.parallel_for(0, 16, move |i| {
            let mut data = r.lock().unwrap();
            data[i] = (i * i) as u64;
        });

        let data = results.lock().unwrap();
        for i in 0..16 {
            assert_eq!(data[i], (i * i) as u64);
        }
    }
}
