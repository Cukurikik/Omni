// Unit test: IoEngine submit/poll
#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn test_io_submit() {
        let mut e = IoEngine::new(64).unwrap();
        let r = e.submit(IoRequest { op: IoOp::Read, fd: 0, buf: vec![], offset: 0 });
        assert!(r.is_ok());
    }
}