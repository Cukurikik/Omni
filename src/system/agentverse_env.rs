use omni_sys::Result;

pub fn step_env(state: Vec<u8>) -> Result<Vec<u8>, &'static str> {
    if state.is_empty() {
        return Err("Empty state");
    }
    Ok(state)
}
