// omni_onnx_exporter.rs — ONNX Model Export Engine
// Inspired by: PyTorch ONNX export + OMNI deployment pipeline
// Layer: System / Rust
//
// Constructs ONNX computation graphs from OMNI model definitions
// for cross-platform inference deployment.

use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq)]
pub enum DataType {
    Float32,
    Float16,
    Int32,
    Int64,
    Bool,
    String,
}

impl DataType {
    pub fn onnx_type_id(&self) -> i32 {
        match self {
            DataType::Float32 => 1,
            DataType::Float16 => 10,
            DataType::Int32 => 6,
            DataType::Int64 => 7,
            DataType::Bool => 9,
            DataType::String => 8,
        }
    }

    pub fn byte_size(&self) -> usize {
        match self {
            DataType::Float32 => 4,
            DataType::Float16 => 2,
            DataType::Int32 => 4,
            DataType::Int64 => 8,
            DataType::Bool => 1,
            DataType::String => 0,
        }
    }
}

#[derive(Debug, Clone)]
pub struct TensorShape {
    pub dims: Vec<i64>,
    pub dtype: DataType,
}

impl TensorShape {
    pub fn new(dims: Vec<i64>, dtype: DataType) -> Self {
        Self { dims, dtype }
    }

    pub fn numel(&self) -> i64 {
        self.dims.iter().product()
    }

    pub fn with_dynamic_batch(mut self) -> Self {
        if !self.dims.is_empty() {
            self.dims[0] = -1; // Dynamic batch dimension
        }
        self
    }
}

#[derive(Debug, Clone)]
pub struct OnnxAttribute {
    pub name: String,
    pub value: AttributeValue,
}

#[derive(Debug, Clone)]
pub enum AttributeValue {
    Int(i64),
    Float(f64),
    String(String),
    Ints(Vec<i64>),
    Floats(Vec<f64>),
}

#[derive(Debug, Clone)]
pub struct OnnxNode {
    pub op_type: String,
    pub name: String,
    pub inputs: Vec<String>,
    pub outputs: Vec<String>,
    pub attributes: Vec<OnnxAttribute>,
    pub domain: String,
}

impl OnnxNode {
    pub fn new(op_type: &str, name: &str) -> Self {
        Self {
            op_type: op_type.to_string(),
            name: name.to_string(),
            inputs: Vec::new(),
            outputs: Vec::new(),
            attributes: Vec::new(),
            domain: String::new(),
        }
    }

    pub fn with_inputs(mut self, inputs: Vec<&str>) -> Self {
        self.inputs = inputs.into_iter().map(String::from).collect();
        self
    }

    pub fn with_outputs(mut self, outputs: Vec<&str>) -> Self {
        self.outputs = outputs.into_iter().map(String::from).collect();
        self
    }

    pub fn with_attr_int(mut self, name: &str, value: i64) -> Self {
        self.attributes.push(OnnxAttribute {
            name: name.to_string(),
            value: AttributeValue::Int(value),
        });
        self
    }

    pub fn with_attr_float(mut self, name: &str, value: f64) -> Self {
        self.attributes.push(OnnxAttribute {
            name: name.to_string(),
            value: AttributeValue::Float(value),
        });
        self
    }

    pub fn with_attr_ints(mut self, name: &str, values: Vec<i64>) -> Self {
        self.attributes.push(OnnxAttribute {
            name: name.to_string(),
            value: AttributeValue::Ints(values),
        });
        self
    }
}

#[derive(Debug, Clone)]
pub struct OnnxInitializer {
    pub name: String,
    pub shape: TensorShape,
    pub data: Vec<u8>,
}

#[derive(Debug)]
pub struct OnnxGraph {
    pub name: String,
    pub nodes: Vec<OnnxNode>,
    pub inputs: Vec<(String, TensorShape)>,
    pub outputs: Vec<(String, TensorShape)>,
    pub initializers: Vec<OnnxInitializer>,
    opset_version: i64,
}

impl OnnxGraph {
    pub fn new(name: &str, opset_version: i64) -> Self {
        Self {
            name: name.to_string(),
            nodes: Vec::new(),
            inputs: Vec::new(),
            outputs: Vec::new(),
            initializers: Vec::new(),
            opset_version,
        }
    }

    pub fn add_input(&mut self, name: &str, shape: TensorShape) {
        self.inputs.push((name.to_string(), shape));
    }

    pub fn add_output(&mut self, name: &str, shape: TensorShape) {
        self.outputs.push((name.to_string(), shape));
    }

    pub fn add_node(&mut self, node: OnnxNode) {
        self.nodes.push(node);
    }

    pub fn add_initializer(&mut self, init: OnnxInitializer) {
        self.initializers.push(init);
    }

    pub fn validate(&self) -> Result<(), Vec<String>> {
        let mut errors = Vec::new();

        // Check all node inputs are defined
        let mut defined_names: std::collections::HashSet<String> = std::collections::HashSet::new();
        for (name, _) in &self.inputs {
            defined_names.insert(name.clone());
        }
        for init in &self.initializers {
            defined_names.insert(init.name.clone());
        }

        for node in &self.nodes {
            for input in &node.inputs {
                if !input.is_empty() && !defined_names.contains(input) {
                    errors.push(format!("Node '{}': undefined input '{}'", node.name, input));
                }
            }
            for output in &node.outputs {
                defined_names.insert(output.clone());
            }
        }

        // Check outputs are defined
        for (name, _) in &self.outputs {
            if !defined_names.contains(name) {
                errors.push(format!("Graph output '{}' is not produced by any node", name));
            }
        }

        if errors.is_empty() { Ok(()) } else { Err(errors) }
    }

    pub fn node_count(&self) -> usize {
        self.nodes.len()
    }

    pub fn parameter_count(&self) -> i64 {
        self.initializers.iter()
            .map(|init| init.shape.numel())
            .sum()
    }
}

/// Helper to build common transformer ONNX subgraphs
pub struct TransformerGraphBuilder {
    graph: OnnxGraph,
    node_counter: usize,
}

impl TransformerGraphBuilder {
    pub fn new(name: &str, dim: i64, heads: i64, max_seq: i64) -> Self {
        let mut graph = OnnxGraph::new(name, 17); // ONNX opset 17

        graph.add_input("input_ids",
            TensorShape::new(vec![-1, max_seq], DataType::Int64));
        graph.add_input("attention_mask",
            TensorShape::new(vec![-1, max_seq], DataType::Float32));

        Self { graph, node_counter: 0 }
    }

    fn next_name(&mut self, prefix: &str) -> String {
        self.node_counter += 1;
        format!("{}_{}", prefix, self.node_counter)
    }

    pub fn add_layer_norm(&mut self, input: &str, output: &str, dim: i64) {
        let name = self.next_name("layer_norm");
        let scale_name = format!("{}_scale", name);
        let bias_name = format!("{}_bias", name);

        self.graph.add_node(
            OnnxNode::new("LayerNormalization", &name)
                .with_inputs(vec![input, &scale_name, &bias_name])
                .with_outputs(vec![output])
                .with_attr_float("epsilon", 1e-5)
                .with_attr_int("axis", -1)
        );
    }

    pub fn add_matmul(&mut self, input_a: &str, input_b: &str, output: &str) {
        let name = self.next_name("matmul");
        self.graph.add_node(
            OnnxNode::new("MatMul", &name)
                .with_inputs(vec![input_a, input_b])
                .with_outputs(vec![output])
        );
    }

    pub fn add_gelu(&mut self, input: &str, output: &str) {
        let name = self.next_name("gelu");
        self.graph.add_node(
            OnnxNode::new("Gelu", &name)
                .with_inputs(vec![input])
                .with_outputs(vec![output])
        );
    }

    pub fn add_softmax(&mut self, input: &str, output: &str, axis: i64) {
        let name = self.next_name("softmax");
        self.graph.add_node(
            OnnxNode::new("Softmax", &name)
                .with_inputs(vec![input])
                .with_outputs(vec![output])
                .with_attr_int("axis", axis)
        );
    }

    pub fn add_residual(&mut self, input_a: &str, input_b: &str, output: &str) {
        let name = self.next_name("add");
        self.graph.add_node(
            OnnxNode::new("Add", &name)
                .with_inputs(vec![input_a, input_b])
                .with_outputs(vec![output])
        );
    }

    pub fn build(self) -> OnnxGraph {
        self.graph
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_graph_construction() {
        let mut builder = TransformerGraphBuilder::new("test_model", 768, 12, 512);
        builder.add_layer_norm("input_ids", "normed", 768);
        builder.add_gelu("normed", "activated");

        let graph = builder.build();
        assert!(graph.node_count() >= 2);
    }

    #[test]
    fn test_tensor_shape() {
        let shape = TensorShape::new(vec![2, 512, 768], DataType::Float32);
        assert_eq!(shape.numel(), 2 * 512 * 768);

        let dynamic = shape.with_dynamic_batch();
        assert_eq!(dynamic.dims[0], -1);
    }
}
