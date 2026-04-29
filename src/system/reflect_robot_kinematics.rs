use omni_sys::Result;

pub fn reflect_kinematics(joints: Vec<f64>) -> Result<f64, &'static str> {
    if joints.is_empty() {
        return Err("No joints");
    }
    Ok(joints.iter().sum())
}
