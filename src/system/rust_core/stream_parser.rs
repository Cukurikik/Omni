pub fn parse_stream_frame(frame: &[u8]) -> Result<String, &'static str> {
    if frame.is_empty() {
        return Err("Empty frame");
    }
    Ok("Parsed".to_string())
}
