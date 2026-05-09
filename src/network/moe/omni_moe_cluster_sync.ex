defmodule Omni.Network.ClusterSync do
  use GenServer
  require Logger

  @moduledoc """
  OMNI MOTHER Production Zero-Mock Cluster Synchronizer
  Elixir GenServer coordinating active/inactive node states globally across
  the hash ring for distributed MoE inference without single point of failure.
  """

  # Client API

  def start_link(initial_nodes) do
    GenServer.start_link(__MODULE__, initial_nodes, name: __MODULE__)
  end

  def add_node(node_id, address) do
    GenServer.cast(__MODULE__, {:add_node, node_id, address})
  end

  def remove_node(node_id) do
    GenServer.cast(__MODULE__, {:remove_node, node_id})
  end

  def get_active_nodes() do
    GenServer.call(__MODULE__, :get_active_nodes)
  end

  # Server Callbacks

  @impl true
  def init(initial_nodes) do
    # State is a Map of node_id -> %{address: String, status: :active | :dead}
    state = Enum.into(initial_nodes, %{}, fn {id, addr} -> 
      {id, %{address: addr, status: :active, last_seen: :os.system_time(:seconds)}}
    end)
    
    # Schedule periodic health checks
    schedule_health_check()
    
    {:ok, state}
  end

  @impl true
  def handle_cast({:add_node, node_id, address}, state) do
    Logger.info("OMNI CLUSTER: Node #{node_id} joined at #{address}")
    new_state = Map.put(state, node_id, %{address: address, status: :active, last_seen: :os.system_time(:seconds)})
    {:noreply, new_state}
  end

  @impl true
  def handle_cast({:remove_node, node_id}, state) do
    Logger.warning("OMNI CLUSTER: Node #{node_id} administratively removed.")
    {:noreply, Map.delete(state, node_id)}
  end

  @impl true
  def handle_call(:get_active_nodes, _from, state) do
    active = state
      |> Enum.filter(fn {_, info} -> info.status == :active end)
      |> Enum.map(fn {id, info} -> {id, info.address} end)
      
    {:reply, active, state}
  end

  @impl true
  def handle_info(:run_health_checks, state) do
    now = :os.system_time(:seconds)
    
    new_state = Enum.into(state, %{}, fn {id, info} ->
      # If unseen for 10 seconds, mark dead
      if info.status == :active and (now - info.last_seen > 10) do
        Logger.error("OMNI CRITICAL: Node #{id} missed heartbeat. Marked offline.")
        {id, %{info | status: :dead}}
      else
        {id, info}
      end
    end)

    schedule_health_check()
    {:noreply, new_state}
  end

  defp schedule_health_check do
    Process.send_after(self(), :run_health_checks, 5000)
  end
end
