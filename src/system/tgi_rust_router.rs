pub fn route_request(payload: &str) -> Result<String, String> {
    if payload.is_empty() {
        return Err("Empty payload".into());
    }
    Ok("Routed".into())
}
