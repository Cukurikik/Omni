% MiniRAG resource usage constraints
int: max_ram_mb = 4096;
var 0..8192: current_usage;
constraint current_usage <= max_ram_mb;
solve satisfy;
