// omni_map_reduce.rs — Concurrent MapReduce Engine
// Layer: Domain / Compute / Search
//
// Implements an in-memory, thread-pool driven MapReduce framework.
// Allows massive datasets to be processed in parallel by distributing
// Map operations across cores and aggregating via Reduce. Zero mock.

use std::collections::HashMap;
use std::hash::Hash;
use std::sync::{mpsc, Arc, Mutex};
use std::thread;

/// The Map function signature: Takes an input item and outputs a list of (Key, Value) pairs.
pub type MapFn<I, K, V> = Arc<dyn Fn(I) -> Vec<(K, V)> + Send + Sync + 'static>;

/// The Reduce function signature: Takes a Key and a list of Values, outputs a final Value.
pub type ReduceFn<K, V, R> = Arc<dyn Fn(&K, &[V]) -> R + Send + Sync + 'static>;

pub struct OmniMapReduce<I, K, V, R> {
    map_fn: MapFn<I, K, V>,
    reduce_fn: ReduceFn<K, V, R>,
    num_threads: usize,
}

impl<I, K, V, R> OmniMapReduce<I, K, V, R>
where
    I: Send + 'static,
    K: Eq + Hash + Clone + Send + Sync + 'static,
    V: Clone + Send + Sync + 'static,
    R: Send + 'static,
{
    pub fn new(map_fn: MapFn<I, K, V>, reduce_fn: ReduceFn<K, V, R>, num_threads: usize) -> Self {
        OmniMapReduce {
            map_fn,
            reduce_fn,
            num_threads,
        }
    }

    /// Executes the MapReduce job on a given dataset.
    pub fn execute(&self, data: Vec<I>) -> HashMap<K, R> {
        let (map_tx, map_rx) = mpsc::channel();
        let map_fn = self.map_fn.clone();

        // --- MAP PHASE ---
        // We use a basic chunking strategy for the thread pool
        let chunk_size = (data.len() + self.num_threads - 1) / self.num_threads;
        if chunk_size == 0 {
            return HashMap::new();
        }

        let mut chunks: Vec<Vec<I>> = Vec::new();
        let mut current_chunk = Vec::new();
        for item in data {
            current_chunk.push(item);
            if current_chunk.len() == chunk_size {
                chunks.push(current_chunk);
                current_chunk = Vec::new();
            }
        }
        if !current_chunk.is_empty() {
            chunks.push(current_chunk);
        }

        let mut handles = Vec::new();

        for chunk in chunks {
            let tx = map_tx.clone();
            let mapper = map_fn.clone();

            let handle = thread::spawn(move || {
                for item in chunk {
                    let kvs = mapper(item);
                    for kv in kvs {
                        let _ = tx.send(kv);
                    }
                }
            });
            handles.push(handle);
        }

        // Close the original sender so the receiver will eventually close
        drop(map_tx);

        for handle in handles {
            let _ = handle.join();
        }

        // --- SHUFFLE PHASE ---
        // Group values by key
        let mut grouped_data: HashMap<K, Vec<V>> = HashMap::new();
        for (k, v) in map_rx {
            grouped_data.entry(k).or_insert_with(Vec::new).push(v);
        }

        // --- REDUCE PHASE ---
        let grouped_data = Arc::new(Mutex::new(grouped_data.into_iter().collect::<Vec<_>>()));
        let (reduce_tx, reduce_rx) = mpsc::channel();
        let reduce_fn = self.reduce_fn.clone();

        let mut reduce_handles = Vec::new();
        for _ in 0..self.num_threads {
            let tx = reduce_tx.clone();
            let reducer = reduce_fn.clone();
            let data_ref = Arc::clone(&grouped_data);

            let handle = thread::spawn(move || {
                loop {
                    // Pop a group to process
                    let item = {
                        let mut data_lock = data_ref.lock().unwrap();
                        data_lock.pop()
                    };

                    match item {
                        Some((k, values)) => {
                            let result = reducer(&k, &values);
                            let _ = tx.send((k, result));
                        }
                        None => break, // No more groups to process
                    }
                }
            });
            reduce_handles.push(handle);
        }

        drop(reduce_tx);

        for handle in reduce_handles {
            let _ = handle.join();
        }

        // --- FINALIZE ---
        let mut final_results = HashMap::new();
        for (k, r) in reduce_rx {
            final_results.insert(k, r);
        }

        final_results
    }
}
