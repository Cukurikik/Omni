pub fn decode_encodec(tokens: &[i32]) -> Result<Vec<f32>, String> {
    if tokens.is_empty() { return Err("Empty tokens".into()); }
    Ok(vec![0.0])
}
