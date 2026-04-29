# Omni Lion Distillation Consensus Actor (Elixir)
# Ref: YJiangcm/Lion — EMNLP 2023
defmodule Omni.LionDistillation do
  def discriminate(student_scores, teacher_scores, threshold \\ 0.3) do
    student_scores
    |> Enum.zip(teacher_scores)
    |> Enum.with_index()
    |> Enum.filter(fn {{s, t}, _i} -> t - s > threshold end)
    |> Enum.map(fn {_, i} -> i end)
  end

  def distillation_stats(student_acc, teacher_acc) do
    improvement = List.last(student_acc) - List.first(student_acc)
    gap = List.last(teacher_acc) - List.last(student_acc)
    %{improvement: Float.round(improvement, 4), final_gap: Float.round(gap, 4),
      iterations: length(student_acc)}
  end
end
