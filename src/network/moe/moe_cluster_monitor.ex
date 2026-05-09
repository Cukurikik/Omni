# moe_cluster_monitor.ex — Network / Management
# Layer: Network / Elixir — MoE Global Supervisor
#
# OTP Application that monitors the health and topology of the entire
# MoE cluster. Integrates with the fault detector and routing engine.

defmodule Omni.MoE.ClusterMonitor do
  use GenServer
  require Logger

  @refresh_interval 5_000 # 5 seconds

  # --- API ---

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  def get_cluster_state() do
    GenServer.call(__MODULE__, :get_state)
  end

  def report_expert_health(node_id, expert_id, status) do
    GenServer.cast(__MODULE__, {:update_health, node_id, expert_id, status})
  end

  # --- Callbacks ---

  @impl true
  def init(_opts) do
    Logger.info("[MoE Cluster Monitor] Starting up...")
    
    # State holds node statuses and expert mappings
    state = %{
      nodes: %{},
      experts: %{},
      last_refresh: :os.system_time(:millisecond)
    }

    schedule_refresh()
    {:ok, state}
  end

  @impl true
  def handle_call(:get_state, _from, state) do
    {:reply, state, state}
  end

  @impl true
  def handle_cast({:update_health, node_id, expert_id, status}, state) do
    timestamp = :os.system_time(:millisecond)
    
    nodes = Map.update(state.nodes, node_id, %{last_seen: timestamp, experts: [expert_id]}, fn node ->
      %{node | last_seen: timestamp, experts: Enum.uniq([expert_id | node.experts])}
    end)

    experts = Map.put(state.experts, expert_id, %{node: node_id, status: status, updated_at: timestamp})

    {:noreply, %{state | nodes: nodes, experts: experts}}
  end

  @impl true
  def handle_info(:refresh_cluster, state) do
    now = :os.system_time(:millisecond)
    timeout_threshold = 15_000 # 15 seconds

    # Check for dead nodes
    {alive_nodes, dead_nodes} = Enum.split_with(state.nodes, fn {_id, node_info} -> 
      (now - node_info.last_seen) < timeout_threshold
    end)

    if length(dead_nodes) > 0 do
      Logger.warning("[MoE Cluster Monitor] Detected dead nodes: #{inspect(dead_nodes)}")
      # Trigger fault detector / reallocation logic here
    end

    state = %{state | nodes: Map.new(alive_nodes)}
    schedule_refresh()

    {:noreply, state}
  end

  # --- Internal ---

  defp schedule_refresh() do
    Process.send_after(self(), :refresh_cluster, @refresh_interval)
  end
end
