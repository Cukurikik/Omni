import gleam/list
import gleam/result

pub type PipelineError {
  DataCorruption
  Timeout
}

pub fn transform_stream(
  data: List(Float),
  multiplier: Float,
) -> Result(List(Float), PipelineError) {
  // Pure functional transformation pipeline
  let processed = 
    data
    |> list.map(fn(x) { x *. multiplier })
    |> list.filter(fn(x) { x >. 0.0 })
    
  case list.is_empty(processed) {
    True -> Error(DataCorruption)
    False -> Ok(processed)
  }
}
