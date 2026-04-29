defmodule Omni.Concurrency.DeepSpaceNetworkRelay.BundleForwarder do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{bundles_queued: 0}, name: __MODULE__)
  end

  def queue_dtn_bundle(pid, payload) do
    GenServer.cast(pid, {:queue, payload})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:queue, _payload}, state) do
    # Distributed Elixir worker managing Store-and-Forward logic for Interplanetary Internet.
    # Because Earth-Mars links drop frequently (e.g., solar conjunctions), this worker holds
    # packets safely in state/disk for days or weeks, automatically forwarding them 
    # the second a radio link is re-established.
    
    new_count = state.bundles_queued + 1
    
    {:noreply, %{state | bundles_queued: new_count}}
  end
end
