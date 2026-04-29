# Omni DMax Parallel Scheduler (Elixir)
# Ref: czg1225/DMax
defmodule Omni.DMaxScheduler do
  def schedule(step, total, base \\ 4) do
    progress = step / max(total, 1)
    cond do
      progress < 0.3 -> min(base * 2, 16)
      progress < 0.7 -> base
      true -> max(div(base, 2), 1)
    end
  end
  def batch_schedule(steps, total, base \\ 4) when is_list(steps) do
    Enum.map(steps, &schedule(&1, total, base))
  end
end
