# Omni Confucius Dispatcher (Elixir)
# Concurrency Layer: Actor-based curriculum scheduling for tool learning.
# Ref: mangopy/Confucius-tool-learning — AAAI 2024

defmodule Omni.ConfuciusDispatcher do
  def schedule_curriculum(tools, mastered) when is_list(tools) and is_list(mastered) do
    mastered_set = MapSet.new(mastered)
    tools
    |> Enum.filter(fn t -> not MapSet.member?(mastered_set, t) end)
    |> Enum.sort_by(fn t -> byte_size(t) end)
  end

  def compute_mastery(%{successes: s, attempts: a}) when a > 0, do: Float.round(s / a, 6)
  def compute_mastery(_), do: 0.0
end
