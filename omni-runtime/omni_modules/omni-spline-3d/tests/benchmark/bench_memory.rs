// Benchmark: ArenaPool alloc speed
#[bench] fn bench_arena_alloc(b: &mut Bencher) {
    let pool = ArenaPool::new(1048576).unwrap();
    b.iter(|| { pool.alloc(64).unwrap(); pool.reset(); });
}