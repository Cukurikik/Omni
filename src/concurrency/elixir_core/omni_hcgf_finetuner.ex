# Omni HCGF Fine-Tuning Actor (Elixir)
# Ref: hscspring/hcgf — Apache-2.0
defmodule Omni.HCGFFinetuner do
  def gradient_checkpoint_partition(n_layers, n_checkpoints) do
    chunk_size = max(div(n_layers, n_checkpoints), 1)
    0..(n_layers - 1)
    |> Enum.chunk_every(chunk_size)
    |> Enum.map(&Enum.to_list/1)
  end

  def lora_scale(alpha, rank) do
    alpha / max(rank, 1)
  end

  def training_step_stats(loss_history) do
    avg = Enum.sum(loss_history) / max(length(loss_history), 1)
    best = Enum.min(loss_history)
    %{avg_loss: Float.round(avg, 6), best_loss: Float.round(best, 6),
      steps: length(loss_history)}
  end
end
