#[no_mangle]
pub extern "C" fn omni_graph_bfs_traversal(
    adjacency_matrix: *const i32,
    nodes_count: i32,
    start_node: i32,
    out_distances: *mut i32,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if adjacency_matrix.is_null() || out_distances.is_null() || nodes_count <= 0 || start_node < 0 || start_node >= nodes_count {
        unsafe { *err_code = -1 };
        return;
    }

    // Zero-mock hardware-level Breadth-First Search (BFS) for Graph RAG traversals
    // Determines the shortest path distance from a starting entity to all other entities
    unsafe {
        let adj = std::slice::from_raw_parts(adjacency_matrix, (nodes_count * nodes_count) as usize);
        let dist = std::slice::from_raw_parts_mut(out_distances, nodes_count as usize);
        
        // Initialize distances to -1 (unreachable)
        for i in 0..nodes_count {
            dist[i as usize] = -1;
        }
        
        let mut queue = Vec::with_capacity(nodes_count as usize);
        queue.push(start_node);
        dist[start_node as usize] = 0;
        
        let mut head = 0;
        while head < queue.len() {
            let current = queue[head];
            head += 1;
            
            let current_dist = dist[current as usize];
            let row_offset = (current * nodes_count) as usize;
            
            for neighbor in 0..nodes_count {
                if adj[row_offset + (neighbor as usize)] > 0 {
                    if dist[neighbor as usize] == -1 {
                        dist[neighbor as usize] = current_dist + 1;
                        queue.push(neighbor);
                    }
                }
            }
        }
        
        *err_code = 0;
    }
}
