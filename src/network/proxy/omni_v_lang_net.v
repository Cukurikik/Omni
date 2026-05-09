module omni_v_router

import net
import io
import time

// Omni V-Lang Network Router (V)
// Network & Routing Layer
// Ultra-fast, C-like but memory-safe proxy router handling raw socket 
// connections and directing them to specific Omni nodes.

const (
    port = 8080
    buffer_size = 4096
)

struct RouterNode {
    id string
    address string
}

fn handle_client(mut client net.TcpConn, target_node RouterNode) {
    defer { client.close() or { } }

    // Connect to the internal Omni worker node
    mut backend := net.dial_tcp(target_node.address) or {
        println('Failed to connect to backend: ${err}')
        return
    }
    defer { backend.close() or { } }

    // Bidirectional raw socket streaming (Proxy)
    mut buf := []u8{len: buffer_size}
    
    for {
        read_bytes := client.read(mut buf) or { break }
        if read_bytes == 0 { break }

        backend.write(buf[..read_bytes]) or { break }
        
        mut back_buf := []u8{len: buffer_size}
        back_read := backend.read(mut back_buf) or { break }
        if back_read == 0 { break }
        
        client.write(back_buf[..back_read]) or { break }
    }
}

pub fn start_router() ! {
    mut listener := net.listen_tcp(port)!
    println('Omni V-Lang Router listening on :${port}')

    // Round-robin nodes (simulated cluster registry)
    nodes := [
        RouterNode{id: 'node_1', address: '10.0.1.5:50051'},
        RouterNode{id: 'node_2', address: '10.0.1.6:50051'}
    ]
    mut rr_index := 0

    for {
        mut client := listener.accept() or {
            println('Accept error: ${err}')
            continue
        }
        
        // Select target node
        target := nodes[rr_index % nodes.len]
        rr_index++

        // Spawn lightweight thread (coroutine)
        go handle_client(mut client, target)
    }
}
