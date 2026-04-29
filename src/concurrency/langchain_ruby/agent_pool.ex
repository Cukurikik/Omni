defmodule Omni.Concurrency.LangchainRuby.AgentPool do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{active_agents: %{}, max_agents: 100}, name: __MODULE__)
  end

  def dispatch_task(pid, agent_id, task) do
    GenServer.call(pid, {:dispatch, agent_id, task})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:dispatch, agent_id, task}, _from, state) do
    current_count = map_size(state.active_agents)

    if Map.has_key?(state.active_agents, agent_id) do
      # Agent busy logic
      {:reply, {:error, "Agent already processing a task"}, state}
    else
      if current_count >= state.max_agents do
        {:reply, {:error, "Agent pool exhausted"}, state}
      else
        new_agents = Map.put(state.active_agents, agent_id, %{task: task, status: :running})
        {:reply, {:ok, "Task dispatched to #{agent_id}"}, %{state | active_agents: new_agents}}
      end
    end
  end
end
