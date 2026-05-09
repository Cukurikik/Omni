// moe_grpc_client.rs — Network / Gateway Client
// Layer: Network / RPC — MoE Inference Client
//
// High-performance Rust gRPC client for MoE token transmission.
// Used by application servers (e.g., Rust backends) to stream tokens
// to the MoE serving gateways efficiently via HTTP/2 multiplexing.

use std::sync::Arc;
use tonic::{transport::Channel, Request};
use tokio::sync::mpsc;
use tokio_stream::wrappers::ReceiverStream;

// Mock generated Protobuf definitions
pub mod pb {
    #[derive(Clone, PartialEq, ::prost::Message)]
    pub struct TokenBatch {
        #[prost(string, tag="1")]
        pub trace_id: String,
        #[prost(float, repeated, tag="2")]
        pub embeddings: Vec<f32>,
        #[prost(int32, tag="3")]
        pub dim: i32,
        #[prost(int32, tag="4")]
        pub token_count: i32,
    }

    #[derive(Clone, PartialEq, ::prost::Message)]
    pub struct InferenceResult {
        #[prost(float, repeated, tag="1")]
        pub outputs: Vec<f32>,
        #[prost(int32, tag="2")]
        pub status_code: i32,
    }

    // Mock client stub
    pub struct MoEGatewayClient {
        channel: Channel,
    }
    
    impl MoEGatewayClient {
        pub fn new(channel: Channel) -> Self { Self { channel } }
        pub async fn connect(dst: String) -> Result<Self, String> { Ok(Self { channel: Channel::from_shared(dst).unwrap().connect().await.unwrap() }) }
        pub async fn stream_inference(&mut self, request: Request<ReceiverStream<TokenBatch>>) -> Result<tonic::Response<InferenceResult>, tonic::Status> {
            // Mock
            Ok(tonic::Response::new(InferenceResult { outputs: vec![], status_code: 200 }))
        }
    }
}

pub struct MoEGrpcClient {
    client: pb::MoEGatewayClient,
}

impl MoEGrpcClient {
    pub async fn connect(endpoint: &str) -> Result<Self, String> {
        let channel = Channel::from_shared(endpoint.to_string())
            .map_err(|e| e.to_string())?
            .connect()
            .await
            .map_err(|e| e.to_string())?;

        Ok(Self {
            client: pb::MoEGatewayClient::new(channel),
        })
    }

    /// Streams a large batch of tokens to the MoE gateway to avoid single massive requests.
    pub async fn stream_tokens(
        &mut self,
        trace_id: String,
        embeddings: Vec<f32>,
        dim: usize,
        chunk_size: usize,
    ) -> Result<Vec<f32>, String> {
        
        let total_tokens = embeddings.len() / dim;
        let (tx, rx) = mpsc::channel(32);

        // Background task to chunk and send data
        let trace_clone = trace_id.clone();
        tokio::spawn(async move {
            let mut offset = 0;
            while offset < embeddings.len() {
                let end = std::cmp::min(offset + (chunk_size * dim), embeddings.len());
                let chunk = embeddings[offset..end].to_vec();
                let token_count = (end - offset) / dim;

                let batch = pb::TokenBatch {
                    trace_id: trace_clone.clone(),
                    embeddings: chunk,
                    dim: dim as i32,
                    token_count: token_count as i32,
                };

                if tx.send(batch).await.is_err() {
                    break; // Receiver dropped
                }
                offset = end;
            }
        });

        let request = Request::new(ReceiverStream::new(rx));
        
        let response = self.client.stream_inference(request).await.map_err(|e| e.to_string())?;
        let result = response.into_inner();

        if result.status_code != 200 {
            return Err(format!("Gateway returned error code: {}", result.status_code));
        }

        Ok(result.outputs)
    }
}
