defmodule Dust.AgentOrchestrator do
  @moduledoc """
  Dust AI Agent Platform — Multi-agent coordinator via Elixir actors.
  Manages agent fleet with strict process and memory limits.
  """
  use GenServer

  @max_agents 5000
  @max_tools_per_agent 50

  defstruct [:agents, :tool_registry]

  def start_link(_) do
    GenServer.start_link(__MODULE__, %__MODULE__{agents: %{}, tool_registry: %{}}, name: __MODULE__)
  end

  def spawn_agent(agent_id, config) do
    GenServer.call(__MODULE__, {:spawn, agent_id, config})
  end

  def dispatch_task(agent_id, task) do
    GenServer.call(__MODULE__, {:dispatch, agent_id, task})
  end

  @impl true
  def init(state), do: {:ok, state}

  @impl true
  def handle_call({:spawn, agent_id, config}, _from, state) do
    if map_size(state.agents) >= @max_agents do
      {:reply, {:error, "Agent fleet capacity exhausted"}, state}
    else
      if length(Map.get(config, :tools, [])) > @max_tools_per_agent do
        {:reply, {:error, "Tools per agent exceeds limit"}, state}
      else
        pid = spawn(fn -> agent_loop(agent_id, config) end)
        new_state = %{state | agents: Map.put(state.agents, agent_id, %{pid: pid, config: config})}
        {:reply, {:ok, agent_id}, new_state}
      end
    end
  end

  @impl true
  def handle_call({:dispatch, agent_id, task}, _from, state) do
    case Map.get(state.agents, agent_id) do
      nil -> {:reply, {:error, "Agent not found"}, state}
      %{pid: pid} ->
        send(pid, {:task, task})
        {:reply, {:ok, :dispatched}, state}
    end
  end

  defp agent_loop(agent_id, _config) do
    receive do
      {:task, _payload} -> agent_loop(agent_id, _config)
      :terminate -> :ok
    end
  end
end
