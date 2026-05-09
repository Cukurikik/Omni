// OMNI System — Rust Priority Work Scheduler for Inference
// Priority-based job scheduler with work-stealing semantics.

use std::sync::{Arc, Mutex, Condvar};
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::thread;
use std::collections::BinaryHeap;
use std::cmp::Ordering as CmpOrd;
use std::time::Instant;

type Job = Box<dyn FnOnce() + Send + 'static>;

struct PriJob { priority: u32, job: Job, ts: Instant }
impl PartialEq for PriJob { fn eq(&self, o: &Self) -> bool { self.priority == o.priority } }
impl Eq for PriJob {}
impl PartialOrd for PriJob { fn partial_cmp(&self, o: &Self) -> Option<CmpOrd> { Some(self.cmp(o)) } }
impl Ord for PriJob { fn cmp(&self, o: &Self) -> CmpOrd { self.priority.cmp(&o.priority).then(o.ts.cmp(&self.ts)) } }

pub struct InferenceScheduler {
    queue: Arc<(Mutex<BinaryHeap<PriJob>>, Condvar)>,
    shutdown: Arc<AtomicBool>,
    completed: Arc<AtomicU64>,
    handles: Vec<thread::JoinHandle<()>>,
}

impl InferenceScheduler {
    pub fn new(threads: usize) -> Self {
        let q = Arc::new((Mutex::new(BinaryHeap::new()), Condvar::new()));
        let sd = Arc::new(AtomicBool::new(false));
        let done = Arc::new(AtomicU64::new(0));
        let mut handles = Vec::new();
        for i in 0..threads {
            let qc = Arc::clone(&q); let sdc = Arc::clone(&sd); let dc = Arc::clone(&done);
            handles.push(thread::Builder::new().name(format!("sched-{i}")).spawn(move || {
                loop {
                    let job = { let (lk, cv) = &*qc; let mut h = lk.lock().unwrap();
                        while h.is_empty() && !sdc.load(Ordering::Relaxed) { h = cv.wait(h).unwrap(); }
                        if sdc.load(Ordering::Relaxed) && h.is_empty() { return; } h.pop() };
                    if let Some(pj) = job { (pj.job)(); dc.fetch_add(1, Ordering::Relaxed); }
                }
            }).unwrap());
        }
        Self { queue: q, shutdown: sd, completed: done, handles }
    }
    pub fn submit(&self, job: Job, priority: u32) {
        let (lk, cv) = &*self.queue;
        lk.lock().unwrap().push(PriJob { priority, job, ts: Instant::now() });
        cv.notify_one();
    }
    pub fn completed(&self) -> u64 { self.completed.load(Ordering::Relaxed) }
    pub fn pending(&self) -> usize { self.queue.0.lock().unwrap().len() }
}
impl Drop for InferenceScheduler {
    fn drop(&mut self) { self.shutdown.store(true, Ordering::Relaxed); self.queue.1.notify_all();
        for h in self.handles.drain(..) { let _ = h.join(); } }
}
