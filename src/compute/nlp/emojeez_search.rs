//=============================================================================
// OMNI COMPUTE/SYSTEM LAYER — EMOJEEZ SEMANTIC SEARCH (RUST)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Rust backend for high-speed multi-lingual emoji semantic search.
//              Bridging embeddings to Qdrant vector store.
// INSPIRED BY: badrex/emojeez
//=============================================================================

use std::sync::Arc;
use qdrant_client::prelude::*;
use qdrant_client::qdrant::{Condition, Filter, SearchPoints};

/// OMNI IDIOM: Strict monadic error handling
#[derive(Debug)]
pub enum SearchError {
    VectorDBError(String),
    EmbeddingFailed,
    NoResults,
}

pub type Result<T> = std::result::Result<T, SearchError>;

pub struct EmojeezSearchEngine {
    qdrant_client: Arc<QdrantClient>,
    collection_name: String,
}

impl EmojeezSearchEngine {
    pub async fn new(db_url: &str, collection: &str) -> Result<Self> {
        let client = QdrantClient::from_url(db_url).build()
            .map_err(|e| SearchError::VectorDBError(e.to_string()))?;
            
        Ok(Self {
            qdrant_client: Arc::new(client),
            collection_name: collection.to_string(),
        })
    }

    /// Embeds text and retrieves the top-k semantically related emojis
    pub async fn search_emoji(&self, text_embedding: Vec<f32>, limit: u64, language_filter: Option<&str>) -> Result<Vec<String>> {
        let mut filter = None;
        if let Some(lang) = language_filter {
            filter = Some(Filter::must(vec![
                Condition::matches("language", lang.to_string())
            ]));
        }

        let search_request = SearchPoints {
            collection_name: self.collection_name.clone(),
            vector: text_embedding,
            filter,
            limit,
            with_payload: Some(true.into()),
            ..Default::default()
        };

        let response = self.qdrant_client.search_points(&search_request).await
            .map_err(|e| SearchError::VectorDBError(e.to_string()))?;

        if response.result.is_empty() {
            return Err(SearchError::NoResults);
        }

        let emojis: Vec<String> = response.result.into_iter().filter_map(|point| {
            point.payload.get("emoji").and_then(|val| val.as_str().map(|s| s.to_string()))
        }).collect();

        Ok(emojis)
    }
}
