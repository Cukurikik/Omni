#[cfg(test)]
mod tests {
    use crate::system::llmpowerhouse::inference_engine::CustomInferenceEngine;

    #[test]
    fn test_inference_benchmark() {
        let engine = CustomInferenceEngine { batch_size: 16 };
        let tokens: Vec<u32> = (0..2048).collect();
        
        let res = engine.infer(tokens);
        assert!(res.is_ok);
        assert_eq!(res.value.unwrap().len(), 2048);
    }
}
