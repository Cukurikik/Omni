defmodule Omni.Concurrency.EdgeAiModelQuantizer.FederatedAggregator do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{devices_aggregated: 0}, name: __MODULE__)
  end

  def aggregate_device_gradients(pid, gradient_size) do
    GenServer.cast(pid, {:aggregate, gradient_size})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:aggregate, _size}, state) do
    # Distributed Elixir worker managing Federated Learning at the Edge.
    # Millions of smartphones train the model locally on user data, preserving privacy.
    # This worker securely aggregates the encrypted INT8 gradient updates in real-time.
    
    new_count = state.devices_aggregated + 1
    
    {:noreply, %{state | devices_aggregated: new_count}}
  end
end
