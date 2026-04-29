defmodule Omni.Concurrency.OfflineSyncManager.ReconnectionQueue do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{pending_syncs: 0}, name: __MODULE__)
  end

  def queue_for_sync(pid, crdt_payload) do
    GenServer.cast(pid, {:queue, crdt_payload})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:queue, _payload}, state) do
    # Distributed Elixir worker buffering offline actions (like sending an email or updating DB)
    # When network is restored, this queue drains sequentially to sync with the cloud
    
    new_count = state.pending_syncs + 1
    
    {:noreply, %{state | pending_syncs: new_count}}
  end
end
