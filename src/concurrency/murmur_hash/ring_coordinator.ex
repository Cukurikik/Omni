defmodule Omni.Concurrency.MurmurHash.RingCoordinator do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{nodes: %{}}, name: __MODULE__)
  end

  def add_node(pid, node_id, vnodes) do
    GenServer.cast(pid, {:add, node_id, vnodes})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:add, node_id, vnodes}, state) do
    # Distributed coordination of consistent hash ring
    # IO.puts("Hash Ring: Registered node #{node_id} with #{vnodes} virtual nodes")
    
    new_nodes = Map.put(state.nodes, node_id, vnodes)
    {:noreply, %{state | nodes: new_nodes}}
  end
end
