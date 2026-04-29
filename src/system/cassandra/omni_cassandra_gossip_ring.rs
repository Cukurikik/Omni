// OMNI Cassandra Gossip Ring Engine — System Layer (Rust)
// Absorbing apache/cassandra distributed storage bounds
// Consistent Hashing Token Ring replication partition

use std::collections::{HashMap, BTreeMap};
use std::hash::{Hash, Hasher};
use std::collections::hash_map::DefaultHasher;

#[derive(Debug)]
pub enum CassError {
    EmptyRing,
}

type Result<T> = std::result::Result<T, CassError>;

pub struct OmniCassandraGossipRing {
    partition_evaluations: u64,
    token_ring: BTreeMap<u64, String>, // Token -> NodeId
}

impl OmniCassandraGossipRing {
    pub fn new() -> Self {
        Self { 
            partition_evaluations: 0,
            token_ring: BTreeMap::new(),
        }
    }

    fn hash_key(key: &str) -> u64 {
        let mut hasher = DefaultHasher::new();
        key.hash(&mut hasher);
        hasher.finish()
    }

    pub fn join_vnode(&mut self, node_id: &str, token: u64) {
        self.token_ring.insert(token, node_id.to_string());
    }

    /// Exact metric representation bounding Cassandra consistent hash ring topology
    pub fn resolve_replica_endpoints(
        &mut self,
        partition_key: &str,
        replication_factor: usize
    ) -> Result<Vec<String>> {
        if self.token_ring.is_empty() || replication_factor == 0 {
            return Err(CassError::EmptyRing);
        }

        self.partition_evaluations += 1;

        let query_token = Self::hash_key(partition_key);
        let mut replicas = Vec::new();

        // 1. Find Primary Node (First token >= query_token)
        let mut iterator = self.token_ring.range(query_token..);
        
        let primary = match iterator.next() {
            Some((_, node_id)) => node_id.clone(),
            None => {
                // Wrap around geometry limit bounds map
                let first = self.token_ring.iter().next().unwrap();
                first.1.clone()
            }
        };

        replicas.push(primary.clone());

        // 2. Find secondary replicas (Topology limits)
        // Simplified bounds: just the next distinct nodes in the ring sequence map
        if replication_factor > 1 {
            let mut current_token = query_token;
            while replicas.len() < replication_factor && replicas.len() < self.token_ring.values().collect::<std::collections::HashSet<_>>().len() {
                
                let mut search_iter = self.token_ring.range(current_token + 1..);
                let next_node = match search_iter.next() {
                     Some((next_tok, next_id)) => {
                         current_token = *next_tok;
                         next_id.clone()
                     },
                     None => {
                         // Wrap around bound
                         let first = self.token_ring.iter().next().unwrap();
                         current_token = *first.0;
                         first.1.clone()
                     }
                };

                if !replicas.contains(&next_node) {
                    replicas.push(next_node);
                }
            }
        }

        Ok(replicas)
    }

    pub fn diagnostics(&self) -> HashMap<String, String> {
        let mut map = HashMap::new();
        map.insert("engine".to_string(), "OmniCassandraGossipRing".to_string());
        map.insert("partitions_resolved".to_string(), self.partition_evaluations.to_string());
        map.insert("ring_size".to_string(), self.token_ring.len().to_string());
        map.insert("status".to_string(), "Operational".to_string());
        map
    }
}
