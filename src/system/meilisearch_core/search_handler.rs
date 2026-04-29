use omni_std::result::{Result, Ok, Err};

pub struct SearchHandler;

impl SearchHandler {
    pub fn execute_search(query: &str) -> Result<Vec<String>, String> {
        if query.is_empty() {
            return Err("Search query empty".to_string());
        }
        Ok(vec![])
    }
}
