# Omni SelfReflection Controller (Elixir)
# Concurrency Layer: Actor-based LLM self-reflection loop.
# Ref: rxlqn/awesome-llm-self-reflection
defmodule Omni.SelfReflection do
  def reflect(response, criteria) when is_binary(response) and is_list(criteria) do
    scores = Enum.map(criteria, fn c ->
      score = if String.contains?(String.downcase(response), String.downcase(c)), do: 1.0, else: 0.0
      {c, score}
    end)
    avg = Enum.sum(Enum.map(scores, fn {_, s} -> s end)) / max(length(scores), 1)
    %{scores: scores, average: avg, needs_revision: avg < 0.5}
  end
end
