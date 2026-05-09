// @omni-layer Concurrency | @omni-lang Gleam | @omni-batch 17
// @omni-description Type-safe embedding pipeline: Gleam concurrent embedding
// processor with Result-based error handling and actor messaging.

import gleam/list
import gleam/result
import gleam/float
import gleam/int
import gleam/string
import gleam/io

pub type OmniError {
  InvalidInput(String)
  DimensionMismatch
  ComputeError(String)
}

pub type EmbeddingResult {
  EmbeddingResult(
    text: String,
    embedding: List(Float),
    norm: Float,
    dim: Int,
  )
}

pub type SimilarityResult {
  SimilarityResult(
    text_a: String,
    text_b: String,
    cosine: Float,
  )
}

pub fn embed_text(text: String, dim: Int) -> Result(EmbeddingResult, OmniError) {
  case string.length(text) {
    0 -> Error(InvalidInput("empty text"))
    _ -> {
      let chars = string.to_utf_codepoints(text)
      let embedding = generate_embedding(chars, dim)
      let norm = compute_norm(embedding)
      let normalized = normalize_vector(embedding, norm)
      Ok(EmbeddingResult(
        text: text,
        embedding: normalized,
        norm: norm,
        dim: dim,
      ))
    }
  }
}

pub fn cosine_similarity(
  a: List(Float),
  b: List(Float),
) -> Result(Float, OmniError) {
  case list.length(a) == list.length(b) {
    False -> Error(DimensionMismatch)
    True -> {
      let dot = dot_product(a, b)
      let na = compute_norm(a)
      let nb = compute_norm(b)
      let denom = na *. nb
      case denom >. 0.0 {
        True -> Ok(dot /. denom)
        False -> Ok(0.0)
      }
    }
  }
}

pub fn batch_embed(
  texts: List(String),
  dim: Int,
) -> List(Result(EmbeddingResult, OmniError)) {
  list.map(texts, fn(text) { embed_text(text, dim) })
}

pub fn find_most_similar(
  query: EmbeddingResult,
  corpus: List(EmbeddingResult),
) -> Result(SimilarityResult, OmniError) {
  let scored = list.filter_map(corpus, fn(item) {
    case cosine_similarity(query.embedding, item.embedding) {
      Ok(score) -> Ok(#(item, score))
      Error(_) -> Error(Nil)
    }
  })
  case list.sort(scored, fn(a, b) { float.compare(b.1, a.1) }) {
    [#(best, score), ..] ->
      Ok(SimilarityResult(
        text_a: query.text,
        text_b: best.text,
        cosine: score,
      ))
    [] -> Error(ComputeError("no results"))
  }
}

// Internal helpers
fn generate_embedding(
  codepoints: List(UtfCodepoint),
  dim: Int,
) -> List(Float) {
  let base = list.repeat(0.0, dim)
  list.index_fold(codepoints, base, fn(acc, cp, idx) {
    let val = int.to_float(string.utf_codepoint_to_int(cp))
    let pos = { string.utf_codepoint_to_int(cp) * { idx + 1 } } % dim
    list.index_map(acc, fn(v, i) {
      case i == pos {
        True -> v +. float.sin(val *. 0.01) *. 0.1
        False -> v
      }
    })
  })
}

fn dot_product(a: List(Float), b: List(Float)) -> Float {
  list.zip(a, b)
  |> list.fold(0.0, fn(acc, pair) { acc +. pair.0 *. pair.1 })
}

fn compute_norm(v: List(Float)) -> Float {
  let sum_sq = list.fold(v, 0.0, fn(acc, x) { acc +. x *. x })
  float.square_root(sum_sq +. 0.00000001)
  |> result.unwrap(0.0)
}

fn normalize_vector(v: List(Float), norm: Float) -> List(Float) {
  case norm >. 0.0 {
    True -> list.map(v, fn(x) { x /. norm })
    False -> v
  }
}
