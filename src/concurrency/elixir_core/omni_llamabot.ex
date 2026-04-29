# Omni LlamaBot Actor (Elixir)
defmodule Omni.LlamaBot do
  def build_context(system, history, max_turns \\ 10) do
    turns = Enum.take(history, -max_turns)
    formatted = Enum.map(turns, fn %{role: r, content: c} -> "#{r}: #{c}" end)
    "#{system}\n#{Enum.join(formatted, "\n")}"
  end
  def token_estimate(messages) do
    Enum.reduce(messages, 0, fn %{content: c}, acc -> acc + length(String.split(c)) end)
  end
end
