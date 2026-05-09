# moe_kb_tricks_agent_sync.ex — Network
# Layer: Network — KB Tricks Agent Synchronization
# Inspired by: kb-tricks (Agent-native AI skill suite, sync protocols)

defmodule Omni.Network.KBTricksSync do
  use GenServer
  require Logger

  @doc """
  Maintains distributed state sync across agent-native Knowledge Base workers.
  Ensures that when an agent updates a KB, all other agents invalidate their cache.
  """

  def start_link(opts) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  def init(_opts) do
    Logger.info("[KB Tricks] Agent Sync Node Initialized")
    # Join Erlang distributed group
    :pg.join(:kb_agents, self())
    {:ok, %{active_agents: 0, last_update: :os.system_time(:millisecond)}}
  end

  def handle_cast({:kb_updated, kb_id, agent_id}, state) do
    Logger.info("KB #{kb_id} updated by Agent #{agent_id}. Broadcasting invalidation.")
    
    # Broadcast to all agents in the process group
    members = :pg.get_members(:kb_agents)
    Enum.each(members, fn pid -> 
      if pid != self() do
        send(pid, {:invalidate_kb_cache, kb_id})
      end
    end)

    {:noreply, %{state | last_update: :os.system_time(:millisecond)}}
  end

  def handle_info({:invalidate_kb_cache, kb_id}, state) do
    # Zero-Mock: Flush local ETS cache for this KB
    :ets.delete_all_objects(:"kb_cache_#{kb_id}")
    Logger.debug("Local cache invalidated for KB #{kb_id}")
    {:noreply, state}
  end
end
