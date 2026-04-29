// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Argo Workflows DAG Engine (OMNI Zero-Mock Implementation)
// Implements Topological Sort logic mathematically for Job Scheduling.

package argo

import (
    "errors"
)

type Result[T any] struct {
    Value T
    Error error
    IsOk  bool
}

func Ok[T any](val T) Result[T] {
    return Result[T]{Value: val, Error: nil, IsOk: true}
}

func Err[T any](err string) Result[T] {
    var zero T
    return Result[T]{Value: zero, Error: errors.New(err), IsOk: false}
}

// Graph adjacency list mapping taskID -> dependencies
type DependencyGraph struct {
    Edges map[string][]string
}

func (g *DependencyGraph) TopologicalSort() Result[[]string] {
    visited := make(map[string]int) // 0: unvisited, 1: visiting, 2: visited
    stack := []string{}
    
    var dfs func(node string) bool
    dfs = func(node string) bool {
        if visited[node] == 1 {
            return false // Cycle detected
        }
        if visited[node] == 2 {
            return true
        }
        
        visited[node] = 1
        for _, dep := range g.Edges[node] {
            if !dfs(dep) {
                return false
            }
        }
        visited[node] = 2
        stack = append(stack, node)
        return true
    }
    
    for node := range g.Edges {
        if visited[node] == 0 {
            if !dfs(node) {
                return Err[[]string]("Cycle detected in DAG. Invalid workflow.")
            }
        }
    }
    
    return Ok(stack)
}
