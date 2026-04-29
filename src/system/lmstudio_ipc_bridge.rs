pub fn send_ipc_message(msg: &str) -> Result<(), String> {
    if msg.is_empty() { return Err("Empty msg".into()); }
    Ok(())
}
