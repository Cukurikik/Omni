use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;

#[derive(Serialize, Deserialize, Debug)]
pub struct NexusProject {
    pub name: String,
    pub version: String,
    pub author: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct DependencyInfo {
    pub url: String,
    pub hash: Option<String>,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Permissions {
    pub allow_net: Option<Vec<String>>,
    pub allow_fs_read: Option<Vec<String>>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct NexusManifest {
    pub project: NexusProject,
    pub dependencies: HashMap<String, DependencyInfo>,
    pub permissions: Option<HashMap<String, Permissions>>,
}

impl NexusManifest {
    pub fn parse(path: &str) -> std::io::Result<Self> {
        let content = fs::read_to_string(path)?;
        let nexus_file: NexusManifest = toml::from_str(&content).expect("Gagal mem-parsing Nexus.toml");
        Ok(nexus_file)
    }
}
