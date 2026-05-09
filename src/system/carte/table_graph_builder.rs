/// @omni-layer System | @omni-source soda-inria/carte
/// @omni-description Graph adjacency builder in Rust for tabular data graph
/// construction. Builds column-cell-row edges for CARTE.
/// @omni-lang Rust | @omni-batch 16 | @omni-semester 16

use std::collections::HashMap;

#[derive(Debug)]
pub enum GraphError { EmptyTable, InvalidColumn(String) }
pub type OmniResult<T> = Result<T, GraphError>;

#[derive(Debug, Clone)]
pub struct Edge { pub src: usize, pub dst: usize, pub edge_type: u8 }

pub struct TableGraphBuilder { max_nodes: usize }

impl TableGraphBuilder {
    pub fn new(max_nodes: usize) -> Self { Self { max_nodes } }

    pub fn build_row_graph(&self, n_columns: usize) -> OmniResult<Vec<Edge>> {
        if n_columns == 0 { return Err(GraphError::EmptyTable); }
        let mut edges = Vec::new();
        let row_node = 0usize;
        for col in 0..n_columns {
            let cell_node = col + 1;
            edges.push(Edge { src: row_node, dst: cell_node, edge_type: 0 });
            edges.push(Edge { src: cell_node, dst: row_node, edge_type: 1 });
            if col > 0 {
                edges.push(Edge { src: col, dst: cell_node, edge_type: 2 });
            }
        }
        Ok(edges)
    }

    pub fn build_column_type_edges(&self, col_types: &[&str]) -> OmniResult<Vec<Edge>> {
        if col_types.is_empty() { return Err(GraphError::EmptyTable); }
        let mut type_groups: HashMap<&str, Vec<usize>> = HashMap::new();
        for (i, t) in col_types.iter().enumerate() {
            type_groups.entry(t).or_default().push(i);
        }
        let mut edges = Vec::new();
        for (_, cols) in &type_groups {
            for i in 0..cols.len() {
                for j in (i+1)..cols.len() {
                    edges.push(Edge { src: cols[i], dst: cols[j], edge_type: 3 });
                    edges.push(Edge { src: cols[j], dst: cols[i], edge_type: 3 });
                }
            }
        }
        Ok(edges)
    }

    pub fn adjacency_list(&self, edges: &[Edge], n_nodes: usize) -> Vec<Vec<usize>> {
        let mut adj = vec![Vec::new(); n_nodes];
        for e in edges {
            if e.src < n_nodes && e.dst < n_nodes {
                adj[e.src].push(e.dst);
            }
        }
        adj
    }
}
