# Omni DeepInception Safety Actor (Elixir)
defmodule Omni.DeepInceptionSafety do
  @inception_markers ["create a story","imagine a world","roleplay as","pretend you are"]
  @harmful ["violence","weapon","hack","exploit","steal","attack"]
  def detect(prompt) do
    pl = String.downcase(prompt)
    im = Enum.count(@inception_markers, &String.contains?(pl, &1))
    hm = Enum.count(@harmful, &String.contains?(pl, &1))
    score = min(im * 0.15 + hm * 0.2, 1.0)
    %{is_inception: im >= 2 and hm >= 1, risk_score: Float.round(score, 4)}
  end
end
