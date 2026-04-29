// OMNI AGENT REGISTRY
// Domain: Local Multi-Agent Registration
// Origin: agentscope-ai/agentscope
use std::collections::HashMap;

#[derive(Debug)]
pub enum RegistryError {
    AgentAlreadyExists,
    InvalidMemorySpace,
}

pub struct AgentRegistry {
    agents: HashMap<String, u64>,
}

impl AgentRegistry {
    pub fn new() -> Self {
        Self { agents: HashMap::new() }
    }

    pub fn register(&mut self, name: String, memory_ptr: u64) -> Result<(), RegistryError> {
        if self.agents.contains_key(&name) {
            return Err(RegistryError::AgentAlreadyExists);
        }
        self.agents.insert(name, memory_ptr);
        Ok(())
    }
}\n