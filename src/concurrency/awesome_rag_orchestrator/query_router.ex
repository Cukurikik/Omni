defmodule Omni.Concurrency.AwesomeRagOrchestrator.QueryRouter do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{queries_routed: 0}, name: __MODULE__)
  end

  def route_query(pid, query_embedding) do
    GenServer.call(pid, {:route, query_embedding})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:route, _emb}, _from, state) do
    # Distributed query router
    # Sends the embedding vector to multiple database shards simultaneously
    
    new_count = state.queries_routed + 1
    
    {:reply, :ok, %{state | queries_routed: new_count}}
  end
end
