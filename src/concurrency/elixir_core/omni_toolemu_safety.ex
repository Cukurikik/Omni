# Omni ToolEmu Safety Actor (Elixir)
defmodule Omni.ToolEmuSafety do
  @dangerous %{"delete" => 0.9, "write" => 0.6, "execute" => 0.8, "send" => 0.5}
  def assess(action, args) do
    action_lower = String.downcase(action)
    {score, flags} = Enum.reduce(@dangerous, {0.0, []}, fn {da, w}, {s, f} ->
      if String.contains?(action_lower, da), do: {max(s, w), [da | f]}, else: {s, f}
    end)
    level = cond do; score > 0.7 -> "critical"; score > 0.4 -> "high"; true -> "low"; end
    %{score: Float.round(score, 4), level: level, flags: flags}
  end
end
