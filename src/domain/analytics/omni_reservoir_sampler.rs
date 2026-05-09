// omni_reservoir_sampler.rs — Reservoir Sampling Algorithm
// Layer: Domain / Analytics
// Inspired by: Apache DataSketches
//
// Selects a random sample of K items from a stream of unknown or extremely 
// large size N in a single pass. Guarantees that every item has an equal 
// probability (K/N) of being included in the final sample. Zero mock.

use rand::Rng;

pub struct OmniReservoirSampler<T> {
    capacity: usize,
    items_seen: usize,
    reservoir: Vec<T>,
}

impl<T> OmniReservoirSampler<T> {
    /// Creates a new Reservoir Sampler that will hold exactly `capacity` items.
    pub fn new(capacity: usize) -> Self {
        assert!(capacity > 0, "Capacity must be greater than 0");
        OmniReservoirSampler {
            capacity,
            items_seen: 0,
            reservoir: Vec::with_capacity(capacity),
        }
    }

    /// Feeds a new item from the stream into the sampler.
    pub fn add(&mut self, item: T) {
        self.items_seen += 1;

        // If the reservoir isn't full, just add the item
        if self.reservoir.len() < self.capacity {
            self.reservoir.push(item);
        } else {
            // Randomly decide whether to replace an existing item
            // Probability of inclusion is K / N
            let mut rng = rand::thread_rng();
            let random_index = rng.gen_range(0..self.items_seen);

            // If the random number is less than capacity, replace that index
            if random_index < self.capacity {
                self.reservoir[random_index] = item;
            }
        }
    }

    /// Feeds a batch of items (iterator) into the sampler.
    pub fn add_batch<I>(&mut self, iter: I) 
    where
        I: IntoIterator<Item = T>,
    {
        for item in iter {
            self.add(item);
        }
    }

    /// Returns the current sample.
    pub fn get_sample(&self) -> &[T] {
        &self.reservoir
    }

    /// Returns the total number of items processed so far.
    pub fn items_processed(&self) -> usize {
        self.items_seen
    }
}
