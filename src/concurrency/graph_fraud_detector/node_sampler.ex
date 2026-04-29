defmodule Omni.Concurrency.GraphFraudDetector.NodeSampler do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  def sample_neighborhood(pid, node_id, depth) do
    GenServer.call(pid, {:sample, node_id, depth})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:sample, node_id, depth}, _from, state) do
    # GraphSAGE / Neighborhood sampling logic
    # In massive graphs, we sample fixed-size neighborhoods to prevent memory explosion
    
    # Simulate return of a neighborhood subgraph tensor structure
    result = {:ok, %{center: node_id, edges_sampled: depth * 10}}
    
    {:reply, result, state}
  end
end
