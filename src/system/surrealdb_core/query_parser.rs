use omni_std::result::{Result, Ok, Err};

pub struct QueryParser;

impl QueryParser {
    pub fn parse(query: &str) -> Result<String, String> {
        if query.is_empty() {
            return Err("Empty query".to_string());
        }
        Ok("Parsed_AST".to_string())
    }
}
