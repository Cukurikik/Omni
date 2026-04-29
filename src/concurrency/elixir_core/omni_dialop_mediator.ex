# Omni DialOp Mediation Actor (Elixir)
# Ref: jlin816/dialop
defmodule Omni.DialOpMediator do
  def mediate(preferences, n_options) when is_list(preferences) do
    Enum.map(0..(n_options - 1), fn i ->
      scores = Enum.map(preferences, fn p -> Enum.at(p, i, 0) end)
      %{option: i, mean_pref: Enum.sum(scores) / max(length(scores), 1)}
    end)
    |> Enum.sort_by(& &1.mean_pref, :desc)
  end
end
