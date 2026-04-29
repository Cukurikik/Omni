defmodule Omni.Concurrency.CloudCostOptimizer.SpendAggregator do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{events_processed: 0}, name: __MODULE__)
  end

  def ingest_billing_event(pid, cost_event) do
    GenServer.cast(pid, {:ingest, cost_event})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:ingest, _event}, state) do
    # Distributed Elixir worker aggregating millions of micro-billing events (e.g. per-GB egress, per-Lambda execution)
    # in real-time across a multi-cloud architecture.
    
    new_count = state.events_processed + 1
    
    {:noreply, %{state | events_processed: new_count}}
  end
end
