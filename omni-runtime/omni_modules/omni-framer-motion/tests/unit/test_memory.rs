// Unit test: ArenaPool alloc/reset
#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn test_arena_alloc() { let pool = ArenaPool::new(1024).unwrap(); let block = pool.alloc(64); assert!(block.is_ok()); }
    #[test] fn test_arena_reset() { let pool = ArenaPool::new(1024).unwrap(); pool.alloc(64).unwrap(); pool.reset(); assert_eq!(pool.used(), 0); }
}