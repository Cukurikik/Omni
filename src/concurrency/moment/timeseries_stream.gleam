import gleam/result

pub type OmniResult(t) {
  Ok(t)
  Error(String)
}

pub fn stream_time_series(data: List(Float)) -> OmniResult(Int) {
  case data {
    [] -> Error("Empty time series data")
    _ -> {
      // Simulate Erlang OTP stream dispatch math
      let count = gleam/list.length(data)
      Ok(count)
    }
  }
}
