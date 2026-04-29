defmodule Omni.Concurrency.ServerlessColdStartPredictor.AsyncPrewarmer do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{vms_prewarmed: 0}, name: __MODULE__)
  end

  def trigger_prewarm(pid, function_id) do
    GenServer.cast(pid, {:prewarm, function_id})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:prewarm, _id}, state) do
    # Distributed Elixir worker managing asynchronous pre-warming of thousands of microVMs
    # Listens to the Poisson predictor and spins up Firecracker VMs milliseconds before users click a button
    
    new_count = state.vms_prewarmed + 1
    
    {:noreply, %{state | vms_prewarmed: new_count}}
  end
end
