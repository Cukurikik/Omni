# Omni MultiToken Projection Actor (Elixir)
defmodule Omni.MultiToken do
  def cosine_similarity(a, b) do
    dot = Enum.zip(a, b) |> Enum.map(fn {x, y} -> x * y end) |> Enum.sum()
    na = :math.sqrt(Enum.map(a, &(&1 * &1)) |> Enum.sum()) |> max(1.0e-8)
    nb = :math.sqrt(Enum.map(b, &(&1 * &1)) |> Enum.sum()) |> max(1.0e-8)
    Float.round(dot / (na * nb), 4)
  end
  def expand(embedding, n_tokens) do
    chunk = max(div(length(embedding), n_tokens), 1)
    Enum.chunk_every(embedding, chunk)
  end
end
