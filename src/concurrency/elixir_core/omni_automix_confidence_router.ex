# Omni AutoMix Confidence Router (Elixir)
# Ref: automix-llm/automix
defmodule Omni.AutoMixRouter do
  def route(sv_score, threshold \\ 0.6) do
    if sv_score >= threshold, do: {:ok, :small_model}, else: {:ok, :large_model}
  end
  def batch_route(scores, threshold \\ 0.6) when is_list(scores) do
    Enum.map(scores, fn s -> route(s, threshold) end)
  end
end
