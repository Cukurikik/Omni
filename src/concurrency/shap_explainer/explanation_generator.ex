defmodule Omni.Concurrency.ShapExplainer.Generator do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  def compute_explanations(pid, instance_id, num_features) do
    GenServer.cast(pid, {:compute, instance_id, num_features})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:compute, instance_id, num_features}, state) do
    IO.puts("SHAP Generator: Computing Shapley values for Instance [#{instance_id}] with #{num_features} features in background...")
    
    # Simulate async compute deterministically
    Process.send_after(self(), {:done, instance_id}, 150)
    
    {:noreply, state}
  end

  @impl true
  def handle_info({:done, instance_id}, state) do
    IO.puts("SHAP Generator: Explanations ready for Instance [#{instance_id}].")
    {:noreply, state}
  end
end
