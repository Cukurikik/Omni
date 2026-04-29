# Omni SimplyRetrieve Retrieval Tuning Actor (Elixir)
# Ref: RCGAI/SimplyRetrieve — MIT
defmodule Omni.SimplyRetrieveTuning do
  def retrieval_f1(retrieved_ids, relevant_ids) do
    hits = Enum.count(retrieved_ids, &MapSet.member?(relevant_ids, &1))
    precision = hits / max(length(retrieved_ids), 1)
    recall = hits / max(MapSet.size(relevant_ids), 1)
    f1 = if precision + recall > 0, do: 2 * precision * recall / (precision + recall), else: 0
    %{precision: Float.round(precision, 4), recall: Float.round(recall, 4), f1: Float.round(f1, 4)}
  end

  def tune_threshold(results, target_recall \\ 0.8) do
    sorted = Enum.sort_by(results, & &1.threshold)
    Enum.find(sorted, List.last(sorted), fn r -> r.recall >= target_recall end)
  end
end
