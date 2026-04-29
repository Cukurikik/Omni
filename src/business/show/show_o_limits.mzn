int: max_tokens = 8192;
var 0..16384: tokens;
constraint tokens <= max_tokens;
solve satisfy;
