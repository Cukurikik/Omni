defmodule Omni.Concurrency.GossipProtocol.InfectionState do
  use GenServer

  def start_link(node_id) do
    GenServer.start_link(__MODULE__, %{id: node_id, infected: false, state_version: 0}, name: String.to_atom("gossip_#{node_id}"))
  end

  def receive_gossip(pid, peer_version) do
    GenServer.cast(pid, {:gossip, peer_version})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:gossip, peer_version}, state) do
    if peer_version > state.state_version do
      # Node is "infected" with newer state
      # IO.puts("Gossip Node #{state.id}: Infected with state V#{peer_version}")
      {:noreply, %{state | infected: true, state_version: peer_version}}
    else
      {:noreply, state}
    end
  end
end
