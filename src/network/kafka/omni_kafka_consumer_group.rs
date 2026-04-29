// OMNI Kafka Consumer Group Engine — Concurrency Layer (Rust)
// Absorbing apache/kafka partition assignment
// Range and Round-Robin partition deterministic assignment logic

use std::collections::HashMap;

#[derive(Debug)]
pub enum KafkaError {
    InvalidBounds,
    EmptyTopology,
}

type Result<T> = std::result::Result<T, KafkaError>;

pub struct OmniKafkaConsumerGroup {
    assignments_computed: u64,
}

impl OmniKafkaConsumerGroup {
    pub fn new() -> Self {
        Self { assignments_computed: 0 }
    }

    /// Range assignor implementation (like Kafka's default org.apache.kafka.clients.consumer.RangeAssignor)
    pub fn evaluate_range_assignment(
        &mut self,
        consumer_ids: Vec<String>,
        topic_partitions: HashMap<String, u32>
    ) -> Result<HashMap<String, Vec<(String, u32)>>> {
        if consumer_ids.is_empty() || topic_partitions.is_empty() {
            return Err(KafkaError::EmptyTopology);
        }

        self.assignments_computed += 1;

        let mut consumers = consumer_ids;
        consumers.sort(); // Lexicographical sort required by Kafka RangeAssignor protocol
        let c_len = consumers.len() as u32;

        let mut assignments: HashMap<String, Vec<(String, u32)>> = HashMap::new();
        for c in &consumers {
            assignments.insert(c.clone(), Vec::new());
        }

        // Must process topics in sorted order to ensure deterministic assignment
        let mut topics: Vec<String> = topic_partitions.keys().cloned().collect();
        topics.sort();

        for topic in topics {
            let partitions = topic_partitions.get(&topic).unwrap();
            
            let num_partitions_per_consumer = partitions / c_len;
            let consumers_with_extra_partition = partitions % c_len;

            for i in 0..c_len {
                let start = num_partitions_per_consumer * i + std::cmp::min(i, consumers_with_extra_partition);
                let length = num_partitions_per_consumer + if i + 1 > consumers_with_extra_partition { 0 } else { 1 };
                
                for p in start..(start + length) {
                    if let Some(c_vec) = assignments.get_mut(&consumers[i as usize]) {
                        c_vec.push((topic.clone(), p));
                    }
                }
            }
        }

        Ok(assignments)
    }

    pub fn diagnostics(&self) -> HashMap<String, String> {
        let mut map = HashMap::new();
        map.insert("engine".to_string(), "OmniKafkaConsumerGroup".to_string());
        map.insert("assignments_computed".to_string(), self.assignments_computed.to_string());
        map.insert("status".to_string(), "Operational".to_string());
        map
    }
}
