# Omni MachineSoM Debate Controller (Elixir)
# Concurrency: Actor-based multi-agent debate orchestration.
# Ref: zjunlp/MachineSoM — ACL 2024
defmodule Omni.MachineSoMDebate do
  def run_debate(agents, question, rounds \\ 3) when is_list(agents) do
    Enum.reduce(1..rounds, agents, fn round, positions ->
      avg = Enum.sum(Enum.map(positions, &Map.get(&1, :confidence, 0))) / max(length(positions), 1)
      Enum.map(positions, fn p ->
        new_conf = if p.confidence < avg, do: min(p.confidence * 1.15, 1.0), else: p.confidence
        Map.put(p, :confidence, new_conf) |> Map.put(:round, round)
      end)
    end)
  end
end
