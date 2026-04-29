# Omni Confucius Scheduler (Elixir)
# Concurrency Layer: Actor-based GNN task scheduling.
# Ref: WxxShirley/GNN4TaskPlan — NeurIPS 2024
defmodule Omni.GNN4TaskScheduler do
  def schedule(tasks, completed) when is_list(tasks) and is_list(completed) do
    done = MapSet.new(completed)
    tasks
    |> Enum.filter(fn t -> Enum.all?(t.deps, &MapSet.member?(done, &1)) end)
    |> Enum.sort_by(& &1.priority, :desc)
  end
end
