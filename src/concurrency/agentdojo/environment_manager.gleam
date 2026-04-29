import gleam/result

pub type OmniResult(t) {
  Ok(t)
  Error(String)
}

pub fn spawn_environment(env_id: String) -> OmniResult(String) {
  if env_id == "" {
    Error("Invalid environment ID")
  } else {
    // Gleam concurrent actor logic for AgentDojo isolated environments
    Ok("Environment successfully spawned")
  }
}
