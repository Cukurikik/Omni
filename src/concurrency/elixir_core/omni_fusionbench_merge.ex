# Omni FusionBench Model Merge Actor (Elixir)
# Ref: tanganke/fusion_bench — MIT
defmodule Omni.FusionBenchMerge do
  def task_arithmetic(base, deltas, scaling \\ 0.3) do
    base
    |> Enum.with_index()
    |> Enum.map(fn {b, i} ->
      total = deltas |> Enum.map(fn d -> Enum.at(d, i, 0) - b end) |> Enum.sum()
      Float.round(b + scaling * total, 8)
    end)
  end

  def dare_prune(delta, drop_rate \\ 0.9, seed \\ 42) do
    delta
    |> Enum.with_index()
    |> Enum.map(fn {d, i} ->
      h = rem(seed * (i + 1) * 2654435761, 100)
      if h < round(drop_rate * 100), do: 0.0, else: d / max(1 - drop_rate, 0.01)
    end)
  end
end
