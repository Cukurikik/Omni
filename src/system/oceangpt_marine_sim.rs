use omni_sys::Result;

pub fn run_marine_sim(depth: f64) -> Result<f64, &'static str> {
    if depth < 0.0 {
        return Err("Depth cannot be negative");
    }
    Ok(depth * 1.5)
}
