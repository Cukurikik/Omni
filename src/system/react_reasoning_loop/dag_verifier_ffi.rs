#[no_mangle]
pub extern "C" fn omni_verify_dag_acyclic(
    edges_from: *const i32,
    edges_to: *const i32,
    edges_count: i32,
    nodes_count: i32,
    out_is_acyclic: *mut i32,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if edges_from.is_null() || edges_to.is_null() || out_is_acyclic.is_null() || nodes_count <= 0 {
        unsafe { *err_code = -1 };
        return;
    }

    // Zero-mock hardware-level execution of DAG validation
    // Ensures the agent's thought graph does not contain infinite recursive loops
    unsafe {
        let from = std::slice::from_raw_parts(edges_from, edges_count as usize);
        let to = std::slice::from_raw_parts(edges_to, edges_count as usize);
        
        // Build adjacency list
        let mut adj: Vec<Vec<i32>> = vec![Vec::new(); nodes_count as usize];
        for i in 0..edges_count as usize {
            if from[i] >= 0 && from[i] < nodes_count && to[i] >= 0 && to[i] < nodes_count {
                adj[from[i] as usize].push(to[i]);
            }
        }
        
        let mut visited = vec![0; nodes_count as usize]; // 0: unvisited, 1: visiting, 2: visited
        let mut has_cycle = false;
        
        for i in 0..nodes_count as usize {
            if visited[i] == 0 {
                if check_cycle(&adj, i, &mut visited) {
                    has_cycle = true;
                    break;
                }
            }
        }
        
        *out_is_acyclic = if has_cycle { 0 } else { 1 };
        *err_code = 0;
    }
}

fn check_cycle(adj: &Vec<Vec<i32>>, curr: usize, visited: &mut Vec<i32>) -> bool {
    visited[curr] = 1;
    
    for &neighbor in &adj[curr] {
        let n = neighbor as usize;
        if visited[n] == 1 {
            return true; // Cycle detected
        } else if visited[n] == 0 {
            if check_cycle(adj, n, visited) {
                return true;
            }
        }
    }
    
    visited[curr] = 2;
    false
}
