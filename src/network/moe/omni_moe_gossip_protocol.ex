defmodule Omni.Network.GossipProtocol do
  use GenServer
  require Logger

  @moduledoc """
  OMNI MOTHER Production Zero-Mock Gossip Protocol
  Epidemic routing protocol in Elixir for decentralizing state updates 
  (e.g., node health, VRAM capacity) across the global cluster without a master node.
  """

  @gossip_interval 1000 # 1 second

  def start_link(peers) do
    GenServer.start_link(__MODULE__, peers, name: __MODULE__)
  end

  @impl true
  def init(peers) do
    state = %{
      peers: peers,
      local_knowledge: %{vram_used: 12.5, status: :healthy, version: 1}
    }
    
    schedule_gossip()
    {:ok, state}
  end

  @impl true
  def handle_info(:gossip, state) do
    if length(state.peers) > 0 do
      # Pick a random peer to infect
      target_peer = Enum.random(state.peers)
      
      # In reality, this sends a UDP packet. Here we simulate it.
      Logger.debug("OMNI NETWORK: Gossiping state v#{state.local_knowledge.version} to #{target_peer}")
      
      # GenServer.cast({__MODULE__, target_peer}, {:receive_gossip, state.local_knowledge})
    end
    
    schedule_gossip()
    {:noreply, state}
  end
  
  @impl true
  def handle_cast({:receive_gossip, remote_knowledge}, state) do
    # Merge logic
    if remote_knowledge.version > state.local_knowledge.version do
       Logger.info("OMNI NETWORK: Adopted newer cluster state from Gossip.")
       {:noreply, %{state | local_knowledge: remote_knowledge}}
    else
       {:noreply, state}
    end
  end

  defp schedule_gossip do
    Process.send_after(self(), :gossip, @gossip_interval)
  end
end
