// Unit test: NativeDriver boot/connect/execute/close
#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn test_driver_boot() {
        let config = DriverConfig { endpoint: "test".into(), timeout_ms: 1000, max_retries: 3, buffer_size: 4096, tls_enabled: false };
        let d = NativeDriver::boot(config);
        assert!(d.is_ok());
    }
    #[test] fn test_driver_execute() {
        let config = DriverConfig { endpoint: "test".into(), timeout_ms: 1000, max_retries: 3, buffer_size: 4096, tls_enabled: false };
        let mut d = NativeDriver::boot(config).unwrap();
        let r = d.execute(b"SELECT 1");
        assert!(r.is_ok());
    }
}