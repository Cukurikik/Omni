# Omni CAMEL Consensus Actor (Elixir)
# Ref: camel-ai/multi-agent-streamlit-ui
defmodule Omni.CamelConsensus do
  def check(responses) when is_list(responses) do
    unique = responses |> Enum.map(&String.trim/1) |> Enum.map(&String.downcase/1) |> Enum.uniq()
    agreement = 1.0 - (length(unique) - 1) / max(length(responses), 1)
    %{agreement: Float.round(agreement, 4), consensus: agreement > 0.6, unique: length(unique)}
  end
end
