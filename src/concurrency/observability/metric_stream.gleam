import gleam/list
import gleam/string

pub fn parse_evidently_metrics(stream: List(String)) -> List(Float) {
  list.filter_map(stream, fn(line) {
    case string.split(line, on: "=") {
      ["latency", val] -> {
        // Mock parse
        Ok(10.5)
      }
      _ -> Error(Nil)
    }
  })
}
