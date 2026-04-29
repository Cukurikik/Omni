// OMNI System Layer - ReDel State Store
use std::collections::HashMap;

pub enum StoreError {
    StateNotFound,
    Corruption,
}

pub struct StateStore {
    states: HashMap<String, Vec<u8>>,
}

impl StateStore {
    pub fn new() -> Self {
        StateStore {
            states: HashMap::new(),
        }
    }

    pub fn snapshot_agent_state(&mut self, agent_id: &str, state: Vec<u8>) -> Result<(), StoreError> {
        self.states.insert(agent_id.to_string(), state);
        Ok(())
    }

    pub fn restore_agent_state(&self, agent_id: &str) -> Result<Vec<u8>, StoreError> {
        self.states.get(agent_id).cloned().ok_or(StoreError::StateNotFound)
    }
}
