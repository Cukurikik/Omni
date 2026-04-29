// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Kubeflow Pipeline Runner (OMNI Zero-Mock Implementation)
// Implements state machine transition logic for ML execution nodes.

package kubeflow

// State represents the lifecycle state of a pipeline node.
type State int

const (
    Pending State = iota
    Running
    Succeeded
    Failed
    Skipped
)

// PipelineNode represents a single node in the pipeline graph.
type PipelineNode struct {
    ID    string
    State State
}

// TransitionGraph manages the state transitions of pipeline nodes.
type TransitionGraph struct {
    Nodes map[string]*PipelineNode
}

// DispatchNode transitions a node from Pending to Running.
func (g *TransitionGraph) DispatchNode(id string) Result {
    node, exists := g.Nodes[id]
    if !exists {
        return Err("Node does not exist in pipeline.")
    }
    
    if node.State != Pending {
        return Err("Cannot dispatch non-pending node.")
    }
    
    node.State = Running
    return Ok(node.State)
}

// CompleteNode transitions a Running node to Succeeded or Failed.
func (g *TransitionGraph) CompleteNode(id string, success bool) Result {
    node, exists := g.Nodes[id]
    if !exists {
        return Err("Node does not exist in pipeline.")
    }
    
    if node.State != Running {
        return Err("Node must be Running to complete.")
    }
    
    if success {
        node.State = Succeeded
    } else {
        node.State = Failed
    }
    
    return Ok(node.State)
}
