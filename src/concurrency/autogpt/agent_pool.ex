defmodule Omni.AutoGPT.AgentPool do
  @moduledoc """
  OMNI AUTOGPT: Autonomous Agent Supervision Pool
  OTP Supervisor managing the lifecycle and fault tolerance of multiple autonomous agents.
  Source: Significant-Gravitas/AutoGPT
  """
  use DynamicSupervisor
  require Logger

  def start_link(_arg) do
    DynamicSupervisor.start_link(__MODULE__, :ok, name: __MODULE__)
  end

  @impl true
  def init(:ok) do
    # max_children restricts the number of active AutoGPT instances
    DynamicSupervisor.init(strategy: :one_for_one, max_children: 100)
  end

  @doc """
  Spawns a new Autonomous Agent process into the supervision tree.
  """
  def spawn_agent(agent_id, initial_goal) do
    # In a real system, this points to an Omni.AutoGPT.AgentWorker GenServer
    child_spec = %{
      id: agent_id,
      start: {Omni.AutoGPT.AgentWorker, :start_link, [agent_id, initial_goal]},
      restart: :transient # Do not restart if it completes naturally, restart if crash
    }

    case DynamicSupervisor.start_child(__MODULE__, child_spec) do
      {:ok, pid} -> 
        Logger.info("Spawned AutoGPT Agent: #{agent_id} at PID: #{inspect(pid)}")
        {:ok, pid}
      {:error, reason} -> 
        Logger.error("Failed to spawn agent #{agent_id}: #{inspect(reason)}")
        {:error, reason}
    end
  end
  
  @doc """
  Terminates a runaway agent.
  """
  def terminate_agent(pid) do
     DynamicSupervisor.terminate_child(__MODULE__, pid)
  end
end

# Dummy Worker for structural completeness
defmodule Omni.AutoGPT.AgentWorker do
  use GenServer
  
  def start_link(agent_id, goal) do
    GenServer.start_link(__MODULE__, %{id: agent_id, goal: goal})
  end
  
  @impl true
  def init(state) do
    {:ok, state}
  end
end
