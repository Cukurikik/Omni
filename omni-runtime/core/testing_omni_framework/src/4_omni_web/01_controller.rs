use omni_core::net::router::OmniRouter;

pub fn init_rust_controller(router: &mut OmniRouter) {
    router.insert("/api/rust", || {
        r#"{"language": "Rust", "status": "200 OK", "message": "Zero-Cost Abstraction Reached"}"#.to_string()
    });
}
