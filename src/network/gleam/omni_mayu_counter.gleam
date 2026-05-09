// OMNI MOTHER: Mayu Gleam Hit Counter
// Gleam Functional implementation of Moe-Counter

import gleam/int
import gleam/string
import gleam/io

pub type CounterState {
  CounterState(hits: Int, theme: String)
}

pub fn increment_counter(state: CounterState) -> CounterState {
  CounterState(hits: state.hits + 1, theme: state.theme)
}

pub fn render_svg(state: CounterState) -> String {
  let hits_str = int.to_string(state.hits)
  io.print("[OMNI Gleam] Rendering SVG counter: " <> hits_str <> "\n")
  "<svg> ... [Kawaii Counter: " <> hits_str <> "] ... </svg>"
}
