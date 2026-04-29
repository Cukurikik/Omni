// OMNI METAGPT: Message Bus
// Rust implementation of an in-memory Pub/Sub message bus enabling decoupled 
// communication between independent agent roles (e.g., PM, Engineer).
// Source: geekan/MetaGPT

use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use tokio::sync::broadcast;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum BusError {
    #[error("Channel {0} does not exist.")]
    ChannelNotFound(String),
    #[error("Failed to publish message.")]
    PublishFailed,
}

#[derive(Clone, Debug)]
pub struct AgentMessage {
    pub sender: String,
    pub receiver_role: String,
    pub content: String,
    pub artifact_type: String, // e.g., "PRD", "SystemDesign", "Code"
}

pub struct MessageBus {
    channels: Mutex<HashMap<String, broadcast::Sender<AgentMessage>>>,
}

impl MessageBus {
    pub fn new() -> Self {
        Self {
            channels: Mutex::new(HashMap::new()),
        }
    }

    /// Registers a new topic/role channel
    pub fn create_channel(&self, role_name: &str) {
        let (tx, _) = broadcast::channel(100);
        self.channels.lock().unwrap().insert(role_name.to_string(), tx);
    }

    /// Subscribe to messages directed at a specific role
    pub fn subscribe(&self, role_name: &str) -> Result<broadcast::Receiver<AgentMessage>, BusError> {
        let map = self.channels.lock().unwrap();
        if let Some(tx) = map.get(role_name) {
            Ok(tx.subscribe())
        } else {
            Err(BusError::ChannelNotFound(role_name.to_string()))
        }
    }

    /// Publish an artifact to the next role in the pipeline
    pub fn publish(&self, target_role: &str, msg: AgentMessage) -> Result<(), BusError> {
        let map = self.channels.lock().unwrap();
        if let Some(tx) = map.get(target_role) {
            tx.send(msg).map_err(|_| BusError::PublishFailed)?;
            Ok(())
        } else {
            Err(BusError::ChannelNotFound(target_role.to_string()))
        }
    }
}
