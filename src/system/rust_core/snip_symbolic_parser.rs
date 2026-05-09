/// OMNI SNIP Symbolic Parser
/// Parses LaTeX math expressions into semantic syntax trees.

#[derive(Debug, PartialEq)]
pub enum MathNode {
    Number(f64),
    Variable(String),
    Add(Box<MathNode>, Box<MathNode>),
    Mul(Box<MathNode>, Box<MathNode>),
}

pub struct SnipSymbolicParser {
    strict_mode: bool,
}

impl SnipSymbolicParser {
    pub fn new(strict_mode: bool) -> Self {
        Self { strict_mode }
    }

    pub fn parse(&self, expression: &str) -> Result<MathNode, &'static str> {
        if expression.is_empty() {
            return Err("Expression is empty");
        }

        // Extremely simplified parser for Zero-Mock demonstration
        if expression.contains("+") {
            let parts: Vec<&str> = expression.splitn(2, '+').collect();
            Ok(MathNode::Add(
                Box::new(self.parse(parts[0].trim())?),
                Box::new(self.parse(parts[1].trim())?),
            ))
        } else if expression.contains("*") {
            let parts: Vec<&str> = expression.splitn(2, '*').collect();
            Ok(MathNode::Mul(
                Box::new(self.parse(parts[0].trim())?),
                Box::new(self.parse(parts[1].trim())?),
            ))
        } else if let Ok(num) = expression.parse::<f64>() {
            Ok(MathNode::Number(num))
        } else {
            Ok(MathNode::Variable(expression.to_string()))
        }
    }
}
