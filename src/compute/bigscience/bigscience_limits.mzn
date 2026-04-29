% OMNI MiniZinc Constraint Model for BigScience Data Prep
% Enforces mathematical bounds on chunking and deduplication

% Parameters
int: MAX_RAM_MB;
int: WORKER_COUNT;
int: TOTAL_DATASET_MB;

% Variables
var 10..1024: chunk_size_mb; % Chunk size must be between 10MB and 1024MB
var 1..WORKER_COUNT: active_workers;

% Constraints
% 1. Memory constraint: Total memory used by active workers cannot exceed Max RAM
constraint (chunk_size_mb * active_workers * 2) <= MAX_RAM_MB; % * 2 for overhead

% 2. Efficiency constraint: Use at least half the workers if data is large enough
constraint (TOTAL_DATASET_MB > chunk_size_mb * WORKER_COUNT) -> (active_workers >= WORKER_COUNT div 2);

% 3. Coverage constraint: Ensure active workers can process data efficiently
constraint active_workers * chunk_size_mb >= min(TOTAL_DATASET_MB, MAX_RAM_MB div 4);

% Objective: Maximize chunk size to reduce hashing overhead, 
% while staying within safe memory bounds
solve maximize chunk_size_mb;

% Default safe output format for OMNI parser
output [
    "OMNI_OPTIMAL_CHUNK_MB=", show(chunk_size_mb), "\n",
    "OMNI_ACTIVE_WORKERS=", show(active_workers), "\n"
];
