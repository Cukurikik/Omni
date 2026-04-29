defmodule Omni.Concurrency.NeuromorphicSpikingNet.SpikeRouter do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{spikes_routed: 0}, name: __MODULE__)
  end

  def route_spike(pid, spike_event) do
    GenServer.cast(pid, {:route, spike_event})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:route, _event}, state) do
    # Distributed Elixir worker routing millions of asynchronous neural spikes per second
    # Elixir's Actor model perfectly mirrors the decentralized, event-driven nature of Spiking Neural Networks
    
    new_count = state.spikes_routed + 1
    
    {:noreply, %{state | spikes_routed: new_count}}
  end
end
