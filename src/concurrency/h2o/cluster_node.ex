defmodule Omni.H2O.ClusterNode do
  use GenServer

  def start_link(node_name) do
    GenServer.start_link(__MODULE__, node_name, name: node_name)
  end

  def init(name) do
    {:ok, %{name: name, peers: [], data_chunks: 0}}
  end

  def handle_cast({:add_peer, peer_pid}, state) do
    {:noreply, %{state | peers: [peer_pid | state.peers]}}
  end

  def handle_call({:distribute_data, chunk_size}, _from, state) do
    # Simulate distributed memory allocation
    new_state = %{state | data_chunks: state.data_chunks + chunk_size}
    {:reply, :ok, new_state}
  end
end
