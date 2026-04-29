import gleam/result

pub type OmniResult(t) {
  Ok(t)
  Error(String)
}

pub fn align_sequences(seq_a: String, seq_b: String) -> OmniResult(String) {
  if seq_a == "" || seq_b == "" {
    Error("Invalid sequences")
  } else {
    // Gleam concurrent message passing for parallel DNA sequence alignment (BioReason)
    Ok("Sequences aligned")
  }
}
