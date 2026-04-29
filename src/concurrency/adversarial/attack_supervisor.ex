defmodule OmniConcurrency.Adversarial.AttackSupervisor do
  @moduledoc """
  OMNI CONCURRENCY LAYER: Adversarial
  Supervisor for distributing parallel adversarial attacks (PGD, FGSM, CW) across nodes.
  """
  use Task.Supervisor

  def start_link(opts) do
    Task.Supervisor.start_link(__MODULE__, opts)
  end

  def execute_attack_batch(supervisor, image_batch, attack_type) do
    # Monadic Result pattern matching in Elixir
    try do
      tasks = Enum.map(image_batch, fn img ->
        Task.Supervisor.async(supervisor, fn ->
          run_attack(img, attack_type)
        end)
      end)

      results = Task.await_many(tasks, 60_000)
      {:ok, results}
    rescue
      e -> {:error, "Supervision failed: #{Exception.message(e)}"}
    end
  end

  defp run_attack(img, type) do
    # Bridge call to Python Compute layer
    OmniBridge.Python.call("adversarial_attack_generator", "generate_#{type}", [img])
  end
end
