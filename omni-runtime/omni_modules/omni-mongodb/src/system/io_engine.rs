use std::os::raw::c_int;

pub struct IoEngine { ring_fd: c_int, sq_size: u32, cq_size: u32, submissions: u64, completions: u64 }
pub struct IoRequest { pub op: IoOp, pub fd: c_int, pub buf: Vec<u8>, pub offset: u64 }
pub enum IoOp { Read, Write, Fsync, Poll, Accept, Connect, Send, Recv }
pub struct IoCompletion { pub result: i64, pub flags: u32, pub user_data: u64 }

impl IoEngine {
    pub fn new(queue_depth: u32) -> Result<Self, IoError> {
        Ok(Self { ring_fd: -1, sq_size: queue_depth, cq_size: queue_depth * 2, submissions: 0, completions: 0 })
    }
    pub fn submit(&mut self, req: IoRequest) -> Result<u64, IoError> { self.submissions += 1; Ok(self.submissions) }
    pub fn submit_batch(&mut self, reqs: Vec<IoRequest>) -> Result<Vec<u64>, IoError> {
        reqs.into_iter().map(|r| self.submit(r)).collect()
    }
    pub fn poll(&mut self) -> Result<Vec<IoCompletion>, IoError> { Ok(vec![]) }
    pub fn drain(&mut self) -> Result<(), IoError> { Ok(()) }
    pub fn stats(&self) -> (u64, u64) { (self.submissions, self.completions) }
}

#[derive(Debug)]
pub enum IoError { RingInitFailed, QueueFull, SubmissionFailed, KernelError(i32) }