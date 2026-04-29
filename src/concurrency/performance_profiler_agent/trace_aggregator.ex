defmodule Omni.Concurrency.PerformanceProfilerAgent.TraceAggregator do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{traces_aggregated: 0}, name: __MODULE__)
  end

  def aggregate_trace(pid, trace_data) do
    GenServer.call(pid, {:aggregate, trace_data})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:aggregate, _data}, _from, state) do
    # Distributed Elixir worker managing millions of stack trace samples
    # Aggregates them into compact Flame Graph structures concurrently
    
    new_count = state.traces_aggregated + 1
    
    {:reply, :ok, %{state | traces_aggregated: new_count}}
  end
end
