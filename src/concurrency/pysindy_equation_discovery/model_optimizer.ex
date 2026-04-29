defmodule Omni.Concurrency.PySindyEquationDiscovery.ModelOptimizer do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{iteration: 0, best_model: nil}, name: __MODULE__)
  end

  def optimize_threshold(pid, accuracy, sparsity) do
    GenServer.call(pid, {:optimize, accuracy, sparsity})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:optimize, accuracy, sparsity}, _from, state) do
    # Hyperparameter optimization coordinating parallel SINDy searches
    new_iteration = state.iteration + 1
    
    score = (accuracy * 0.7) + (sparsity * 0.3)
    
    new_state = if state.best_model == nil or score > state.best_model.score do
      %{state | iteration: new_iteration, best_model: %{score: score, threshold: 0.1 * new_iteration}}
    else
      %{state | iteration: new_iteration}
    end
    
    {:reply, :ok, new_state}
  end
end
